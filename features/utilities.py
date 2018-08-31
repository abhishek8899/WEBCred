import os
import re


# location where raw data (html, text) will be dumped
loct = 'data/dump'


# dump text of webpage
def dumpText(site):
    '''
    :param site: Urlattributes instance
    :return: location of raw dump
    '''

    global loct

    # trim http things
    filepath = re.sub(r'((ht|f)tp(s?)\://)', '', site.getoriginalurl())

    # special case when url is >> https../...../lekmef/
    filepath = filepath.split('/')
    if not filepath[-1]:
        del filepath[-1]

    filepath = (os.sep).join(filepath)

    # directory location
    dir_location = (os.sep).join([
        loct, 'text',
        (os.sep).join(filepath.split('/')[:-1])
    ])

    if not os.path.exists(dir_location):
        os.makedirs(dir_location)

    text_location = (os.sep).join([dir_location, filepath.split('/')[-1]])

    fi = open(text_location, 'w')
    func = getattr(site, 'gettext')
    raw = func()

    try:
        fi.write(raw)
    except UnicodeEncodeError:
        fi.write(raw.encode('utf-8'))

    fi.close()

    return text_location


# dump html of webpage
def dumpHtml(site):
    '''
    :param site: Urlattributes instance
    :return: location of raw dump
    '''

    global loct

    # trim http things
    filepath = re.sub(r'((ht|f)tp(s?)\://)', '', site.getoriginalurl())

    # special case when url is >> https../...../lekmef/
    filepath = filepath.split('/')
    if not filepath[-1]:
        del filepath[-1]

    filepath = (os.sep).join(filepath)

    # directory location
    dir_location = (os.sep).join([
        loct, 'html',
        (os.sep).join(filepath.split('/')[:-1])
    ])

    if not os.path.exists(dir_location):
        os.makedirs(dir_location)

    html_location = (os.sep).join([dir_location, filepath.split('/')[-1]])

    fi = open(html_location, 'w')
    func = getattr(site, 'gethtml')
    raw = func()

    try:
        fi.write(raw)
    except UnicodeEncodeError:
        fi.write(raw.encode('utf-8'))

    fi.close()

    return html_location
