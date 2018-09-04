from datetime import datetime
from features import *  # noqa
from utils.essentials import apiList
from utils.essentials import genreList
from utils.essentials import merge_two_dicts
from utils.essentials import MyThread
from utils.essentials import WebcredError
from utils.urls import normalizeCategory
from utils.urls import normalizedData
from utils.urls import Urlattributes

import logging


logger = logging.getLogger('WEBCred.webcred')
logging.basicConfig(
    filename='log/logging.log',
    filemode='a',
    format='[%(asctime)s] {%(name)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO
)

# map feature to function name
# these keys() are also used to define db columns


class Webcred():
    def __init__(self, db, request):
        self.db = db
        self.request = request

    def assess(self):

        now = datetime.now()

        data = {}

        data['url'] = self.request['site']

        site = Urlattributes(url=self.request.get('site', None))

        # get genre
        # FIXME we may want to store justified genre,
        # which are results from ML
        data['genre'] = self.request.get('genre', None)

        if data['url'] != site.geturl():
            data['redirected'] = site.geturl()

        data['lastmod'] = site.getlastmod()

        data, existing_features = check_data_existence(self.db, data)

        data = extract_value(
            self.request, apiList, data, site, existing_features
        )

        # TODO if dimensions are dynamically added
        # number = len([
        #     keys for keys in self.request.keys() if keys.endswith('Perc')
        # ])
        # while True:
        #     dim = "dimension" + str(number)
        #     api = "api" + str(number)
        #     if dim in self.request.keys():
        #         try:
        #             data[self.request.get(dim)[0]] = surface.dimapi(  # noqa
        #                 site.geturl(),
        #                 self.request.get(api)[0]
        #             )
        #             perc = api + "Perc"
        #             self.request[dim] = self.request.get(perc)[0]
        #         except WebcredError as e:
        #             data[self.request.get(dim)[0]] = e.message
        #         except Exception:
        #             data[self.request.get(dim)[0]] = "Fatal ERROR"
        #     else:
        #         break
        #     number += 1

        # calculate webcred score
        data = webcred_score(data, self.request)

        now = str((datetime.now() - now).total_seconds())
        data['assess_time'] = now

        return data


def check_data_existence(db, data):
    '''
    :param db: database instance
    :param data: data which is to be modified
    :return: all data from db, list of existing_features
    '''

    existing_features = []

    # if url is already present?
    if db.filter('url', data['url']).count():
        '''
        if lastmod not changed
            don't update any column
            # update only the columns with None value
        else update every column
        '''

        # use db data for assessment
        dbdata = db.getdata('url', data['url'])
        lastmod = dbdata.get('lastmod', None)

        if lastmod == data['lastmod'] and data['lastmod']:

            data = dbdata
            # do not assess this url again
            existing_features = data.keys()

            # check the ones from columns which have non None value
            # '''
            # None value indicates that feature has not
            # successfully extracted yet
            # '''

            # webcred always assess loadtime
            # existing_features = [
            #     k for k, v in data.items()
            #     if v or str(v) == str(0) and k != 'pageloadtime'
            # ]

    return data, existing_features


def extract_value(req, apiList, data, url, existing_features):
    '''
    :param req: list of required feature value
    :param apiList: list of features and their unit features
    :param data: dict, which contain existing data values from db
    :param url: Urlattributes instance
    :param existing_features: list of existing_features
    (which are already extracted) in db
    :return: updated data dict with updated values for all features
    '''

    # always dump raw data
    req['text'] = ''
    req['html'] = ''
    threads = []
    for keys in req.keys():
        if keys not in existing_features:
            Method = apiList[keys][0]
            Name = keys
            Url = url
            Args = apiList[keys][1]
            if not Method:
                continue
            func = eval(Method)
            thread = MyThread(func, Name, Url, Args)
            thread.start()
            threads.append(thread)

    # wait to join all threads in order to get all results
    maxTime = 300
    for t in threads:
        t.join(maxTime)
        data[t.getName()] = t.getResult()
        logger.debug('{} = {}'.format(t.getName(), data[t.getName()]))
    return data


class Genre():
    def __init__(self, db, request):

        self.db = db
        self.request = request
        now = datetime.now()
        self.afterSetup()
        self.data['assess_time'] = str((datetime.now() - now).total_seconds())

    def afterSetup(self):

        self.data = {'url': self.request.get('site')}

        # get list of features to be evaluated along with
        # their function and args
        self.features = merge_two_dicts(apiList, genreList)

        self.url = Urlattributes(self.data['url'])

        if self.data['url'] != self.url.geturl():
            self.data['redirected'] = self.url.geturl()

        self.data['lastmod'] = self.url.getlastmod()

        self.getfeaturevalues()

    def assess(self):
        # pass self.data to ML library
        # and get classified genre value
        return self.data

    def getfeaturevalues(self):
        self.data, existing_features = check_data_existence(self.db, self.data)

        self.data = extract_value(
            self.features.copy(), self.features, self.data, self.url,
            existing_features
        )

        return True

    def geturl(self):
        return self.data['url']


# FIXME are we removing any outliers?
def webcred_score(data, request):
    '''

    :param data: extracted data
    :param request: flask request object
    :return: webcred_score value
    '''

    # score varies from -1 to 1
    score = 0

    # take all keys of data into account
    for k, v in data.items():

        try:
            perc = k + 'Perc'
            if k in normalizeCategory['3'].keys() and perc in request.keys():
                name = k + "norm"
                data[name] = normalizedData[k].getnormalizedScore(v)
                score += data[name] * float(request[perc])

            if k in normalizeCategory['2'].keys() and perc in request.keys():
                name = k + "norm"
                data[name] = normalizedData[k].getfactoise(v)
                score += data[name] * float(request[perc])

            if k in normalizeCategory['misc'
                                      ].keys() and perc in request.keys():
                sum_hyperlinks_attributes = 0
                try:
                    for key, value in v.items():
                        sum_hyperlinks_attributes += value
                    name = k + "norm"
                    data[name] = normalizedData[k].getnormalizedScore(
                        sum_hyperlinks_attributes
                    )
                    score += data[name] * float(request[perc])
                except:
                    logger.info('Issue with misc normalizing categories')
        except Exception:
            error = WebcredError()
            error.traceerror()

    data["webcred_score"] = score / 100

    # TODO add Weightage score for new dimensions
    return data
