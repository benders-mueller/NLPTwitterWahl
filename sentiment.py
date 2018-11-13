from twython import Twython
from textblob_de import TextBlobDE as TextBlobDE
from textblob import TextBlob
import json
import pandas as pd
import nltk
import GetOldTweets3 as got
import datetime
from langdetect import detect
from langdetect import DetectorFactory
from pymongo import MongoClient

# To enforce consistent results since langdetect is non-deterministic
DetectorFactory.seed = 0

# Load credentials from json file
with open("../twitter_credentials2.json", "r") as file:
    creds = json.load(file)

# Instantiate an object and print key and secret
# print("CONSUMER_KEY: " + creds['CONSUMER_KEY'])
# print("CONSUMER_SECRET: " + creds['CONSUMER_SECRET'])
python_tweets = Twython(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])

# collection of all tweets from DB and storing it back into the DB
dic = {}

# Connect to DB
uri = creds['MONGODB_URI']
# print(uri)
client = MongoClient(uri)

db = client.tweetcollection

posts = db.posts
# post_id = posts.insert_one(post).inserted_id
# print(post_id)

for tweetsDB in posts.find():
    if tweetsDB["id"] in dic:
        continue

    dic[tweetsDB["id"]] = {"id": tweetsDB["id"],
                           "formatted_date": tweetsDB["formatted_date"],
                           "username": tweetsDB["username"],
                           "text": tweetsDB["text"],
                           "author_id": tweetsDB["author_id"],
                           "favorites": tweetsDB["favorites"],
                           "date": tweetsDB["date"],
                           "geo": tweetsDB["geo"],
                           "hashtags": tweetsDB["hashtags"],
                           "mentions": tweetsDB["mentions"],
                           "permalink": tweetsDB["permalink"],
                           "retweets": tweetsDB["retweets"],
                           "to": tweetsDB["to"],
                           "urls": tweetsDB["urls"],
                           "language": tweetsDB["language"],
                           "subjectivity": tweetsDB["subjectivity"],
                           "polarity": tweetsDB["polarity"]}

    print(tweetsDB)

dicInDB = dic.copy()

# print(posts.find_one({"_id" : "5be9f3b69b407c5144907b63"}))

# Create our query
query = {'q': 'Trump',
         'result_type': 'popular',
         'count': 2,
         'lang': 'en',
         'tweet_mode': 'extended',
         }

# Search tweets
dict_ = {'user': [], 'date': [], 'text': [], 'favorite_count': []}
mythonTweetsReturn = python_tweets.search(**query)['statuses'];
# print(mythonTweetsReturn)
print()

'''
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
'''

# myStuff
mytime = datetime.datetime.now()
print("Before downloading new tweets: " + str(mytime))

today = datetime.datetime.today().strftime('%Y-%m-%d')
tweetCriteria = got.manager.TweetCriteria().setQuerySearch('CDU').setUntil("2018-12-07").setMaxTweets(5)
tweetCollection = got.manager.TweetManager.getTweets(tweetCriteria)

for tweet in tweetCollection:
 #raw unfilted tweets
    print(str(tweet.date) + " : " + detect(tweet.text) + " ID: " + tweet.id + " : @" + tweet.username + ": " + tweet.text + " : " + tweet.permalink)

print("Time needed for downloading new tweets: " + str(datetime.datetime.now() - mytime) + "\n")

for tweet in tweetCollection:
    resultLanguage = detect(tweet.text)

    if tweet.id in dic or resultLanguage != "de":
        continue

    # perform sentiment analysis
    blob = TextBlob(tweet.text)
    result = blob.sentiment

    dic[tweet.id] = {"id": tweet.id,
                     "formatted_date": tweet.formatted_date,
                     "username": tweet.username,
                     "text": tweet.text,
                     "author_id": tweet.author_id,
                     "favorites": tweet.favorites,
                     "date": tweet.date,
                     "geo": tweet.geo,
                     "hashtags": tweet.hashtags,
                     "mentions": tweet.mentions,
                     "permalink": tweet.permalink,
                     "retweets": tweet.retweets,
                     "to": tweet.to,
                     "urls": tweet.urls,
                     "language": resultLanguage,
                     "subjectivity": result[1],
                     "polarity": result[0]}

for key, value in dic.items():
    #print(value)
    print(value)
    # print(value['text'])



#print(dic)

print("Filtered dic, only new tweets remain: ")
for key, value in dicInDB.items():
    if key in dic:
        del dic[key]

for key, value in dic.items():
    print(value)

print("Filtering of dic done.")

# result2 = posts.insert_many(dic.values())
# print(result2.inserted_ids)

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
