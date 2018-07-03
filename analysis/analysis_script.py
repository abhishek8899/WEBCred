sampleData = {
    "0": [
        3,
        0,
        0,
        -1,
        0,
        0,
        -1,
        0,
        0,
        1,
        0,
        -1,
    ],
    "1": [
        6,
        0,
        1,
        -1,
        0,
        0,
        0,
        0,
        0,
        1,
        0,
        -1,
    ],
    "2": [
        3,
        -1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        0,
        -1,
    ],
    "3": [
        3,
        0,
        -1,
        0,
        0,
        0,
        -1,
        0,
        0,
        1,
        0,
        0,
    ],
    "4": [
        3,
        0,
        -1,
        -1,
        0,
        0,
        0,
        1,
        0,
        1,
        0,
        0,
    ],
    "5": [
        3,
        0,
        -1,
        -1,
        0,
        0,
        0,
        1,
        0,
        1,
        0,
        0,
    ],
    "6": [
        1,
        0,
        -1,
        -1,
        0,
        0,
        -1,
        0,
        0,
        1,
        0,
        0,
    ],
    "7": [
        1,
        1,
        1,
        -1,
        0,
        0,
        -1,
        1,
        0,
        1,
        0,
        1,
    ],
    "8": [
        2,
        0,
        -1,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        0,
        0,
    ],
    "9": [
        3,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        0,
        1,
    ],
}

genre = {
    u'article': {
        u'ads': u'0.029099',
        u'brokenlinks': u'0.000006',
        u'domain': u'-0.040435',
        u'hyperlinks': u'-0.017604',
        u'imgratio': u'0.011597',
        u'inlinks': u'0.017667',
        u'langcount': u'0.029271',
        u'lastmod': u'-0.011533',
        u'misspelled': u'0.065318',
        u'outlinks': u'-0.005968',
        u'pageloadtime': u'-0.00607',
        u'responsive': u'0.011616'
    },
    u'shop': {
        u'ads': u'0',
        u'brokenlinks': u'0.000006',
        u'domain': u'-0.040435',
        u'hyperlinks': u'-0.017604',
        u'imgratio': u'0.011597',
        u'inlinks': u'0.017667',
        u'langcount': u'0.029271',
        u'lastmod': u'-0.011533',
        u'misspelled': u'0.065318',
        u'outlinks': u'0.02313',
        u'pageloadtime': u'-0.00607',
        u'responsive': u'0.011616'
    },
    u'other-genre': {
        u'ads': u'-24.0140441',
        u'brokenlinks': u'49.6275523',
        u'domain': u'24.8023672',
        u'hyperlinks': u'48.0862371',
        u'imgratio': u'-0.6922669',
        u'inlinks': u'-72.8650503',
        u'langcount': u'0.8516245',
        u'lastmod': u'50.3201873',
        u'misspelled': u'28.9997645',
        u'outlinks': u'47.4079554',
        u'pageloadtime': u'-2.2339502',
        u'responsive': u'-0.6856424'
    },
}

order = [
    'domain',
    'ads',
    'imgratio',
    'inlinks',
    'pageloadtime',
    'misspelled',
    'hyperlinks',
    'brokenlinks',
    'responsive',
    'lastmod',
    'langcount',
    'outlinks',
]

scoreboard = []
for k, v in sampleData.items():
    score = 0
    for index in range(len(v)):
        score += float(genre["shop"][order[index]]) * v[index]
    scoreboard.append(score / 100)

print scoreboard
