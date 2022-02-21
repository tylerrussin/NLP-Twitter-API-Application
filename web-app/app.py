from os import getenv
import psycopg2

from flask import Flask, render_template

from database_functions.Connect import connect
from database_functions.Single_insert import single_insert

import tweepy 

TWITTER_CONSUMER_API_KEY = getenv('TWITTER_CONSUMER_API_KEY')
TWITTER_CONSUMER_API_SECRET = getenv('TWITTER_CONSUMER_API_SECRET')
TWITTER_ACCESS_TOKEN = getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = getenv('TWITTER_ACCESS_TOKEN_SECRET')

TWITTER_AUTH = tweepy.OAuthHandler(TWITTER_CONSUMER_API_KEY,TWITTER_CONSUMER_API_SECRET)
TWITTER_AUTH.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
TWITTER = tweepy.API(TWITTER_AUTH)

ELEPHANTSQL_DATABASE = getenv('ELEPHANTSQL_DATABASE')
ELEPHANTSQL_USERNAME = getenv('ELEPHANTSQL_USERNAME')
ELEPHANTSQL_PASSWORD = getenv('ELEPHANTSQL_PASSWORD')
ELEPHANTSQL_HOST = getenv('ELEPHANTSQL_HOST')

app = Flask(__name__)

@app.route('/')
def index():
    elephantsql_client = connect(ELEPHANTSQL_DATABASE, ELEPHANTSQL_USERNAME, ELEPHANTSQL_PASSWORD, ELEPHANTSQL_HOST)
    test = ['user1', 'user2', 'user3']
    test2 = ['some information one', 'some info 2']
    return render_template('base.html', title='Home', users=test, comparisons=test2)

