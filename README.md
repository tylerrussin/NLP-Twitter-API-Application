# NLP Twitter API Application

### Introduction

The NLP Twitter API application aims to create an ecosystem of calling the Twitter API, saving Twitter API responses into a SQL database, and referencing the SQL database to classify the Twitter data using logistic regression. The application allows users to input valid Twitter usernames and text information to be used to compare which Twitter users are more likely to tweet a given message.

**Gallery**

![](assets/img/gallery.png)

### Usage

**Python Notebooks**

Located in the “notebooks” directory of this repository are the following “.ipynb” files:

- database_creation.ipynb
- modeling.ipynb

These notebooks explore the data processing and SQL database construction of this project. The “database_creation.ipynb” contains work done on the connections built to the Twitter API and SQL database. The “modeling.ipynb” contains work done on handling Twitter API timeline data as well as data cleaning and modeling.

**The Interactive Model**

The baseline work done within the python notebooks has contributed to the creation of a Flask website hosted on Heroku. The web application allows users to add new Twitter usernames to the SQL database, reference a given Twitter user’s timeline page, input artificial tweet text, compare the likelihood of Twitter users writing a given tweet, observe recent comparisons, and reset the SQL database. The structure of the web application consists of a base “app.py” file that contains the routes of the flask app, a “base.html” file that hosts the website front-end, and various functions contributing to the processes of the above-listed features.

The deployed web application can be interacted with [Here](https://nlp-twitter-api-application.herokuapp.com/)

# Overview of Twitter API and Tweet Classification Process

**Calling Twitter API**

The [Twitter API](https://developer.twitter.com/en/docs/twitter-api) allows access to information available on the [twitter.com](https://twitter.com) website in a programmatic way. Once a developer is approved by the Twitter team, unique keys are created and given to the developer to be used when referencing the API. This project utilizes the Twitter user timeline object. The timeline object hosts a given user's past interactions on Twitter including past tweets, retweets, and replies. Using the python library [tweepy](https://docs.tweepy.org/en/stable/) the Twitter API is accessed and a given user's tweet information is extracted. The Twitter API has several rate limits, for the timeline object only the last 3,200 tweets are able to be retrieved.

### SQL Database Tables

**Usernames Table**

The usernames table holds Twitter usernames as type ```(VARCHAR 30)```. Valid inputs include public Twitter usernames, usernames that have posted at least 3,000 tweets/replies, and usernames that the Twitter API returns at least 3,000 tweets for (high volume username responses are limited to only a few hundred tweets). 

**Comparison Table**

The comparison table contains past comparisons between Twitter users as type ```(VARCHAR 500)```. A user-generated tweet for classification has no length limit. However, when stored in the comparison table the tweet is limited to the first 50 characters.

**Example Comparision**

```"never say never" is more likely to be said by @justinbieber than @rihanna```

**Username Tweets Table**

For each valid username within the usernames table, a username tweets table is created containing a user’s past 3,000 to 3,200 tweets/replies as type ```(VARCHAR 500)```. The tweets/replies are referenced from the Twitter API timeline object and include the user’s most recent activity.

### Tweet Classification

**Tweet Preprocessing**

Tweet data is put through a text preprocessing pipeline. Tweet data includes the past tweets/replies stored in each username tweets table as well as web application user-generated tweets. The process for standardizing the text strings involves using the [re](https://docs.python.org/3/library/re.html) python library to remove all non-alphanumeric characters, encode emojis into a numeric format, and remove text information that represents HTTP links.

**Count Vectorizer**

Using scikit-learn’s [CountVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html) the text strings are converted into a tokenized sparse matrix. The vector is fitted on the tweet data of two selected usernames. The matrix represents the word counts for each word within each tweet of the two usernames. For user-generated tweets, the text is transformed on the previously fitted vector. The result is tweet information transformed in a way valid for importing into the logistic regression classification model.

**Logistic Regression**

Using scikit-learn’s [LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html) model a user-generated tweet is classified to be said by one of the two selected Twitter usernames. The logistic regression model is fit on the tweet data for each selected Twitter username. The model then aims to classify a user-generated tweet. It is found the logistic regression model has an accuracy score of 90 to 98 percent dependent on the two usernames in comparison and their most recent tweets/replies.
