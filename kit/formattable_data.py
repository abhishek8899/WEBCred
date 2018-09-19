# this program, tones data into desired format.
'''
- remove datasets which have error
- remove redundant columns
- Convert dictionary keys into features
- include genre column
'''

from utils.databases import Features
from utils.databases import Genre_labels
from utils.essentials import Database

import csv
import json
import os
import pdb
import pickle
import sys


reload(sys)
# python2 has default ascii encoding
sys.setdefaultencoding('utf-8')

filename = 'data/dump/webcred_features/webcred_public_features.csv'
features_norm_dump = 'data/dump/webcred_features/features_norm.p'
url_norm_dump = 'data/dump/webcred_features/url_norm.p'
final_csv = 'data/dump/webcred_features.csv'
figure_eight_label = 'data/essentials/figure_eight_labelled.txt'
genre_label = 'data/Genre_Labels/dump/figure-eight/' \
              'cf_report_1297959_aggregated.csv'
norm_keys = ['genre', 'domain', 'doc_type', 'responsive']
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
    # 'pos'
]

label_confidence = 0.2
genre_data = {}
csv_headers = []
csv_data = []
features_norm_dict = {}

# remove old csv file
try:
    os.remove(final_csv)
except OSError:
    pass

# load pickle
try:
    features_norm_dict = pickle.load(open(features_norm_dump, 'rb'))
except IOError:
    pass

count = 0

'get genre labels into a dict corresponding to url'
database = Database(Genre_labels)
data = database.getdbdata()

pdb.set_trace()

'get features data into a dict corresponding to url'
database = Database(Features)

# prepared redundant key set
redundant_keys += [
    key for key in data[0].keys()
    if key.endswith('norm') or key.endswith('Norm')
]
redundant_keys = set(redundant_keys)

for rows in data:
    if float(rows['confidence']) > label_confidence:
        genre = rows['which_genre_does_this_web_page_belongs_to']

        'make desired csv'

        rows = database.getdata('url', rows['url'])

        if not rows:
            continue

        rows['genre'] = genre

        for key in rows.keys():

            # delete redundant keys
            if key in redundant_keys:
                del rows[key]
                continue

            # convert dict to list
            # FIXME handle 'null'
            # if isinstance(rows[key], dict):
            #     # rows[key] = json.loads(rows[key])
            #     for k, v in rows[key].items():
            #         pretty_key = key + '_' + k
            #         rows[pretty_key] = v
            #     del rows[key]

            # normalize values
            # if rows[key] and (isinstance(rows[key], str)
            #                   or isinstance(rows[key], bool)):
            #     rows[key] = str(rows[key]).lower()
            #     if key not in features_norm_dict.keys():
            #         features_norm_dict[key] = []
            #
            #     if rows[key] not in features_norm_dict[key]:
            #         features_norm_dict[key].append(rows[key])
            #
            #     rows[key] = features_norm_dict[key].index(rows[key])

        # get csvfileheaders
        csv_headers += rows.keys()

        # write row to csv
        csv_data.append(json.dumps(rows))

with open(final_csv, 'a') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=list(set(csv_headers)))
    print('writing headers')
    writer.writeheader()
    print('writing rows')
    for rows in csv_data:
        rows = json.loads(rows)
        writer.writerow(rows)

print('dumping pickle {}'.format(features_norm_dict))
pickle.dump(features_norm_dict, open(features_norm_dump, 'wb'))
print(count)
print('A job well done!!')
