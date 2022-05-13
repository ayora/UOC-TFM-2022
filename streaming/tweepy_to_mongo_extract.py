import tweepy
from tweepy.streaming import Stream
from tweepy import OAuthHandler

import pymongo
import json
import datetime
import sys
from jproperties import Properties

# #########################################################################
# Load properties

configs = Properties()
  
with open('stream.cfg', 'rb') as read_prop:
    configs.load(read_prop)
    
# MongoDB
address 	= configs.get("address").data 
port 		= int(configs.get("port").data)
username 	= configs.get("username").data
password 	= configs.get("password").data
authSource 	= configs.get("authSource").data

# Twitter API
consumer_key    = configs.get("consumer_key").data
consumer_secret = configs.get("consumer_secret").data
access_token    = configs.get("access_token").data
access_secret   = configs.get("access_secret").data


# #########################################################################
# Connection

connection =  pymongo.MongoClient(address, port, username=username, password=password, authSource=authSource)

db = connection.cryptotwitter  

collection = db.tweets_staging


class MyStreamListener(tweepy.StreamListener):

	MAX_TWEETS_TO_EXTRACT = 3000

	def on_data(self, data):

		t = json.loads(data)

		tweet_id = t['id_str']  
		username = t['user']['screen_name']  
		followers = t['user']['followers_count']  
		text = t['text']  
		full_text = t['extended_tweet']['full_text'] if 'extended_tweet' in t.keys() else ''
		hashtags = t['entities']['hashtags']  
		dt = t['created_at']  
		
		created = datetime.datetime.strptime(dt, '%a %b %d %H:%M:%S +0000 %Y')

		tweet = {'id':tweet_id, 'username':username, 'followers':followers, 'text':text, 'full_text':full_text, 'hashtags':hashtags, 'created_at':created}

		collection.insert_one(tweet)

		if self.MAX_TWEETS_TO_EXTRACT  == 1:
			sys.exit(1)
		else:
			self.MAX_TWEETS_TO_EXTRACT  -= 1

		return True

	def on_error(self, status):
		print ("Streaming error: " + status)


if __name__ == '__main__':

	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_secret)

	listener = MyStreamListener(api=tweepy.API(wait_on_rate_limit=True))

	streamer = tweepy.Stream(auth=auth, listener=listener)

	streamer.filter(track=["btc", "BTC", "bitcoin", "BITCOIN", "#btc", "#BTC"], languages=["en"])
	