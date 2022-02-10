from os import getenv
import psycopg2

from flask import Flask, render_template

from database_functions.Connect import connect
from database_functions.Single_insert import single_insert

import tweepy 
import basilica

TWITTER_CONSUMER_API_KEY = getenv('TWITTER_CONSUMER_API_KEY')
TWITTER_CONSUMER_API_SECRET = getenv('TWITTER_CONSUMER_API_SECRET')
TWITTER_ACCESS_TOKEN = getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = getenv('TWITTER_ACCESS_TOKEN_SECRET')
BASILICA_KEY = getenv('BASILICA_KEY')

TWITTER_AUTH = tweepy.OAuthHandler(TWITTER_CONSUMER_API_KEY,TWITTER_CONSUMER_API_SECRET)
TWITTER_AUTH.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
TWITTER = tweepy.API(TWITTER_AUTH)
BASILICA =basilica.Connection(BASILICA_KEY)

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

@app.route('/add_user')
def add_user():
    # Create a new table for the user
    temp_user = 'elonmusk'
    twitter_user = TWITTER.get_user(screen_name='elonmusk')
    tweets = twitter_user.timeline(count=200)
    print(tweets[0].text)
    elephantsql_client = connect(ELEPHANTSQL_DATABASE, ELEPHANTSQL_USERNAME, ELEPHANTSQL_PASSWORD, ELEPHANTSQL_HOST)
    command = '''
    CREATE TABLE IF NOT EXISTS {}_tweets_table (id                 SERIAL PRIMARY KEY,
                                                tweet_text             varchar(500))
                                            
    '''.format(temp_user)
    try:

        # A "cursor", a structure to iterate over db records to perform queries
        cur = elephantsql_client.cursor()

        # Execute commands in order
        cur.execute('DROP TABLE {}_tweets_table;'.format(temp_user))
        cur.execute(command)

        # Close communication with the PostgreSQL database server
        cur.close()

        # Commit the changes
        elephantsql_client.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        cur.close()

    # Add resent tweets to database
    # Inserting data from dataframe --- obviously not optimal but good for demonstration
    for index, tweet in enumerate(tweets):
        query = "INSERT INTO {}_tweets_table (id, tweet_text) VALUES ('{}', '{}')".format(temp_user, index, tweet.text)
        single_insert(elephantsql_client, query)

    # Close the connection
    elephantsql_client.close()
    print('Connection is closed.')

    return 'hey I think we got it'