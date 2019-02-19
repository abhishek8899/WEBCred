from features.surface import getAlexarank
from features.surface import getWot
from sqlalchemy.orm import sessionmaker
from utils.databases import Features
from utils.databases import FeaturesSet
from utils.databases import Genre_labels
from utils.databases import Manual_labels
from utils.databases import Ranks
from utils.databases import Scores
from utils.essentials import apiList
from utils.essentials import Correlation
from utils.essentials import Database
from utils.essentials import db
from utils.essentials import merge_two_dicts
from utils.essentials import weights
from utils.webcred import webcred_score

import json
import logging
import sys
import traceback

logger = logging.getLogger('similarity_score')
logging.basicConfig(
    filename='log/logging.log',
    filemode='a',
    format='[%(asctime)s] {%(name)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO
)

Session = sessionmaker()
Session.configure(bind=db.engine)
session = Session()

genre = Database(Genre_labels)
manual_labels = Database(Manual_labels)

scores = Database(Scores)
features = Database(Features)


def goodurls():

    # get instances when none of the entry in invalid
    query = session.query(Ranks, Features).filter(
        Features.url == Genre_labels.url
    ).filter(Ranks.error == None).filter(Features.error == None).filter(
        Features.domain != None
    ).filter(Features.brokenlinks != None).filter(
        Features.langcount != None
    ).filter(Features.ads != None).filter(Features.imgratio != None).filter(
        Features.inlinks != None
    ).filter(Features.misspelled != None).filter(
        Features.pageloadtime != None
    ).filter(Features.responsive != None
             ).filter(Features.hyperlinks != None).filter(
                 Features.lastmod != None
             ).filter(Features.outlinks != None
                      ).filter(Ranks.wot != None
                               ).filter(Ranks.wot_confidence != None
                                        ).filter(Ranks.wot_reputation != None
                                                 ).filter(
                                                     Ranks.alexa != None
                                                 )  # noqa
    return query


def prepareDataset():

    # qu = ''
    # for key in apiList.keys():
    #     qu += '.filter(Features.' + key + ' != None)'
    #
    # qu += '.filter(Ranks.wot != None)'
    # qu += '.filter(Ranks.wot_confidence != None)'
    # qu += '.filter(Ranks.wot_reputation != None)'
    # qu += '.filter(Ranks.alexa != None)'

    query = goodurls()
    query.count()
    features_name = apiList.keys()

    features = Database(Features)
    ranks = Database(Ranks)
    features_set = Database(FeaturesSet)

    # append columns form Ranks class
    for i in ranks.getcolumns():
        features_name.append(i)

    # remove redundant columns
    features_name.remove('cookie')
    features_name.remove('site')
    features_name.remove('domain')
    features_name.remove('hyperlinks')
    features_name.remove('responsive')
    features_name.remove('id')
    features_name.remove('error')
    features_name.remove('redirected')

    for i in query.all():
        url = i[0]
        temp = merge_two_dicts(
            features.getdata('url', str(url)), ranks.getdata('url', str(url))
        )
        dt = {}
        for j in features_name:
            dt[j] = temp.get(j)

        dbData = {'url': str(url), 'dataset': json.dumps(dt)}

        features_set.update('url', str(url), dbData)

    logger.info('Prepared table {}'.format(features_set.gettablename()))

    return True


def getsimilarity():
    # get data from Class FeaturesSet
    database = Database(FeaturesSet)
    temp = database.getcolumndata('dataset')
    # clean data in list format
    features_name = json.loads(temp.all()[0][0]).keys()
    features_name.remove('url')
    corr = Correlation()
    for j in range(1, 6):
        dump = temp.all()[:(50 * j)]
        data = []
        for i in dump:
            joker = json.loads(i[0])
            joker['alexa'] = float(1.0 / joker['alexa'])
            del joker['url']
            values = joker.values()
            data.append(values)

        print(corr.getcorr(data, features_name))
        print()


def getsimilarity_Score():
    # get data from Class FeaturesSet
    database = Database(FeaturesSet)
    temp = database.getcolumndata('dataset')
    # clean data in list format
    features_name = json.loads(temp.all()[0][0]).keys()
    features_name = [
        'alexa score (1/alexa rank)', 'wot', 'article', 'shop', 'help',
        'others', 'portrayal_individual', 'wot_confidence', 'wot_reputation'
    ]
    corr = Correlation()
    for j in range(1, 6):
        dump = temp.all()[:(50 * j)]
        data = []
        for i in dump:
            joker = json.loads(i[0])
            joker['alexa'] = float(1.0 / joker['alexa'])

            # append all values in data
            dataDict = merge_two_dicts(joker, database.getdata('dataset', i))
            values = []
            for k in features_name:
                values.append(dataDict.get(k))

            data.append(values)

        print(corr.getcorr(data, features_name))
        print()


def genre_feature_urls():
    '''
    get all genre urls which are crawled with no error
    :return:
    '''

    query = session.query(Genre_labels,
                          Features).filter(Features.url == Genre_labels.url
                                           ).filter(Features.error == None)
    return query


# store webcred_score for all genre
def fillallscore():

    # get all URLs with labels
    label_url = {}

    # self labelled url
    query = session.query(Scores, Features).filter(
        Features.url == Scores.url
    ).filter(Scores.which_genre_does_this_web_page_belongs_to != None).all()

    for rows in query:
        url = str(rows[0])
        label = scores.getdata('url', url
                               )['which_genre_does_this_web_page_belongs_to']
        if label:
            label_url[url] = label

    # crowdsource labelled url
    query = session.query(Genre_labels, Features).filter(
        Features.url == Genre_labels.url
    ).filter(Genre_labels.confidence >= 1).all()

    for rows in query:
        url = str(rows[0])
        if not label_url.get(url):
            rows = genre.getdata('url', url)
            label_url[url] = rows['which_genre_does_this_web_page_belongs_to']

    # serc labelled url
    query = session.query(Manual_labels).filter(
        Manual_labels.which_genre_does_this_web_page_belongs_to != None
    ).all()

    for rows in query:
        url = str(rows)
        if not label_url.get(url):
            rows = manual_labels.getdata('url', url)
            if rows.get('which_genre_does_this_web_page_belongs_to'):
                label_url[url] = rows[
                    'which_genre_does_this_web_page_belongs_to']

    for url, label in label_url.items():

        if url in scores.getcolumndata('url') and scores.getdata(
                'url', url).get(['gcs']):
            continue

        data = {}

        # fetch gcs score
        try:

            # prepare percentage dict
            feature_name = weights.get('features')
            percentage = {}

            if not weights['genres'].get(label):
                continue

            for index, elem in enumerate(
                    weights['genres'][label].get('weights')):
                percentage[feature_name[index] + 'Perc'] = elem

            dbdata = features.getdata('url', url)

            # get score
            if not dbdata.get('error'):
                data['gcs'] = webcred_score(dbdata,
                                            percentage)["webcred_score"]

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

            logger.info(ex_value)
            logger.debug(stack_trace)

        # fetch wot score
        try:
            web_of_trust = getWot(url)

            data['wot_confidence'] = web_of_trust['confidence']
            data['wot_reputation'] = web_of_trust['reputation']
            data['wot'] = (
                data['wot_reputation'] * data['wot_confidence'] / 10000.0
            )

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

            logger.info(ex_value)
            logger.debug(stack_trace)

        # fetch alexa rank
        try:

            data['alexa'] = getAlexarank(url)

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

            logger.info(ex_value)
            logger.debug(stack_trace)

        scores.update('url', url, data)


def fillsecuritygroup():
    '''
    assign securtiy group to scores table
    :return:
    '''

    # scores = Database(Scores)
    # feature = Database(Features)
    # security_groups = Database(Security_Groups)
    # import pdb
    # pdb.set_trace()
    #
    # query = session.query(Security_Groups, Features).filter(
    #     Features.url == Security_Groups.url
    # )
    #
    # for url in scores.getcolumndata('url'):
    #     url = str(url[0])
    #     if security_groups.exist('url', url):
    #
    #         data = {}
    #         data['url'] = url
    #         data['group'] = security_groups.getdata('url', url)['groups']
    #         scores.update('url', url, data)


if __name__ == "__main__":

    while True:
        print(
            '''
            p = prepareDataset
            s = similarity_score between features Vs wot & alexa
            sw = similarity_score between webcred_score and wot & alexa
            w = calculate all scores>> wot, alexa, webcred
            g = add security group details to rank table
            q = quit
        '''
        )

        action = raw_input("what action would you like to perform: ")

        if action == 'p':
            prepareDataset()
        elif action == 's':
            getsimilarity()
        elif action == 'w':
            fillallscore()
        elif action == 'sw':
            getsimilarity_Score()
        elif action == 'g':
            fillsecuritygroup()
        elif action == 'q':
            print('babaye')
            break
