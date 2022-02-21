from os import getenv
from flask import Flask, render_template
import tweepy 

from database_functions.Connect import connect
from database_functions.Get_Table import get_table
from database_functions.Drop_Table import drop_table

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


def create_app():
    app = Flask(__name__)

    @app.route('/reset')
    def reset():
        '''Removes all tables from the SQL server'''
        
        # Database connection
        elephantsql_client = connect(ELEPHANTSQL_DATABASE, ELEPHANTSQL_USERNAME, ELEPHANTSQL_PASSWORD, ELEPHANTSQL_HOST)

        # Removing all user tweet tables within SQL server
        command = '''SELECT username FROM usernames_table'''
        usernames = get_table(elephantsql_client, command)
        for user in usernames:
            command = '''DROP TABLE {}_tweets_table;'''.format(user[1:])
            # Execute commands in order
            drop_table(elephantsql_client, command)

        # Removing usernames table within SQL server
        command = '''DROP TABLE usernames_table;'''
        drop_table(elephantsql_client, command)

        # Removing comparision table within SQL server
        command = '''DROP TABLE comparision_table;'''
        drop_table(elephantsql_client, command)

        # Close the database connection
        elephantsql_client.close()
        print('Connection is closed.')

        return 'SQL Server Reset'

    @app.route('/')
    def index():
        return 'Hello World'

    return app

