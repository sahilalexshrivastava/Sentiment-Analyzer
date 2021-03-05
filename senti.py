import nltk
import re
import tweepy
import numpy as np
import pandas as pd
from textblob import TextBlob
import pandas as pd
from datetime import datetime
import sqlite3
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')
def clean_text(text):
    text = re.sub(r'@[A-Za-z0-9]+', '', text)
    text = re.sub(r'#', '', text)
    text = re.sub(r'RT[\s]+', '', text)
    text = re.sub(r'https?:\/\/\S+', '', text)
    return text

def sentiment(text):
    sia = SentimentIntensityAnalyzer()
    score = sia.polarity_scores(text)
    compound = score['compound']
  
    if compound>0:
        tag = 'pos'
        return tag
    elif compound<0:
        tag = 'neg'
        return tag
    else:
        tag = 'neu'
        return tag

def tweets(hashtag):
    pd.set_option('display.max_colwidth', -1)
    consumer_key = 'XzCRnnff5MJtxoY33tgWddRZ6'
    consumer_secret = '75yXXC9hrQ4gPoTrfheeGhdgBUZGsM4JTQV07hZKAhT1QGnZ3j'

    access_token = '1911808627-W7HyrD9OAKIj3EHyQU80ZT0FwEpEsZhZ9MwyXhZ'
    access_token_secret = 'SrCpAu5pEoM0dYjrDfGZ5xurhHgjSMFrsdVZuhZQvXKdj'

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True)

    public_tweets = tweepy.Cursor(api.search, q=hashtag, lang="en", tweet_mode='extended').items(50)
    
    df = pd.DataFrame([tweet.full_text for tweet in public_tweets], columns=['Tweets'])
    df['Tweets'] = df['Tweets'].apply(clean_text)
    df['Sentiments'] = df['Tweets'].apply(sentiment)
    
    s = df['Sentiments'].value_counts()[df['Sentiments'].value_counts() == df['Sentiments'].value_counts().max()]
    s1 = s.index
    
    return s1, df
    
from flask import Flask,request,render_template
import pickle

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template("login.html")
database={'sahil':'123','james':'aac','karthik':'asdsf'}

@app.route('/form_login',methods=['POST','GET'])
def login():
    name1=request.form['username']
    pwd=request.form['password']
    if name1 not in database:
	    return render_template('login.html',info='Invalid User')
    else:
        if database[name1]!=pwd:
            return render_template('login.html',info='Invalid Password')
        else:
	         return render_template('home.html',name=name1)
             

@app.route('/post_hashtag',methods=['POST','GET'])
def get_sentiment():
    pd.set_option('display.max_colwidth', -1)
    i=0
    name2 = request.form['hashtag']
    hs = '#'
    tag = hs + name2
    senti, data = tweets(tag)
    one = data.iloc[0]['Tweets']
    two = data.iloc[1]['Tweets']
    three = data.iloc[2]['Tweets']
    four = data.iloc[3]['Tweets']
    five = data.iloc[4]['Tweets']
    sentiment = senti.values
    dt = datetime.now()
    final = senti.values[0]
    if senti.values[0] == 'neg':
        final = 'negative'
    elif senti.values[0] == 'pos':
        final = 'positive'
    else: 
        final = 'neutral'
    dt_string = dt.strftime("%d/%m/%Y %H:%M:%S")
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    c.execute("insert into sent (hashtag, sentiment, time) values (?, ?, ?)",(name2, final, dt_string))
    for row in c.execute("SELECT * FROM sent"):
        print(row)
    conn.commit()
    conn.close()
    print(data.head())
    return render_template('home.html',hashtag=final ,value = name2, date = dt_string,one = one,two = two, three = three, four = four, five = five, total = data.shape[0])
if __name__ == '__main__':
    app.run()
    
#senti = tweets("#india")
#print(senti.values)
