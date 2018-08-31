'''
Prepare set of sheets for genre analysis
One can set total sets
One can set total urls to be present in each set
'''

from random import randint
from urlparse import urlparse
from utils.essentials import WebcredError
from utils.urls import PatternMatching

import copy
import logging
import os
import shutil


logger = logging.getLogger('WEBCred.kit')
logging.basicConfig(
    filename='log/logging.log',
    filemode='a',
    format='[%(asctime)s] {%(name)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO
)


def geturl(max_sets, len_entries, common_entries):
    '''
    :param max_sets: number of required sets of sheets
    :param len_entries: total number of urls
    :param common_entries: number of repeated entry of urls
    :return: max_sets number of sets with each set
        having maxentr_perset entries
    '''

    print('preparing sets')
    sets = {}
    # so as to ensure each set has equal number of entries
    len_entries -= ((len_entries * common_entries) % max_sets) / common_entries
    maxentr_perset = len_entries * common_entries / max_sets

    print('len_entries=', len_entries, 'maxentr_perset=', maxentr_perset)

    count = 0
    # select ith url
    for i in range(0, len_entries - 5):
        orderSet = []
        for j in range(0, common_entries):
            while True and count < (len_entries * common_entries - 1):
                # get set_num to put i into
                set_num = randint(0, max_sets - 1)
                # check if set_num doesn't already contains ith url
                if not sets.get(set_num):
                    sets[set_num] = []
                    break
                if len(sets[set_num]) < maxentr_perset:
                    if set_num not in orderSet:
                        break
            # put ith url into set_num
            sets[set_num].append(i)
            orderSet.append(set_num)
            count += 1
    print('sets prepared')
    return sets


def getSheets(max_sets, common_entries, netloc_list, total_required_url=None):
    '''

    :param max_sets: number of sets of sheets requried
    :param common_entries: number of common entries of each url
    :param netloc_list: lists of netlocs, which are not allowed in the sheets
    :param total_required_url: number of distinct urls required combining
    all sheets
    :return: prepare csv sheets at 'data/Genre_Labels/survey/' folder
    '''

    print('preparing sheets')

    urlFile = open('data/essentials/complete_urls.txt', 'r')
    urlList = urlFile.read().split()
    urlFile.close()

    urlList = filterdomain(urlList, netloc_list)

    global article_count, article_urls

    article_count = -1
    fi = open('data/Genre_Labels/dump/article_urls.txt', 'r')
    article_urls = fi.read().split()

    if total_required_url and total_required_url < len(urlList):
        urlList = filterdomain(urlList, netloc_list)[:total_required_url]

    sets = geturl(max_sets, len(urlList), common_entries)

    # index of urls, where articles are present for cross-validation
    article_index = [0, 8, 14, 28, 42, 56]  # for nanda
    # article_index = [
    #     0, 10, 25, 37, 49, 60, 75, 87, 98, 103
    # ]  # for figure-eight
    dump_filename = 'data/Genre_Labels/dump/survey/Survey' + '.csv'
    dump_file = open(dump_filename, 'a')
    content = 'URL, Labels \n'
    dump_file.write(content)
    for i in sets.keys():
        for j in sets[i]:
            if sets[i].index(j) in article_index:
                content = str(getarticleurl()) + str('\n')
                dump_file.write(content)
                # print sets[i].index(j), content
            content = str(urlList[j]) + str('\n')
            dump_file.write(content)
    dump_file.close()

    print('sheets prepared')


def getarticleurl():
    '''
    :return: url from article list
    '''

    global article_count, article_urls

    article_count += 1
    return article_urls[article_count].split(',')[0]


def filterdomain(urlList=None, filterList=None):
    '''
    :param urlList: list of all urls
    :param filterList: list of netlocs, which are not allowed in final
    list of url
    :return: list of filtered urls which have no netlocs from filterList
    '''

    di = open('data/Genre_Labels/dump/article_urls.txt', 'a')
    urls = copy.deepcopy(urlList)
    for i in urlList:
        netloc = urlparse(i).netloc
        if netloc in filterList:
            di.write(','.join([i, '\n']))
            urls.remove(i)

        # prepare list of netlocs present in urls.text
        # if netloc not in locs:
        #     locs.append(netloc)
        #     netloc = str(netloc) + '\n'
        #     fi.write(netloc)

    return urls


# prepare filter list
def prepare_filterList():
    '''
    filter urls which has certain netloc, as listed in var keywords
    or have '#' at the starting
    :return: Write all filtered netlocs in
        'data/Genre_Labels/filtered_netlocs.txt'
    '''

    fi = open('data/Genre_Labels/netlocs_0.txt', 'r')
    fi_data = fi.read().split()
    # list of all filtered netlocs
    di = open('data/Genre_Labels/filtered_netlocs.txt', 'a')
    pattern_matching = PatternMatching()
    keywords = [
        'news',
        'article',
        'blog',
        'timesofindia',
        'eweek',
        'nytimes',
        'wiki',
        'books',
        'developer',
        'docs',
        'documents',
        'journals',
        'scholar.google',
        'dblp',
        'ieee',
        'acm',
        'archive.org',
        'microsoft.com',
        'youtube',
        'facebook',
        'economist',
        'indiatimes',
        'twitter',
        'post',
        'tribune',
    ]
    pattern = pattern_matching.regexCompile(keywords)

    for netloc in fi_data:
        if netloc.startswith('#'):
            # print(netloc.split('#')[-1])
            netloc = str(netloc.split('#')[-1]) + '\n'
            di.write(netloc.split('#')[-1])
        else:
            match, matched = pattern_matching.regexMatch(
                pattern=pattern, data=str(netloc)
            )
            if match:
                netloc = str(netloc) + '\n'
                di.write(netloc)

    fi.close()
    di.close()


if __name__ == "__main__":

    # remove existing filterList and survey sheets
    try:
        os.remove('data/Genre_Labels/filtered_netlocs.txt')
        os.remove('data/Genre_Labels/dump/article_urls.txt')
        survey_path = 'data/Genre_Labels/dump/survey'
        if os.path.exists(survey_path):
            shutil.rmtree(survey_path)
        os.makedirs(survey_path)
    except Exception:

        er = WebcredError()
        er.traceerror(log='info')

    # prepare filterList
    prepare_filterList()

    # for nanda, 10800 urls
    # max_sets = 360
    # common_entries = 1
    # url_per_set = 33
    # url_per_set -= 3  # for nanda

    # for figure-eight, 10800 urls
    max_sets = 100
    common_entries = 1
    url_per_set = 70
    # url_per_set -= 6  # for figure-eight

    # final calculations 10800*4*.9/4+5000 = 14720

    filterList = open('data/Genre_Labels/filtered_netlocs.txt', 'r')
    filterList_data = filterList.read().split()
    filterList.close()

    getSheets(
        max_sets, common_entries, filterList_data,
        max_sets * url_per_set / common_entries
    )
