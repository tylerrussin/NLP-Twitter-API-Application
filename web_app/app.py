from os import getenv
from flask import Flask, render_template, request, redirect
import tweepy 

from web_app.Generate_Tweets import generate_tweets
from web_app.database_functions.Connect import connect
from web_app.database_functions.Get_Table import get_table
from web_app.database_functions.Drop_Table import drop_table
from web_app.database_functions.Create_Table import create_table
from web_app.database_functions.Single_Insert import single_insert

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

        # Initiating usernames table
        command = '''CREATE TABLE IF NOT EXISTS usernames_table (username       varchar(30))'''
        create_table(elephantsql_client, command)

        # Initiating comparisions table
        command = '''CREATE TABLE IF NOT EXISTS comparision_table (comparision_str       varchar(500))'''
        create_table(elephantsql_client, command)

        # Close the database connection
        elephantsql_client.close()
        print('Connection is closed.')

        return redirect('/')

    @app.route('/')
    def index():
        # Database connection
        elephantsql_client = connect(ELEPHANTSQL_DATABASE, ELEPHANTSQL_USERNAME, ELEPHANTSQL_PASSWORD, ELEPHANTSQL_HOST)

        command = '''SELECT username FROM usernames_table'''
        usernames = get_table(elephantsql_client, command)

        command = '''SELECT comparision_str FROM comparision_table'''
        comparisions = get_table(elephantsql_client, command)

        # Close the connection
        elephantsql_client.close()
        print('Connection is closed.')

        return render_template('base.html', title='Home', users=usernames, comparisons=comparisions)

    @app.route('/add_user', methods=['POST'])
    def add_user():
        name = request.values['user_name']
        name = name.lower()
        if name[0] != '@':
            name = '@' + name

        # Database connection
        elephantsql_client = connect(ELEPHANTSQL_DATABASE, ELEPHANTSQL_USERNAME, ELEPHANTSQL_PASSWORD, ELEPHANTSQL_HOST)

        # Does user already exist
        command = '''SELECT username FROM usernames_table'''
        usernames = get_table(elephantsql_client, command)
        
        if name not in usernames:
            try:
                # Building Inital user tweet table
                command = '''CREATE TABLE IF NOT EXISTS {}_tweets_table (tweet       varchar(500))'''.format(name[1:])
                create_table(elephantsql_client, command)

                # Populate database
                generate_tweets(elephantsql_client, TWITTER, name)

                # Adding user to the usernames table
                query = "INSERT INTO usernames_table (username) VALUES ('{}')".format(name)
                single_insert(elephantsql_client, query)

                # Test if user has enough tweets
                command = '''SELECT tweet FROM {}_tweets_table'''.format(name[1:])
                user_tweets = get_table(elephantsql_client, command)
                if len(user_tweets) < 3000:
                    output_message = 'API could not retrive enough tweets for analysis'

            except:
                # Failed to get twitter data
                command = '''DROP TABLE {}_tweets_table;'''.format(name[1:])
                drop_table(elephantsql_client, command)
                output_message = 'API failed to find inputed user'

        # make an output message. display it under add user button
        


        # Close the connection
        elephantsql_client.close()
        print('Connection is closed.')

        return redirect('/')


    return app

