import tweepy
from  functions.Clean_Tweet import clean_tweet
from database_functions.Single_Insert import single_insert

def generate_tweets(elephantsql_client, TWITTER, user):
    """ Calling Twitter API, adding tweets to user database """

    base_query = '''INSERT INTO {}_tweets_table (tweet) VALUES '''.format(user[1:])     # base insert statment
    query = base_query
    count = 0

    # Calling twitter api and iterating over returned tweets
    for status in tweepy.Cursor(TWITTER.user_timeline, screen_name=user, tweet_mode="extended", count=200).items():
        if count == 1000:
            query = query[:-1]  # Removing comma
            single_insert(elephantsql_client, query)    # Inserting tweets into user database
            query = base_query
            count = 0
        else:    
            query = query + "('" + clean_tweet(status.full_text) + "'),"    # Adding tweet value to query string
            count = count + 1

    query = query[:-1]  # Removing comma
    single_insert(elephantsql_client, query)    # Inserting tweets into user database