import matplotlib  # isort:skip
matplotlib.use('TkAgg')  # isort:skip
import matplotlib.pyplot as pl  # isort:skip

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

import json
import logging
import numpy as np
import os
import pandas as pd
import seaborn as sns
import sys
import threading
import traceback

excluding_keys = ['_sa_instance_state']

with open('data/essentials/weightage.json') as f:
    weightage_data = json.load(f)

load_dotenv(dotenv_path='.env')

logger = logging.getLogger('WEBCred.essentials')
logging.basicConfig(
    filename='log/logging.log',
    filemode='a',
    format='[%(asctime)s] {%(name)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO
)

app = Flask(__name__, root_path=os.getcwd())

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
'''
To create our database based off our model, run the following commands
$ python
>>> from app import db
>>> db.create_all()
>>> exit()'''

Base = declarative_base()

# keywords used to check real_world_presence
hyperlinks_attributes = ['contact', 'email', 'help', 'sitemap']

# these keys are used for credibility assessment
# {'features name': ['functions', 'Args1', 'whether normalization is
# required', 'return type']}
apiList = {
    'lastmod': ['surface.getDate', '', 'norm', 'Integer'],
    'domain': ['surface.getDomain', '', 'norm', 'String(120)'],
    'inlinks': [
        'surface.getInlinks',
        '',
        'norm',
        'BIGINT',
    ],
    'outlinks': [
        'surface.getOutlinks',
        '',
        'norm',
        'Integer',
    ],
    'hyperlinks': [
        'surface.getHyperlinks',
        hyperlinks_attributes,
        'norm',
        'JSON',
    ],
    'imgratio': ['surface.getImgratio', '', 'norm', 'FLOAT'],
    'brokenlinks': ['surface.getBrokenlinks', '', 'norm', 'Integer'],
    'cookie': ['surface.getCookie', '', '', 'Boolean'],
    'langcount': ['surface.getLangcount', '', 'norm', 'Integer'],
    'misspelled': ['surface.getMisspelled', '', 'norm', 'Integer'],
    'responsive': ['surface.getResponsive', '', 'norm', 'Boolean'],
    'ads': ['surface.getAds', '', 'norm', 'Integer'],
    'pageloadtime': ['surface.getPageloadtime', '', 'norm', 'Integer'],
    'text': ['utilities.dumpText', '', '', 'String'],
    'html': ['utilities.dumpHtml', '', '', 'String'],
}

genreList = {
    # 'keywords': ['content.doc_keyword', '', '', 'ARRAY(db.String)'],
    'pos': ['content.getPos', '', '', 'JSON'],
    'symbols': ['content.getSymbols', '', '', 'JSON'],
    'tokens': ['content.getIndividualTokens', '', '', 'JSON'],
    # 'sentiment': ['content.getSentiment', '', '', 'JSON'],
    'depth': ['form.depth', '', '', 'Integer'],
    'doc_type': ['form.doc_type', '', '', 'String(120)'],
    'lexical_terms': ['form.lexical', '', '', 'JSON'],
    'html_tags': ['form.getCountOfHtml', '', '', 'JSON'],
}


# A class to catch error and exceptions
class WebcredError(Exception):
    """An error happened during assessment of site.
    """

    def __init__(self, message=None):
        if message:
            self.message = message

    def __str__(self):
        return repr(self.message)

    def traceerror(self, log='debug'):
        '''
        set log to 'info' if require it to register it to logs
        :param log: specify logger attribute
        :return: ex_value, stack_trace of error
        '''

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

        if log == 'info':
            logger.info(ex_value)
            logger.info(stack_trace)
        # elif log == 'debug':
        #     pass

        return ex_value, stack_trace


class MyThread(threading.Thread):
    # def __init__(
    #         self, Module='api', Method=None, Name=None, Url=None, Args=None
    # ):
    #     pass

    def __init__(self, func, Name, Url, Args=None):

        threading.Thread.__init__(self)

        self.func = func
        self.name = Name
        self.url = Url
        self.args = Args
        self.result = None

        if Args and Args != '':
            self.args = Args

    def run(self):
        try:
            if self.args:
                self.result = self.func(self.url, self.args)
            else:
                self.result = self.func(self.url)

        except Exception:
            error = WebcredError()
            ex_value, stack_trace = error.traceerror()

            if not ex_value.message == 'Response 202':
                logger.info(ex_value)
                logger.info(stack_trace)

            self.result = None

    def getResult(self):
        return self.result

    # clear url if Urlattributes object
    def freemem(self):
        self.url.freemem()


class Database(object):
    def __init__(self, database):
        engine = db.engine
        # check existence of table in database
        if not engine.dialect.has_table(engine, database.__tablename__):
            # db.create_all()
            Base.metadata.create_all(engine, checkfirst=True)
            logger.info('Created table {}'.format(database.__tablename__))

        self.db = db
        self.database = database

    def filter(self, name, value):

        return self.db.session.query(
            self.database
        ).filter(getattr(self.database, name) == value)

    def exist(self, name, value):

        if self.filter(name, value).count():
            return True

        return False

    def getdb(self):
        return self.db

    def getsession(self):
        return self.db.session

    def add(self, data):
        logger.debug('creating entry')
        reg = self.database(data)
        self.db.session.add(reg)
        self.commit()

    def update(self, name, value, data):
        # TODO pull out only items of available columns of table
        if not self.filter(name, value).count():
            self.add(data)
        else:
            logger.debug('updating entry')

            # we want assess_time only at the time of creation
            ignore_items = ['assess_time', '_sa_instance_state']

            for i in ignore_items:
                if data.get(i):
                    del data[i]

            try:
                self.filter(name, value).update(data)
            except Exception:
                error = WebcredError()
                error.traceerror(log='info')

            self.commit()

    def commit(self):
        try:
            self.db.session.commit()
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

            logger.debug(ex_value)
            logger.debug(stack_trace)

            logger.debug('Rolling back db commit')

            self.getsession().rollback()

    def getdata(self, name=None, value=None):
        global excluding_keys
        if self.exist(name, value):
            local_data = self.filter(name, value).all()[0].__dict__
            for key in excluding_keys:
                if local_data.get(key):
                    local_data.pop(key)

            return local_data

        return None

    def getcolumns(self):

        return self.database.metadata.tables[self.database.__tablename__
                                             ].columns.keys()

    def gettablename(self):

        return self.database.__tablename__

    def getcolumndata(self, column):
        return self.getsession().query(getattr(self.database, column))

    def getdbdata(self):
        data = []
        global excluding_keys
        for i in self.getcolumndata('url'):
            if not self.getdata('url', i).get('error'):
                local_data = self.getdata('url', i)
                data.append(local_data)

        return data


class Correlation(object):
    def __init__(self):
        pass

    def getcorr(self, data, features_name):

        # supply data to np.coorcoef
        dataframe = pd.DataFrame(
            data=np.asarray(data)[0:, 0:],
            index=np.asarray(data)[0:, 0],
            columns=features_name
        )
        corr = dataframe.corr()

        return corr

    def getheatmap(self, data, features_name):

        corr = self.getcorr(data, features_name)

        # get correlation heatmap
        sns.heatmap(
            corr,
            xticklabels=features_name,
            yticklabels=features_name,
            cmap=sns.diverging_palette(220, 10, as_cmap=True)
        )
        # show graph plot of correlation
        pl.show()


def merge_two_dicts(x, y):
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z
