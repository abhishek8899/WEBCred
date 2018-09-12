# this program, tones data into desired format.
'''
- remove datasets which have error
- remove redundant columns
- Convert dictionary keys into features
- include genre column
'''

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
final_csv = 'data/dump/webcred_features.csv'
genre_label = 'data/Genre_Labels/dump/figure-eight/' \
              'cf_report_1297959_aggregated.csv'
norm_keys = ['genre', 'domain', 'doc_type', 'responsive']
redundant_keys = [
    'id', 'cookie', 'redirected', 'text', 'html', 'site', 'sentiment',
    'keywords', 'assess_time', 'webcred_score', 'error', 'url', 'doc_type'
]

label_confidence = 0.0
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
    # print features_norm_dict
    # import pdb
    # pdb.set_trace()
except IOError:
    pass

'get genre labels into a dict corresponding to url'
with open(genre_label) as csv_file:
    data = csv.DictReader(csv_file)
    all_genres = []
    for rows in data:
        if float(rows['which_genre_does_this_web_page_belongs_to:confidence']
                 ) > label_confidence:
            genre_data[rows['url']] = unicode(
                rows['which_genre_does_this_web_page_belongs_to']
            )
            all_genres.append(
                rows['which_genre_does_this_web_page_belongs_to']
            )

print(list(set(all_genres)))
pdb.set_trace()
count = 0

with open(filename) as csv_file:
    data = csv.DictReader(csv_file)

    data = [row for row in data if not row.get('error')]

    # prepared redundant keyset
    redundant_keys += [
        key for key in data[0].keys()
        if key.endswith('norm') or key.endswith('Norm')
    ]
    redundant_keys = set(redundant_keys)

    for rows in data:

        # add genre label
        # FIXME genre label not getting into csv
        if genre_data.get(rows['url']):
            count += 1
            rows['genre'] = unicode(genre_data.get(rows['url']))

        for key in rows.keys():

            # delete redundant keys
            if key in redundant_keys:
                del rows[key]
                continue

            # convert dict to list
            # FIXME handle 'null'
            # if '{' in rows[key]:
            #     rows[key] = json.loads(rows[key])
            #     for k, v in rows[key].items():
            #         pretty_key = key + '_' + k
            #         rows[pretty_key] = v
            #     del rows[key]

            # normalize values
            if key in norm_keys and rows[key]:

                if key not in features_norm_dict.keys():
                    features_norm_dict[key] = []

                if rows[key] not in features_norm_dict[key]:
                    features_norm_dict[key].append(rows[key])

                rows[key] = features_norm_dict[key].index(rows[key])

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

print('dumping pickle')
pickle.dump(features_norm_dict, open(features_norm_dump, 'wb'))
print(count)
print('A job well done!!')
