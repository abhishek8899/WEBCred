import subprocess  # isort:skip
import time  # isort:skip

# os.spawnl(os.P_NOWAIT, 'python', 'run_corenlp_server.py')  # isort:skip
subprocess.Popen(['python', 'run_corenlp_server.py'])  # isort:skip

time.sleep(3)
from dotenv import load_dotenv
from flask import jsonify
from flask import render_template
from flask import request
# from utils.databases import Features
from utils.databases import Health_Features
from utils.essentials import app
from utils.essentials import Database
from utils.essentials import WebcredError
from utils.webcred import Genre

import copy
import json
import logging
import os
import requests
import subprocess
import timeout_decorator


app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
load_dotenv(dotenv_path='.env')
logger = logging.getLogger('WEBCred.app')
logging.basicConfig(
    filename='log/logging.log',
    filemode='a',
    format=  # noqa
    '[%(asctime)s] {%(name)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO
)


class Captcha(object):
    def __init__(self, resp=None, ip=None):
        google_api = 'https://www.google.com/recaptcha/api/siteverify'
        self.url = google_api
        self.key = '6LcsiCoUAAAAAL9TssWVBE0DBwA7pXPNklXU42Rk'
        self.resp = resp
        self.ip = ip
        self.params = {
            'secret': self.key,
            'response': self.resp,
            'remoteip': self.ip
        }

    def check(self):
        result = requests.post(url=self.url, params=self.params).text
        result = json.loads(result)
        return result.get('success', None)


@app.route("/start", methods=['GET'])
def start():

    addr = request.environ.get('REMOTE_ADDR')
    g_recaptcha_response = request.args.get('g-recaptcha-response', None)
    response_captcha = Captcha(ip=addr, resp=g_recaptcha_response)

    if not response_captcha.check() and addr != '127.0.0.1':
        result = "Robot not allowed"

        return result

    data = collectData(request)

    # prevent users to know of dump location and other db attributes
    excluding_keys = [
        'text',
        'html',
        'id',
        'cookie',
        'cookienorm',
        'site',
        'sitenorm',
        '_sa_instance_state',
    ]

    for keys in excluding_keys:
        if keys in data.keys():
            del data[keys]

    return jsonify(data)


@app.route("/")
def index():
    return render_template("index.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# FIXME Robustness
# TODO run collectdata through a child process,
# which should be restarted, if mem excedes some (80%) limit
@timeout_decorator.timeout(300)
def collectData(request):

    data = {}

    # because self.request.args is of ImmutableMultiDict form
    if not isinstance(request, dict):
        request = dict(request.args)
        for k, v in request.items():
            if isinstance(request.get(k, None), list):
                request[k] = str(v[0])
            else:
                request[k] = str(v)

    try:

        database = Database(Health_Features)
        dt = Genre(database, request)
        data = dt.assess()
        # store it in data, if webcred throws no error
        database.update('url', data['url'], copy.deepcopy(data))

    except WebcredError as e:
        data['error'] = e.message

    except Exception:

        error = WebcredError()
        error.traceerror(log='info')

        # HACK if it's not webcred error,
        #  then probably it's python error
        data['error'] = 'Fatal Error'

    return data


def appinfo(url=None):
    pid = os.getpid()
    # print pid
    cmd = ['ps', '-p', str(pid), '-o', "%cpu,%mem,cmd"]
    # print
    while True:
        info = subprocess.check_output(cmd)
        print info
        time.sleep(3)

    print 'exiting appinfo'
    return None


if __name__ == "__main__":

    app.run(
        threaded=True,
        host='0.0.0.0',
        debug=False,
        port=5050,
    )
