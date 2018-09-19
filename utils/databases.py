# -*- coding: utf-8 -*-

from sqlalchemy.dialects.postgresql import ARRAY  # noqa
from utils.essentials import apiList
from utils.essentials import Base
from utils.essentials import db
from utils.essentials import genreList


#  Our database model
class Features(Base):
    __tablename__ = 'features'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(), unique=True)
    redirected = db.Column(db.String())
    genre = db.Column(db.String(120))
    webcred_score = db.Column(db.FLOAT)
    error = db.Column(db.String(120))
    assess_time = db.Column(db.Float)

    # credibility_specific_features
    for key in apiList.keys():
        dataType = apiList[key][-1]
        exec (key + " = db.Column(db." + dataType + ")")
        if apiList[key][2]:
            norm = key + 'norm'
            exec (norm + " = db.Column(db.Integer)")

    # genre_specific_features
    for key in genreList.keys():
        dataType = genreList[key][-1]
        exec (key + " = db.Column(db." + dataType + ")")

    def __init__(self, data):
        for key in data.keys():
            setattr(self, key, data[key])

    def __repr__(self):
        return self.url


class FeaturesSet(Base):
    __tablename__ = 'feature_set'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(), unique=True)
    error = db.Column(db.String())
    dataset = db.Column(db.String())
    article = db.Column(db.FLOAT())
    shop = db.Column(db.FLOAT())
    help = db.Column(db.FLOAT())
    portrayal_individual = db.Column(db.FLOAT())
    others = db.Column(db.FLOAT())

    def __init__(self, data):
        for key in data.keys():
            setattr(self, key, data[key])

    def __repr__(self):
        return self.url


class Ranks(Base):
    __tablename__ = 'ranks'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(), unique=True)
    redirected = db.Column(db.String())
    error = db.Column(db.String())
    alexa = db.Column(db.Integer())
    wot_confidence = db.Column(db.Integer())
    wot_reputation = db.Column(db.Integer())
    alexa = db.Column(db.Integer())
    wot = db.Column(db.FLOAT())

    def __init__(self, data):
        for key in data.keys():
            setattr(self, key, data[key])

    def __repr__(self):
        return self.url


class Genre_labels(Base):
    __tablename__ = 'genre_labels'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(), unique=True)
    which_genre_does_this_web_page_belongs_to = db.Column(db.String())
    labels = db.Column(db.Integer())
    confidence = db.Column(db.FLOAT())

    def __init__(self, data):
        for key in data.keys():
            setattr(self, key, data[key])

    def __repr__(self):
        return self.url
