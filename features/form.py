from bs4 import BeautifulSoup
from features.content import get_matches
from urlparse import urlparse
from utils.essentials import WebcredError

import re
import validators


# TODO test these all
class URL(object):
    def __init__(self, url):

        if not validators.url(url):
            raise WebcredError('Not a valid url')

        self.url = url
        self.parse = urlparse(url=self.url)

    def depth(self):
        path = self.parse.path
        return len(path.split('/'))

    def gtld(self):
        netloc = self.parse.netloc
        return netloc.split('.')[-1]

    def doc_type(self):
        path = self.parse.path
        return path.split('/')[-1].split('.')[-1]

    def lexical(self):
        '''
        :return: list of matched lexical terms
        '''
        path = self.parse.path
        lexical_terms = [
            'faq', 'news', 'board', 'detail', 'list', 'termsqna', 'index',
            'shop', 'data', 'go', 'view', 'front', 'main', 'company', 'item',
            'paper', 'bbslist', 'product', 'read', 'papers', 'start', 'file',
            'gallery', 'introduction', 'info', 'login', 'search', 'research',
            'bbs', 'link', 'intro', 'people', 'profile', 'video', 'photo'
        ]

        regex_exp = [
            re.compile(re.escape(keys), re.X) for keys in lexical_terms
        ]

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
