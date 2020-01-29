from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()

class User(DB.Model):
    id = DB.Column(DB.BigInteger, primary_key=True)
    name = DB.Column(DB.String(20), nullable=False)
    followers = DB.Column(DB.BigInteger, nullable=False)
    # Tweets Ids are ordinal ints, so we can fetch most recent tweets
    newest_tweet_id = DB.Column(DB.BigInteger, nullable=False)

    def __repr__(self):
        return 'User {}>'.format(self.name)

class Tweet(DB.Model):
    id = DB.Column(DB.BigInteger, primary_key=True)
    text = DB.Column(DB.Unicode(280), nullable=False)
    user_id = DB.Column(DB.BigInteger, DB.ForeignKey('user.id'), nullable=False)
    user = DB.relationship("User", backref=DB.backref('tweets', lazy=True))
    embedding = DB.Column(DB.PickleType, nullable=False)

    def __repr__(self):
        return '<Tweet {}>'.format(self.text)
