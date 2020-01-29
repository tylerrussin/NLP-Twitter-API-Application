import basilica
import tweepy
from decouple import config
from .models import DB, Tweet, User

#TWITTER_USERS = ['elonmusk', 'nasa', 'sadserver', 'austen', 'lockeedmartin']

TWITTER_AUTH = tweepy.OAuthHandler(config('TWITTER_CONSUMER_API_KEY'),
                                   config('TWITTER_CONSUMER_API_SECRET'))
TWITTER_AUTH.set_access_token(config('TWITTER_ACCESS_TOKEN'),
                              config('TWITTER_ACCESS_TOKEN_SECRET'))
TWITTER = tweepy.API(TWITTER_AUTH)
BASILICA =basilica.Connection(config('BASILICA_KEY'))

def add_user(name):
  """Adds a user along with their tweet to our database."""
  try:
    # Using tweepy API to get user info
    twitter_user = TWITTER.get_user(name)

    # Adding recent non-retwee/reply tweets
    # the limmit on Twitter API is 200 for single request
    tweets = twitter_user.timeline(count=200,
                                   exclude_replies=True,
                                   include_rts=False,
                                   tweet_mode='extended')

    #import pdb; pdb.set_trace()

    newest_tweet_id = tweets[0].id

    # Add user info to user table in database
    db_user = User(id=twitter_user.id,
                   name=twitter_user.screen_name,
                   followers=twitter_user.followers_count,
                   newest_tweet_id=newest_tweet_id)
    DB.session.add(db_user)

    # Looping over each tweet
    for tweet in tweets:

      # Get Basilica embedding for each tweet
      embedding = BASILICA.embed_sentence(tweet.full_text,
                                          model='twitter')

      # adding tweet info to tweets table in database
      db_tweet = Tweet(id=tweet.id,
                       text=tweet.full_text[:300],
                       embedding=embedding)
      DB.session.add(db_tweet)
  except Exception as e:
    print('Error processing {}: {}'.format(name, e))
    raise e
  else:
    DB.session.commit()
