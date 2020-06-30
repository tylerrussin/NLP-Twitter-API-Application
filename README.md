# Twitter Tweet Predicter Web Application

# Introduction

With the increase in data driven teqnicest being developed methods to integrate such models within web application enviorments is a vital necessity. Data flows through websites and with propper sytems in place that data can be used to cator to the user experiene or be extracted for the solving of real world problems. This demo application aims to be an example of this relationship as it takes in data in real time from the twitter api and learns to predict which twitter user is most likely to say a given phrase.

## Usage

Users can use the interavtive front end

## Modles used

This appliction uses a Random Forest Classifer that is trained in real time on tokenized tweet data

```python
def predict_user(user1_name, user2_name, tweet_text):
    user1 = User.query.filter(User.name == user1_name).one()
    user2 = User.query.filter(User.name == user2_name).one()
    user1_embeddings = np.array([tweet.embedding for tweet in user1.tweets])
    user2_embeddings = np.array([tweet.embedding for tweet in user2.tweets])
    embeddings = np.vstack([user1_embeddings, user2_embeddings])
    labels = np.concatenate([np.ones(len(user1.tweets)),
                            np.zeros(len(user2.tweets))])
    log_reg = LogisticRegression().fit(embeddings, labels)
    tweet_embedding = BASILICA.embed_sentence(tweet_text, model='twitter')
    #import pdb; pdb.set_trace()
    return log_reg.predict(np.array(tweet_embedding).reshape(1,-1))
```




## License
[MIT](https://choosealicense.com/licenses/mit/)
