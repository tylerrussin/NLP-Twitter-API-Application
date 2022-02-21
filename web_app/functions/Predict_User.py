import pandas as pd
import random
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

from web_app.database_functions.Get_Table import get_table
from web_app.functions.Clean_Tweet import clean_tweet

def predict_user(elephantsql_client, user1, user2, tweet):
    '''Returns user classified to have said input tweet'''
    # Generate lists of tweets and users
    tweets = []
    users = []

    command = '''SELECT tweet FROM {}_tweets_table'''.format(user1[1:])
    user_tweets = get_table(elephantsql_client, command)
    users = users + [user1] * len(user_tweets)
    tweets = tweets + user_tweets

    command = '''SELECT tweet FROM {}_tweets_table'''.format(user2[1:])
    user_tweets = get_table(elephantsql_client, command)
    users = users + [user2] * len(user_tweets)
    tweets = tweets + user_tweets

    # Randomize lists
    temp = list(zip(tweets, users))
    random.shuffle(temp)
    tweets, users = zip(*temp)

    # Splitting the data into training and validation sets
    X = tweets
    y = users
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

    # Vectorizing the input tweet
    vectorizer = CountVectorizer()
    train_vector = vectorizer.fit_transform(X_train)
    test_vector = vectorizer.transform(X_test)

    # Fitting logistic Regression classifer model
    clr = LogisticRegression()
    clr.fit(train_vector, y_train)

    # Determining user most likely to have said tweet
    tweet = clean_tweet(tweet)
    tweet = pd.DataFrame({'tweet':[tweet]})
    tweet = vectorizer.transform(tweet['tweet'])
    predicted_user = clr.predict(tweet)

    return predicted_user[0]