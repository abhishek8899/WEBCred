'''
Before running this file. Start the server
'''
from features.tfidf import all_files
from features.tfidf import doc_folder
from features.tfidf import global_term_freq
from features.tfidf import global_terms_in_doc
from features.tfidf import num_docs
from functools import wraps
from nltk import sent_tokenize
from stanfordcorenlp import StanfordCoreNLP

import json
import math
import re
import regex as currency_re
import string


class StanfordNLP:
    def __init__(self, host='http://localhost', port=9000):
        self.nlp = StanfordCoreNLP(host, port=port, timeout=30000)
        self.nlp = StanfordCoreNLP(host, port=port, timeout=30000)
        self.props = {
            'annotators': 'tokenize,ssplit,pos,lemma,ner,parse,depparse,'
            'dcoref,relation,sentiment,truecase,cleanxml,relation,'
            'natlog,quote',
            'pipelineLanguage': 'en',
            'outputFormat': 'json',
            'options': {
                "ner.useSUTime": False
            },
        }

    # get tokens of paragraph
    def word_tokenize(self, paragraph):
        return self.nlp.word_tokenize(paragraph)

    def sentence_tokenize(self, paragraph):
        return sent_tokenize(paragraph)

    def character_tokenize(self, paragraph):
        return paragraph

    def digit_tokenize(self, paragraph):
        return re.compile(r'\d+').findall(paragraph)

    def punctuation_tokenize(self, paragraph):
        regex = re.compile('[%s]' % re.escape(string.punctuation))
        return regex.findall(paragraph)

    def misspell_tokenize(self, paragraph):
        # TODO some nltk brown corpus shit
        tokens = []
        return tokens

    def pos(self, paragraph):
        '''
        get pos counts for a given paragraph
        '''
        return self.nlp.pos_tag(paragraph)

    # get sentiment(positive, neutral, negative) count for given paragraph
    def sentiment(self, paragraph):
        val = self.nlp._request(annotators='sentiment', data=paragraph)
        count = {}
        for sentence in val['sentences']:
            sentiment = sentence['sentiment']
            if sentiment not in count.keys():
                count[sentiment] = 1
            else:
                count[sentiment] += 1
        return count

    def ner(self, sentence):
        return self.nlp.ner(sentence)

    def parse(self, sentence):
        return self.nlp.parse(sentence)

    def question(self, sentence):
        parsed = self.parse(sentence)[:15].split('(')
        if 'SQ ' in parsed:
            return "Inverted question"
        elif 'SBARQ\n' in parsed:
            return "Direct question"
        return "No question"

    def dependency_parse(self, sentence):
        return self.nlp.dependency_parse(sentence)

    def annotate(self, sentence):
        return json.loads(self.nlp.annotate(sentence, properties=self.props))

    def getnlp(self):
        return self.nlp

    @staticmethod
    def tokens_to_dict(_tokens):
        tokens = {}
        for token in _tokens:
            tokens[int(token['index'])] = {
                'word': token['word'],
                'lemma': token['lemma'],
                'pos': token['pos'],
                'ner': token['ner']
            }
        return tokens


token_symbols = {
    'currency': '',
    'date': '',
    'scientific_notation': '',
    # TODO add more keywords to this
    'shop': ['sell', 'buy', 'cart', 'purchase'],
    'help': ['faq', 'help', 'support'],
    # FIXME need improvisation here
    'contact': ['email', 'phone', 'address'],
}

sNLP = StanfordNLP()


def makestr(func):
    '''
    non-key will be converted to string

    :param func:
    :return:
    '''

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not all(isinstance(arg, str) for arg in args):
            return func(*[str(arg) for arg in args], **kwargs)
        return func(*args, **kwargs)

    return wrapper


@makestr
def get_matches(paragraph, regex_exp):
    '''
    :param paragraph: Input could be word, sentence, paragraph
    :param regex_exp: list of compiled regex
    :return: compiled list of matched strings from paragraph
    '''
    matched_string = []
    for regex in regex_exp:
        matches = regex.findall(paragraph)
        # to ensure no double count
        for match in matches:
            paragraph = paragraph.replace(match, '', 1)
        if matches:
            matched_string.append(matches)

    return [
        item for sublist in matched_string for item in sublist
        if isinstance(sublist, list)
    ]


def currency_regex(**kwargs):
    '''
    **supported patterns**: All currency symbols

    **non-supported patterns**: Currency words are not supported

    :return: compiled list of currency symbols occurred
    '''
    return [currency_re.compile(r'\p{Sc}')]


def date_regex(**kwargs):
    '''
    **supported patterns**: '2010/08/27', '2010/08-26', '2009-02-02',
    '20/8/2018', '20/8-2018', '20-8-2018', 'March 2018', 'March 20',
    '5 March', '25 march',

    **non-supported patterns** 'March 5', 'March 25'

    :return: compiled list of date symbols occurred
    '''

    # regex should give complete matched string
    return [
        re.compile(r'\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2}', re.IGNORECASE),
        re.compile(r'\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}', re.IGNORECASE),
        re.compile(
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*\s\d{4})',
            re.IGNORECASE
        ),
        re.compile(
            r'(\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))',
            re.IGNORECASE
        ),
    ]


def keywords_regex(**kwargs):

    return [re.compile(re.escape(keys), re.X) for keys in kwargs['keywords']]


def scientific_notation_regex(**kwargs):
    '''
    **supported patterns**:
    2.99 x 10^33; 3.14159 x 10E5, -1.23E99 | 1E0 | -9.999e-999,
    1.1 x 10^9 | 2.34 X 10^12 | 3.14159 * 10^30 | 1.1x10^9 |
    2.34X10^12 | 3.14159*10^30 | 1.1 x 10e9 | 2.34 x 10E12 | 3.14159e30
    | 1.1 x 10^-9 | 2.34 X 10^-12 | 3.14159E-30 | -1.1 x 10^9 | -2.34 X 10E12
    | -3.14159 * 10e30 | -1.1x10^-9 | -2.34E-12 | -3.14159e-30 | 3.1459E+030
    | 1x10^9 | 1E9,

    **non-supported patterns**: rstuvwxyz 754.234e-23 | yz754.234e-23 | yz
    .234e-23, 33.2 x 10^7; 0.180 X 10^6.3,  +10E0 | 2.3e5.4,
    0.1 x 10^9 | 23.4 x 10^12 | 3.14159 * 10e^30 | 1.1e8.3
    1.0E-10|-2-i0.999e-8,
    1.0+i|i|2|i+2|i-1|0.122222i-0.2333|0.2|0.2i|-2-i|-1.0-i|-3.0+1i|-2.0+1.0i
    |3.0i-2.0i,
    ROOT 4.873624764e-34 | `1234567 890-= 3.8765e-
    34543 | ~! @ # $ % ^ &amp; ( % )_+ 3.345e-2384754,

    :return: compiled list of scientific notations occurred
    '''

    return [
        re.compile(
            r'((?:\d)(?:\.)(?:\d)+\s(?:x)\s(?:10)(?:e|E|\^)(?:-)?(?:\d)+)',
            re.IGNORECASE
        ),
        re.compile(r'([+-]?\d(?:\.\d+)?[Ee][+-]?\d+)', re.IGNORECASE),
        re.compile(
            r'((?:-?[1-9](?:\.\d+)?)(?:(?:\s?[X*]\s?10[E^](?:[+-]?\d+))|(?:E(?:[+-]?\d+))))',  # noqa
            re.IGNORECASE
        ),
        # iota
        # re.compile(r'([+-]?[0-9\.]{0,}[i][+-]?[i0-9\.]{0,})', re.IGNORECASE),
    ]


# TODO adverb_keywords
def doc_keyword(filename=None):
    '''
    :param filename: this file should be present under /data/dump/text folder
    :return: keywords to a document, sorted by decreasing tfidf score
    '''
    global_keyterms_in_doc = {}
    if filename:
        required_file = [doc_folder + filename]
    else:
        required_file = all_files

    for f in required_file:

        # writer = open(f + '_tfidf', 'w')
        result = []
        # iterate over terms in f, calculate their tf-idf, put in new list
        max_freq = 0
        for (term, freq) in global_terms_in_doc[f].items():
            if freq > max_freq:
                max_freq = freq
        for (term, freq) in global_terms_in_doc[f].items():
            idf = math.log(
                float(1 + num_docs) / float(1 + global_term_freq[term])
            )
            tfidf = float(freq) / float(max_freq) * float(idf)
            result.append([tfidf, term])

        # sort result on tfidf and write them in descending order
        result = sorted(result, reverse=True)
        f = f.replace(doc_folder, '', 1)
        global_keyterms_in_doc[f] = []
        global_keyterms_in_doc[f] = [term for (tfidf_score, term) in result]

    if filename:
        return global_keyterms_in_doc[filename]
    return global_keyterms_in_doc


'''
-------------from here starts token functions-----------
'''


@makestr
def getPos(paragraph):
    '''
    :param paragraph: Input could be word, sentence, paragraph
    :return: dict, count of occurrences of pos_tags in given param
    '''

    posCount = {}
    tags_list = sNLP.pos(paragraph)
    for items in tags_list:
        if items[1] in posCount.keys():
            posCount[items[1]] += 1
        else:
            posCount[items[1]] = 1

    return posCount


def getSymbols(paragraph, dictsym=token_symbols):
    '''
    :param paragraph: Input could be word, sentence, paragraph
    :return: count of occurrences of varied symbols
    '''
    symbols = {}
    for token in token_symbols.keys():
        func = token + '_regex'
        try:
            eval(func)
        except NameError:
            # for generic regex match
            func = 'keywords_regex'
            eval(func)
        symbols[token] = len(
            get_matches(
                paragraph, regex_exp=eval(func)(keywords=token_symbols[token])
            )
        )

    return symbols


@makestr
def getIndividualTokens(paragraph):
    '''
    :param paragraph:  Input could be word, sentence, paragraph
    :return: count of occurrences of individual tokens
    tokens >> sentences, words(with/without morphological analysis),
    characters, digits, individual punctuation marks, misspell
    '''
    individual_token = {
        'word': '',
        'sentence': '',
        'character': '',
        # 'alphanum': '',
        'digit': '',
        'punctuation': '',
        'misspell': '',
    }
    for key in individual_token.keys():
        func = eval('sNLP.' + key + '_tokenize')
        individual_token[key] = len(func(paragraph))

    return individual_token


@makestr
def getSentiment(paragraph):
    return sNLP.sentiment(paragraph)


if __name__ == '__main__':
    text = 'A blog post using Stanford CoreNLP Server. ' \
           'Visit www.khalidalnajjar.com for more details.'
    text += ' ' + text + text + 'This is a test'
    text += text
    # print("Annotate:", sNLP.annotate(text))
    print("POS:", sNLP.pos(text))
    notations = 'sdf 1 uW, 1 mW, 1 W, 1 m, 1.5 W, .5 W, 5E-12 F, 5 nF skdfb'
    doc_keyword('beta.html5test.com')
    getPos(text)
    para = "ROOT 4.873624764e-34 | `1234567 890-= 3.8765e-" \
           "34543 | ~! @ # $ % ^ &amp; ( % )_+ 3.345e-2384754," \
           "2.99 x 10^33; 3.14159 x 10E5, -1.23E99 | 1E0 | -9.999e-999," \
           "1.1 x 10^9 | 2.34 X 10^12 | 3.14159 * 10^30 | 1.1x10^9 |" \
           "2.34X10^12 | 3.14159*10^30 | 1.1 x 10e9 | 2.34 x 10E12 " \
           "| 3.14159e30 sjdhbfsellthis for 10$" \
           "need instanstsupport for 20rupya" \
           "| 1.1 x 10^-9 | 2.34 X 10^-12 | 3.14159E-30 | -1.1 x 10^9 | " \
           "-2.34 X 10E12 my phone is 9034 and email is 02394" \
           "| -3.14159 * 10e30 | -1.1x10^-9 | -2.34E-12 | -3.14159e-30 | " \
           "3.1459E+030" \
           "| 1x10^9 | 1E9," \
           "1.0+i i 2 i+2 i-1 0.122222i-0.2333 0.2 0.2i -2-i -1.0-i -3.0+1i " \
           "-2.0+1.0i" \
           " 3.0i-2.0i,"
    sen = ' Which tags are nouns most commonly found after? What do ' \
          'these tags' \
          ' represent? - articles or adjectives are the most common.'
    print getSentiment(sen)
    # print("Tokens:", sNLP.word_tokenize(text))
    # print("NER:", sNLP.ner(text))
    # print("Parse:", sNLP.parse(text))
    # print("Dep Parse:", sNLP.dependency_parse(text))
    # print(sNLP.question(text))
    # val = sNLP.getnlp()._request(annotators='sentiment', data=text)
