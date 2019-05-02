# this program, build data into desired format.
'''
- remove datasets which have error
- remove redundant columns
- Convert dictionary keys into features
- include genre column
'''

# from collections import Counter
# mapping = {
#     1: 'help',
#     2: 'article',
#     3: 'discussion',
#     4: 'shop',
#     5: 'public_portrayals_companies_and_institutions',
#     6: 'private_portrayal_personal_homepage',

# }
#

#     8: 'downloads'
# from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import sessionmaker
# from copy import deepcopy as cc
#     7: 'link_collection',
from utils.databases import Health as Genre_labels
from utils.databases import Health_Features as Features
# from utils.databases import Scores
# from utils.databases import Manual_labels
# from utils.databases import Security_Groups
# from utils.essentials import Correlation
from utils.essentials import Database
from utils.essentials import db

import csv
import json
import logging
import os
# import pandas as pd
# import pdb
import pickle
import sys
import traceback


Session = sessionmaker()
Session.configure(bind=db.engine)

session = Session()

logger = logging.getLogger('formattable_data')
logging.basicConfig(
    filename='log/logging.log',
    filemode='a',
    format='[%(asctime)s] {%(name)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO
)

reload(sys)
# python2 has default ascii encoding
sys.setdefaultencoding('utf-8')

# filename = 'data/dump/webcred_features/webcred_public_features.csv'
features_norm_dump = 'data/dump/health/webcred_features/features_norm.p'
# url_norm_dump = 'data/dump/webcred_features/url_norm.p'
final_csv = 'data/dump/health/webcred_features_expanded.csv'
# final_csv = 'data/dump/filtered_label_genre.csv'
# figure_eight_label = 'data/essentials/figure_eight_labelled.txt'
# genre_label = 'data/Genre_Labels/dump/figure-eight/' \
#               'cf_report_1297959_aggregated.csv'
# norm_keys = ['genre', 'domain', 'doc_type', 'responsive']
redundant_keys = [
    'id',
    'cookie',
    'redirected',
    'text',
    'html',
    'site',
    'sentiment',
    'keywords',
    'assess_time',
    'webcred_score',
    'error',
    'url',
    'doc_type',
    # 'pos',
]

label_confidence = 1
genre_data = {}
csv_headers = []
csv_data = []
features_norm_dict = {}

# remove old csv file
try:
    # pass
    os.remove(final_csv)
except OSError:
    pass

# load pickle
try:
    features_norm_dict = pickle.load(open(features_norm_dump, 'rb'))
except IOError:
    pass

"-----------------------------------------------------------------"
# building new csv from SERC-Labelling
# location = 'data/Genre_labels/SERC-labels/Genre Labelling/'
# names = [
#     'Mohit',
#     'Siddharth',
#     'Palash',
#     'Vivek',
#     'Sai Anirudh',
#     'Ali',
# ]
# mapping = {
#     1: 'help',
#     2: 'article',
#     3: 'discussion',
#     4: 'shop',
#     5: 'public_portrayals_companies_and_institutions',
#     6: 'private_portrayal_personal_homepage',
#     7: 'link_collection',
#     8: 'downloads'
# }
#

# for i in names:
#     temp = location + i + '.csv'
#     di = pd.read_csv(temp)
#     df = di.replace({'genre': mapping})
#     df.to_csv(temp)

"-----------------------------------------------------------------"
# checking correctness of SERC-labelling
#
# for i in xrange(11):
#     count = len(
#         session.query(Manual_labels, Genre_labels).filter(
#             Manual_labels.url == Genre_labels.url
#         ).filter(Genre_labels.confidence >= i / 10.0).all()
#     )
#
#     similar = len(
#         session.query(Manual_labels, Genre_labels).filter(
#             Manual_labels.url == Genre_labels.url
#         ).filter(
#             Manual_labels.which_genre_does_this_web_page_belongs_to == Genre_labels. # noqa
#             which_genre_does_this_web_page_belongs_to
#         ).filter(Genre_labels.confidence >= i / 10.0).all()
#     )
#     print i / 10.0, count, similar, str(similar / (count + 0.0) * 100) + '%'
#
# pdb.set_trace()

"-----------------------------------------------------------------"

"-----------------------------------------------------------------"

'get genre labels into a dict corresponding to url'

# scores = Database(Scores)
genre = Database(Genre_labels)
# scores = Database(Scores)
# data = genre.getdbdata()

'get features data into a dict corresponding to url'
features = Database(Features)

print('now iterating over data')

# # get all which_genre_does_this_web_page_belongs_to urls and process them further # noqa
# for rows in scores.getcolumndata('url'):
#     rows = scores.getdata('url', str(rows[0]))
#     if rows.get('which_genre_does_this_web_page_belongs_to'):
#         genre = rows.get('which_genre_does_this_web_page_belongs_to')
#
data = {}

# prepare sets for labelling URLs

# per_url = 1000
# for i in range(0, len(urls), per_url):
#     with open('label/file' + str(i / per_url) + '.csv', 'w') as f:
#         f.write('\n'.join(['urls,genre'] + urls[i:i + per_url]))

"-----------------------------------------------------------------"
# find similarity bw wot, alexa and gcs

# query = session.query(Security_Groups, Scores).filter(
#     Security_Groups.url == Scores.url
# ).filter(Scores.gcs != None).filter(Scores.alexa != None
#                                     ).filter(Scores.wot != None).all()
#
# security_group = Database(Security_Groups)
#
# gg = [security_group.getdata('url', str(i[0]))['group'] for i in query]
# wot = [scores.getdata('url', str(i[0]))['wot'] for i in query]
# alexa = [scores.getdata('url', str(i[0]))['alexa'] for i in query]
# gcs = [scores.getdata('url', str(i[0]))['gcs'] for i in query]
# corr = Correlation()
#
# print 'Spearman & cosine'
# for i in Counter(gg).keys():
#     ta = [alexa[index] for index, elem in enumerate(gg) if elem == i]
#     tw = [wot[index] for index, elem in enumerate(gg) if elem == i]
#     tg = [gcs[index] for index, elem in enumerate(gg) if elem == i]
#
#     # print i
#     #
#
#     print corr.getcorrelation(ta, tw),
#     print ',',
#     print cosine_similarity([ta], [tw])[0][0],
#     print ',',
#     print corr.getcorrelation(ta, tg),
#     print ',',
#     print cosine_similarity([ta], [tg])[0][0],
#     print ',',
#     print corr.getcorrelation(tw, tg),
#     print ',',
#     print cosine_similarity([tw], [tg])[0][0],
#     print ','
#
# print Counter(gg).values()
# print Counter(gg).keys()
# pdb.set_trace()
"------------------------------------------------------------------------"

"------------------------------------------------------------------------"
# print "preparing dataCSV for training models"

# get all URLs with labels

# self labelled URLs
# # query = session.query(Scores, Features).filter(
# #     Features.url == Scores.url
# # ).filter(Features.error == None
# #          ).filter(Scores.which_genre_does_this_web_page_belongs_to != None
# #                   ).all()
#
# for rows in query:
#     url = str(rows[0])
#     label = scores.getdata('url',
#                            url)['which_genre_does_this_web_page_belongs_to']
#     if label:
#         data[url] = label

# crowdsource labelled URLs
query = session.query(Genre_labels, Features).filter(
    Features.url == Genre_labels.url
).filter(Features.error == None).filter(Genre_labels.genre != None
                                        ).all()  # noqa

for rows in query:
    url = str(rows[0])
    if not data.get(url):
        rows = genre.getdata('url', url)
        data[url] = rows['genre']

# serc labelled URLs

# query = session.query(Manual_labels,
#                       Features).filter(Features.url == Manual_labels.url
#                                        ).filter(Features.error == None).all()

# temp = Database(Manual_labels)
# for rows in query:
#     url = str(rows[0])
#     if not data.get(url):
#         rows = temp.getdata('url', url)
#         if rows.get('which_genre_does_this_web_page_belongs_to'):
#             data[url] = rows['which_genre_does_this_web_page_belongs_to']

# building individual csv
# location = 'data/Genre_labels/SERC-labels/Genre Labelling/'
# names = [
#     # 'Mohit',
#     'Siddharth',
#     'Palash',
#     'Vivek',
#     'Sai Anirudh',
#     # 'Ali',
# ]

# baseData = cc(data)
# for i in names:
#     data = cc(baseData)
#     temp = location + i + '.csv'
#     di = pd.read_csv(temp)
#     for url, label in [(elem, di['genre'][index])
#                        for index, elem in enumerate(di['urls'])]:
#         data[url] = label

# pdb.set_trace()

for url, label in data.items():
    # rows = genre.getdata('url', str(rows[0]))
    # # if float(rows['confidence']) >= label_confidence:
    # label = rows['which_genre_does_this_web_page_belongs_to']

    # 'make desired csv'

    if isinstance(label, float) or label in ['broken_link', 'other', '0.0']:
        continue

    try:
        rows = features.getdata('url', url)

        if not rows:
            continue
#
        rows['genre'] = label
        # pdb.set_trace()
        #
        for key in rows.keys():

            # delete redundant keys
            if key in redundant_keys or key.endswith('norm') or key.endswith(
                    'Norm'):
                del rows[key]
                continue

            # normalize values
            if isinstance(rows[key], unicode) or isinstance(rows[key], bool):
                rows[key] = str(rows[key]).lower()
                if key not in features_norm_dict.keys():
                    features_norm_dict[key] = []

                if rows[key] not in features_norm_dict[key]:
                    features_norm_dict[key].append(rows[key])

                rows[key] = features_norm_dict[key].index(rows[key])

            # convert dict to list
            if isinstance(rows[key], dict):
                for k, v in rows[key].items():
                    pretty_key = key + '_' + k
                    rows[pretty_key] = v
                del rows[key]

        # get csvfileheaders
        csv_headers += rows.keys()

        # write row to csv
        csv_data.append(json.dumps(rows))

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

with open(final_csv, 'w') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=list(set(csv_headers)))
    print('writing headers')
    writer.writeheader()
    print('writing rows')
    for rows in csv_data:
        rows = json.loads(rows)
        writer.writerow(rows)

print('dumping pickle {}'.format(features_norm_dict))
pickle.dump(features_norm_dict, open(features_norm_dump, 'wb'))

print('A job well done!!')
"------------------------------------------------------------------------"
