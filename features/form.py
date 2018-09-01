from bs4 import BeautifulSoup
from features.content import get_matches
from functools import wraps
from urlparse import urlparse
from utils.urls import Urlattributes

import os
import re


def makeurl(func):
    '''
    :param func:
    :return: url from Urlattributes instance
    '''

    @wraps(func)
    def wrapper(*args, **kwargs):
        if isinstance(args[0], Urlattributes):
            return func(args[0].geturl())

    return wrapper


@makeurl
def depth(url):

    path = urlparse(url=url).path

    if not path[-1]:
        del path[-1]

    path = (os.sep).join(path)

    return len(path.split('/'))


# already covered in surface features
# @makeurl
# def gtld(url):
#     netloc = parseurl(url).netloc
#     return netloc.split('.')[-1]


@makeurl
def doc_type(url):
    path = urlparse(url=url).path

    if not path[-1]:
        del path[-1]

    path = (os.sep).join(path)

    return path.split('/')[-1].split('.')[-1]


@makeurl
def lexical(url):
    '''
    :return: list of matched lexical terms
    '''
    path = urlparse(url=url).path
    lexical_terms = [
        'faq', 'news', 'board', 'detail', 'list', 'termsqna', 'index', 'shop',
        'data', 'go', 'view', 'front', 'main', 'company', 'item', 'paper',
        'bbslist', 'product', 'read', 'papers', 'start', 'file', 'gallery',
        'introduction', 'info', 'login', 'search', 'research', 'bbs', 'link',
        'intro', 'people', 'profile', 'video', 'photo'
    ]

    regex_exp = [re.compile(re.escape(keys), re.X) for keys in lexical_terms]

    # TODO get frequency of matched terms
    return set(get_matches(path, regex_exp=regex_exp))


def getCountOfHtml(html):
    '''
    :param html: clean html (no scripts)
    :return: count of html tags
    '''
    count = {}
    tags = [tag.name for tag in BeautifulSoup(html, 'html.parser').find_all()]
    for i in tags:
        if i in count.keys():
            count[i] += 1
        else:
            count[i] = 1
    return count
