import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

from web_app.database_functions.Get_Table import get_table
from web_app.functions.Clean_Tweet import clean_tweet

def predict_user(elephantsql_client, user1, user2, tweet):

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

    import random
    temp = list(zip(tweets, users))
    random.shuffle(temp)
    tweets, users = zip(*temp)

    X = tweets
    y = users

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

    vectorizer = CountVectorizer()
    train_vector = vectorizer.fit_transform(X_train)
    test_vector = vectorizer.transform(X_test)

    clr = LogisticRegression()
    clr.fit(train_vector, y_train)
    scores = clr.score(test_vector, y_test) # accuracy

    tweet = clean_tweet(tweet)
    tweet = pd.DataFrame({'tweet':[tweet]})
    tweet = vectorizer.transform(tweet['tweet'])
    predicted_user = clr.predict(tweet)

    return predicted_user[0]