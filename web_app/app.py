from os import getenv
from flask import Flask, render_template, request, redirect
import tweepy 

from web_app.Generate_Tweets import generate_tweets
from web_app.database_functions.Connect import connect
from web_app.database_functions.Get_Table import get_table
from web_app.database_functions.Drop_Table import drop_table
from web_app.database_functions.Create_Table import create_table
from web_app.database_functions.Single_Insert import single_insert
from web_app.database_functions.SQL_Command import sql_command
from web_app.functions.Predict_User import predict_user

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

output_message = 'test'

def create_app():
    app = Flask(__name__)

    @app.route('/reset')
    def reset():
        '''Removes all tables from the SQL server'''

        global output_message

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

        output_message = 'Databases reset'
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

        return render_template('base.html', title='Home', users=usernames, comparisons=comparisions[::-1], message=output_message)

    @app.route('/add_user', methods=['POST'])
    def add_user():

        global output_message
        name = request.values['user_name']

        if name == '':
            output_message = 'Must enter a twitter user'
        else:
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
                    output_message = '{} successfully added to database'.format(name)
                    if len(user_tweets) < 3000:
                        output_message = 'API could not retrive enough tweets for analysis'
                        command = '''DROP TABLE {}_tweets_table;'''.format(name[1:])
                        drop_table(elephantsql_client, command)
                        command = '''DELETE FROM usernames_table WHERE username='{}';'''.format(name)
                        sql_command(elephantsql_client, command)

                except:
                    # Failed to get twitter data
                    command = '''DROP TABLE {}_tweets_table;'''.format(name[1:])
                    drop_table(elephantsql_client, command)
                    command = '''DELETE FROM usernames_table WHERE username='{}';'''.format(name)
                    sql_command(elephantsql_client, command)
                    output_message = 'API failed to find inputed user'
            
            # Close the connection
            elephantsql_client.close()
            print('Connection is closed.')

        return redirect('/')

    @app.route('/compare', methods=['POST'])
    def compare():

        global output_message

        user1 = request.values['user1']
        user2 = request.values['user2']
        tweet_text = request.values['tweet_text']

        if user1 == user2:
            output_message = 'Cannot compare a user to themselves'
        else:
            # Database connection
            elephantsql_client = connect(ELEPHANTSQL_DATABASE, ELEPHANTSQL_USERNAME, ELEPHANTSQL_PASSWORD, ELEPHANTSQL_HOST)

            prediction = predict_user(elephantsql_client, user1, user2, tweet_text)
            if user1 == prediction:
                winner = user1
                loser = user2
            else:
                winner = user2
                loser = user1
            output_message = '"{}" is more likely to be said by {} than {}'.format(
                request.values['tweet_text'], winner, loser)

            comp_message = '"{}" is more likely to be said by {} than {}'.format(request.values['tweet_text'][:50] + '...', winner, loser)
            # Adding recent comparisions
            query = "INSERT INTO comparision_table (comparision_str) VALUES ('{}')".format(comp_message)
            single_insert(elephantsql_client, query)

            # Close the connection
            elephantsql_client.close()
            print('Connection is closed.')

        return redirect('/')


    return app

