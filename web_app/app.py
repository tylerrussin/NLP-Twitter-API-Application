from os import getenv
from flask import Flask, render_template, request, redirect, make_response
import tweepy 

from web_app.Generate_Tweets import generate_tweets
from web_app.database_functions.Connect import connect
from web_app.database_functions.Get_Table import get_table
from web_app.database_functions.Drop_Table import drop_table
from web_app.database_functions.Create_Table import create_table
from web_app.database_functions.Single_Insert import single_insert
from web_app.database_functions.SQL_Command import sql_command
from web_app.functions.Predict_User import predict_user


# Connect to twitter API
TWITTER_CONSUMER_API_KEY = getenv('TWITTER_CONSUMER_API_KEY')
TWITTER_CONSUMER_API_SECRET = getenv('TWITTER_CONSUMER_API_SECRET')
TWITTER_ACCESS_TOKEN = getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = getenv('TWITTER_ACCESS_TOKEN_SECRET')

TWITTER_AUTH = tweepy.OAuthHandler(TWITTER_CONSUMER_API_KEY,TWITTER_CONSUMER_API_SECRET)
TWITTER_AUTH.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
TWITTER = tweepy.API(TWITTER_AUTH)

# Connect to SQL database
ELEPHANTSQL_DATABASE = getenv('ELEPHANTSQL_DATABASE')
ELEPHANTSQL_USERNAME = getenv('ELEPHANTSQL_USERNAME')
ELEPHANTSQL_PASSWORD = getenv('ELEPHANTSQL_PASSWORD')
ELEPHANTSQL_HOST = getenv('ELEPHANTSQL_HOST')

output_message = '' # Global output message


def create_app():
    '''Main app'''
    app = Flask(__name__)

    @app.route('/reset')
    def reset():
        '''Removes all user added tables from the SQL server'''

        global output_message
        start_users = ['@justinbieber', '@nasa', '@rihanna', '@joebiden']
        start_comps = ['"never say never" is more likely to be said by @justinbieber than @rihanna', 
                       '"The #Cygnus spacecraft is safely in orbit" is more likely to be said by @nasa than @joebiden']

        # Database connection
        elephantsql_client = connect(ELEPHANTSQL_DATABASE, 
                                     ELEPHANTSQL_USERNAME, 
                                     ELEPHANTSQL_PASSWORD, 
                                     ELEPHANTSQL_HOST)

        
        # Commands
        usernames_command = '''SELECT username FROM usernames_table'''
        drop_comp_command = '''DROP TABLE comparision_table;'''
        create_comp_command = '''CREATE TABLE IF NOT EXISTS comparision_table (comparision_str       varchar(500))'''

        # Delete user added Twitter user tables
        usernames = get_table(elephantsql_client, usernames_command)
        for user in usernames:
            if user not in start_users:  
                drop_user_command = '''DROP TABLE {}_tweets_table;'''.format(user[1:])                      # Drop twitter user tables
                remove_user_command = '''DELETE FROM usernames_table WHERE username='{}';'''.format(user)   # Remove twitter username

                drop_table(elephantsql_client, drop_user_command)
                sql_command(elephantsql_client, remove_user_command)


        drop_table(elephantsql_client, drop_comp_command)       # Removing comparision table within SQL server
        create_table(elephantsql_client, create_comp_command)   # Initiating comparisions table

        # Insert past comparisions into table
        for comp_message in start_comps:
            comp_command = "INSERT INTO comparision_table (comparision_str) VALUES ('{}')".format(comp_message)
            single_insert(elephantsql_client, comp_command)

        # Close the database connection
        elephantsql_client.close()
        print('Connection is closed.')

        output_message = 'Databases reset'
        return redirect('/')


    @app.route('/')
    def index():
        '''Main templete of web application'''
        
        global output_message

        # Database connection
        elephantsql_client = connect(ELEPHANTSQL_DATABASE, 
                                     ELEPHANTSQL_USERNAME, 
                                     ELEPHANTSQL_PASSWORD, 
                                     ELEPHANTSQL_HOST)

        # Commands
        usernames_command = '''SELECT username FROM usernames_table'''
        comparisions_command = '''SELECT comparision_str FROM comparision_table'''

        # Retrive Tables
        usernames = get_table(elephantsql_client, usernames_command)
        comparisions = get_table(elephantsql_client, comparisions_command)

        # Close the connection
        elephantsql_client.close()
        print('Connection is closed.')

        return render_template('base.html', 
                               title='Compare Twitter Users', 
                               users=usernames,                     # Populates current usernames
                               users2=usernames[::-1],
                               comparisons=comparisions[::-1],      # Populates recent comparisions
                               message=output_message)              # Returns global ouptut message


    @app.route('/add_user', methods=['POST'])
    def add_user():
        '''Add new user to database'''

        global output_message
        name = request.values['user_name']

        if name == '':
            output_message = 'No username entered...'
            return redirect('/')

        name = name.lower()     # Lowercase and @ symbol parsing
        if name[0] != '@':
            name = '@' + name

        # Database connection
        elephantsql_client = connect(ELEPHANTSQL_DATABASE, 
                                     ELEPHANTSQL_USERNAME, 
                                     ELEPHANTSQL_PASSWORD, 
                                     ELEPHANTSQL_HOST)

        # Commands
        usernames_command = '''SELECT username FROM usernames_table'''
        create_table_command = '''CREATE TABLE IF NOT EXISTS {}_tweets_table (tweet       varchar(500))'''.format(name[1:])
        insert_username_command = "INSERT INTO usernames_table (username) VALUES ('{}')".format(name)
        get_tweets_command = '''SELECT tweet FROM {}_tweets_table'''.format(name[1:])
        drop_table_command = '''DROP TABLE {}_tweets_table;'''.format(name[1:])
        delete_username_command = '''DELETE FROM usernames_table WHERE username='{}';'''.format(name)

        usernames = get_table(elephantsql_client, usernames_command)    #   Current saved twitter users
        
        if name not in usernames:
            try:
                create_table(elephantsql_client, create_table_command)              # Building Inital user tweet table
                generate_tweets(elephantsql_client, TWITTER, name)                  # Populate database
                single_insert(elephantsql_client, insert_username_command)          # Adding user to the usernames table

                user_tweets = get_table(elephantsql_client, get_tweets_command)     # Test if user has enough tweets
                output_message = '{} successfully added to database'.format(name)

                # Twitter API returned less than 3000 tweets
                if len(user_tweets) < 3000:

                    # Revert table changes
                    output_message = 'API could not retrive enough tweets for analysis'
                    drop_table(elephantsql_client, drop_table_command)
                    sql_command(elephantsql_client, delete_username_command)

            except:
                # Failed to get twitter data
                output_message = 'API failed to find inputed twitter username'
                drop_table(elephantsql_client, drop_table_command)                # Revert table changes  
                sql_command(elephantsql_client, delete_username_command)
                
        else:
            output_message = 'Twitter user already in database'

        # Close the connection
        elephantsql_client.close()
        print('Connection is closed.')

        return redirect('/')


    @app.route('/compare', methods=['POST'])
    def compare():
        '''Classify inputed tweet'''

        global output_message
        user1 = request.values['user1']
        user2 = request.values['user2']
        tweet_text = request.values['tweet_text']

        if user1 == user2:
            output_message = 'Cannot compare a user to themselves'
            return redirect('/')
     
        # Database connection
        elephantsql_client = connect(ELEPHANTSQL_DATABASE, 
                                     ELEPHANTSQL_USERNAME, 
                                     ELEPHANTSQL_PASSWORD, 
                                     ELEPHANTSQL_HOST)

        # Classifing tweet
        prediction = predict_user(elephantsql_client, user1, user2, tweet_text)
        if user1 == prediction:
            winner = user1
            loser = user2
        else:
            winner = user2
            loser = user1

        output_message = '"{}" is more likely to be said by {} than {}'.format(request.values['tweet_text'], winner, loser)
        comp_message = '"{}" is more likely to be said by {} than {}'.format(request.values['tweet_text'][:50] + '...', winner, loser)

        # Command
        comp_command = "INSERT INTO comparision_table (comparision_str) VALUES ('{}')".format(comp_message)
        single_insert(elephantsql_client, comp_command)                                                         # Insert comparision

        # Close the connection
        elephantsql_client.close()
        print('Connection is closed.')

        return redirect('/')


    return app

