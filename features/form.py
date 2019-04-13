from bs4 import BeautifulSoup
from features.content import get_matches
from functools import wraps
from urlparse import urlparse

import re


from utils.urls import Urlattributes


def makeurl(func):
    '''
    :param func:
    :return: url from Urlattributes instance
    '''

    @wraps(func)
    def wrapper(*args, **kwargs):
        if isinstance(args[0], Urlattributes):
            return func(args[0].geturl())
        else:
            return func(args[0])

    return wrapper


@makeurl
def depth(url):

    path = urlparse(url=url).path

    length = 0

    if path[0] == '/' or path[-1] == '/':
        length = -1

    length += len(path.split('/'))

    return length


# already covered in surface features
# @makeurl
# def gtld(url):
#     netloc = parseurl(url).netloc
#     return netloc.split('.')[-1]


@makeurl
def doc_type(url):

    path = urlparse(url=url).path

    if path[-1] == '/':
        path = path[:-1]

    path = path.split('/')[-1]

    splitter = path.split('.')
    if len(splitter) > 1:
        type = splitter[-1]
        if not type == 'htm':
            return type
    return 'html'


@makeurl
def lexical(url):
    '''
    :return: list of matched lexical terms
    '''
    path = urlparse(url=url).path
    # FIXME need to relook into this
    lexical_terms = [
        'faq', 'news', 'board', 'detail', 'list', 'termsqna', 'index', 'shop',
        'data', 'go', 'view', 'front', 'main', 'company', 'item', 'paper',
        'bbslist', 'product', 'read', 'papers', 'start', 'file', 'gallery',
        'introduction', 'info', 'login', 'search', 'research', 'bbs', 'link',
        'intro', 'people', 'profile', 'video', 'photo'
    ]

    count = {}
    for term in lexical_terms:
        regex_exp = [re.compile(re.escape(term), re.X)]
        matches = get_matches(path, regex_exp=regex_exp)
        count[term] = len(matches)

    return count


def getCountOfHtml(url):
    '''
    :param url: Urlattributes instance
    :return: count of html tags
    '''
    html = url.gethtml()
    count = {}
    tags = [tag.name for tag in BeautifulSoup(html, 'html.parser').find_all()]
    for i in tags:
        if i in count.keys():
            count[i] += 1
        else:
            count[i] = 1
    return count
