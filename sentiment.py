from twython import Twython
from textblob import TextBlob
import json
import pandas as pd
import nltk
import GetOldTweets3 as got
import datetime
from langdetect import detect
from langdetect import DetectorFactory
from pymongo import MongoClient

#To enforce consistent results since langdetect is non-deterministic
DetectorFactory.seed = 0

# Load credentials from json file
with open("../twitter_credentials2.json", "r") as file:
    creds = json.load(file)

# Instantiate an object and print key and secret
#print("CONSUMER_KEY: " + creds['CONSUMER_KEY'])
#print("CONSUMER_SECRET: " + creds['CONSUMER_SECRET'])
python_tweets = Twython(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])

#Connect to DB
uri = creds['MONGODB_URI']
#print(uri)
client = MongoClient(uri)

db = client.tweetcollection

post = {"date" : "2018-09-30",
        "text" : "i like ham"}

posts = db.posts
#post_id = posts.insert_one(post).inserted_id
#print(post_id)

for testposts in posts.find():
    print(testposts)

print(posts.find_one({"_id" : "5be9f3b69b407c5144907b63"}))


# Create our query
query = {'q': 'Trump',
         'result_type': 'popular',
         'count': 2,
         'lang': 'en',
         'tweet_mode' : 'extended',
         }

# Search tweets
dict_ = {'user': [], 'date': [], 'text': [], 'favorite_count': []}
mythonTweetsReturn = python_tweets.search(**query)['statuses'];
#print(mythonTweetsReturn)
print()

listOfTweets = ""
i = 1;
for status in mythonTweetsReturn:
    tempString = str(i)
    singleTweet = status['full_text']
    singleTweet = singleTweet.replace("\n", "")
    singleTweet = singleTweet.replace("\r", "")
    listOfTweets += tempString + ": " + singleTweet
    listOfTweets += "\n"
    i = i + 1;

print(listOfTweets)

# myStuff
mytime = datetime.datetime.now()
print("Before: " + str(mytime))

tweetCriteria = got.manager.TweetCriteria().setQuerySearch('CDU').setUntil("2018-09-30").setMaxTweets(2)

for tweet in got.manager.TweetManager.getTweets(tweetCriteria):
    #b = TextBlob(str(tweet.text))
    #print(b.detect_language())
    #print(detect(tweet.text))
    print(str(tweet.date) + " : " + detect(tweet.text) + " : @" + tweet.username + ": " + tweet.text + " : " + tweet.permalink)
    #print(tweet.mentions)


print("Time neede: " + str(datetime.datetime.now()-mytime))

'''
for status in mythonTweetsReturn:
    dict_['user'].append(status['user']['screen_name'])
    dict_['date'].append(status['created_at'])
    dict_['text'].append(status['text'])
    dict_['favorite_count'].append(status['favorite_count'])

# Structure data in a pandas DataFrame for easier manipulation
df = pd.DataFrame(dict_)
df.sort_values(by='favorite_count', inplace=True, ascending=False)
df.head(5)
'''
