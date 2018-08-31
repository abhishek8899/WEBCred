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
import sys
import traceback


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

        if not isinstance(self.request, dict):
            self.request = dict(self.request.args)

        data = {}
        req = {}
        req['args'] = {}
        percentage = {}
        site = None
        try:
            # get percentage of each feature
            # and copy self.request to req['args']
            # TODO come back and do this properly
            for keys in apiList.keys():
                if self.request.get(keys, None):
                    # because self.request.args is of ImmutableMultiDict form
                    if isinstance(self.request.get(keys, None), list):
                        req['args'][keys] = str(self.request.get(keys)[0])
                        perc = keys + "Perc"
                        if self.request.get(perc):
                            percentage[keys] = self.request.get(perc)[0]
                    else:
                        req['args'][keys] = self.request.get(keys)
                        perc = keys + "Perc"
                        if self.request.get(perc):
                            percentage[keys] = self.request.get(perc)

            # to show wot ranking
            # req['args']['wot'] = "true"
            data['url'] = req['args']['site']

            site = Urlattributes(url=req['args'].get('site', None))

            # get genre
            # WARNING there can be some issue with it
            data['genre'] = self.request.get('genre', None)

            if data['url'] != site.geturl():
                data['redirected'] = site.geturl()

            data['lastmod'] = site.getlastmod()

            # site is not a WEBCred parameter
            del req['args']['site']

            data, existing_features = check_data_existence(self.db, data)

            data = extract_value(
                req['args'], apiList, data, site, existing_features
            )

            # HACK 13 is calculated number, refer to index.html, where new
            # dimensions are dynamically added
            # create percentage dictionary
            number = 13
            # TODO come back and do this properly
            while True:
                dim = "dimension" + str(number)
                api = "api" + str(number)
                if dim in self.request.keys():
                    try:
                        data[self.request.get(dim)[0]] = surface.dimapi(  # noqa
                            site.geturl(),
                            self.request.get(api)[0]
                        )
                        perc = api + "Perc"
                        percentage[dim] = self.request.get(perc)[0]
                    except WebcredError as e:
                        data[self.request.get(dim)[0]] = e.message
                    except Exception:
                        data[self.request.get(dim)[0]] = "Fatal ERROR"
                else:
                    break
                number += 1

            data = webcred_score(data, percentage)

            data['error'] = None

        except WebcredError as e:
            data['error'] = e.message
        except Exception:

            error = WebcredError()
            error.traceerror(log='info')

            # HACK if it's not webcred error,
            #  then probably it's python error
            data['error'] = 'Fatal Error'
        finally:
            # always return the final assess time.
            now = str((datetime.now() - now).total_seconds())
            data['assess_time'] = now

            # store it in data
            self.db.update('url', data['url'], data)

            logger.debug(data['url'])

            logger.debug('Time = {}'.format(now))

            return data


def check_data_existence(db, data):
    '''
    :param db: database instance
    :param data: data which is to be modified
    :return: data from db and list of existing_features in db
    '''

    existing_features = []

    # if url is already present?
    if db.filter('url', data['url']).count():
        '''
        if lastmod not changed
            update only the columns with None value
        else update every column
        '''
        if db.filter('lastmod',
                     data['lastmod']).count() or not data['lastmod']:

            # get all existing data in dict format
            data = db.getdata('url', data['url'])

            # check the ones from columns which have non None value
            '''
            None value indicates that feature has not
            successfully extracted yet
            '''

            # webcred always assess loadtime
            existing_features = [
                k for k, v in data.items()
                if v or str(v) == str(0) and k != 'pageloadtime'
            ]

        else:
            data = db.getdata('url', data['url'])

    return data, existing_features


def extract_value(req, apiList, data, url, existing_features):
    '''
    :param req: list of required feature value
    :param apiList: list of features and their unit features
    :param data: data instance
    :param url: Urlattributes instance
    :param existing_features: list of existing_features in db
    :return: values of all features which are yet not extracted
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
        self.data = {'url': request.get('site')}
        # get list of features to be evaluated along with
        # their function and args
        self.features = merge_two_dicts(apiList, genreList)
        try:
            self.url = Urlattributes(self.data['url'])
        except Exception:
            error = WebcredError()
            error.traceerror()
            self.data['error'] = 'Fatal Error'

    def storedata(self):
        pass

    def getGenre(self):
        pass

    def getdata(self):
        pass

    def extractfeatures(self):
        pass

    def geturl(self):
        return self.data['url']


# esp. are we removing any outliers?
def webcred_score(data, percentage):
    # percentage is dict
    # score varies from -1 to 1
    score = 0
    # take all keys of data into account

    for k, v in data.items():

        try:
            if k in normalizeCategory['3'].keys() and k in percentage.keys():
                name = k + "norm"
                data[name] = normalizedData[k].getnormalizedScore(v)
                score += data[name] * float(percentage[k])

            if k in normalizeCategory['2'].keys() and k in percentage.keys():
                name = k + "norm"
                data[name] = normalizedData[k].getfactoise(v)
                score += data[name] * float(percentage[k])

            if k in normalizeCategory['misc'
                                      ].keys() and k in percentage.keys():
                sum_hyperlinks_attributes = 0
                try:
                    for key, value in v.items():
                        sum_hyperlinks_attributes += value
                    name = k + "norm"
                    data[name] = normalizedData[k].getnormalizedScore(
                        sum_hyperlinks_attributes
                    )
                    score += data[name] * float(percentage[k])
                except:
                    logger.info('Issue with misc normalizing categories')
        except Exception:
            # Get current system exception
            ex_type, ex_value, ex_traceback = sys.exc_info()

            # Extract unformatter stack traces as tuples
            trace_back = traceback.extract_tb(ex_traceback)

            # Format stacktrace
            stack_trace = list()

            for trace in trace_back:
                stack_trace.append(
                    "File : %s , Line : %d, Func.Name : %s, Message : %s" %
                    (trace[0], trace[1], trace[2], trace[3])
                )

            # print("Exception type : %s " % ex_type.__name__)
            logger.info(ex_value)
            logger.debug(stack_trace)

    data["webcred_score"] = score / 100

    # TODO add Weightage score for new dimensions
    return data
