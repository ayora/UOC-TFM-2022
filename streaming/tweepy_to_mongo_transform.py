import pymongo
import datetime
import json
import re

from textblob import TextBlob
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


# #########################################################################
# Connection
connection =  pymongo.MongoClient(address, port, username=username, password=password, authSource=authSource)

db = connection.cryptotwitter  

collection_ori = db.tweets_staging
collection_dest = db.tweets


def cleanTweetText(text):
	text = re.sub(r"@[A-Za-z0-9]+", "", text) # se eliminan menciones @
	text = re.sub("https?://[A-Za-z0-9./]+", "", text) # se eliminan URLs 
	text = re.sub(r"[^\x00-\x7F]+", "", text) # se eliminan emoticonos
	return re.sub("[^A-Za-z0-9 ]", "", text) # se eliminan signos de puntuacion
	

def sentimentAnalyst(text):
	text = cleanTweetText(text)

	value = TextBlob(text).sentiment.polarity

	if value > 0: 
		return 1 # 'positive'
	elif value < 0: 
		return -1 # 'negative'
	else: 
		return 0 # 'neutral'

# #########################################################################
# Reading tweets

tweets = []

try:
	
	tweets = collection_ori.find()

	print ("\n Gathering all data from tweets_staging collection... \n")

except Exception as e:
        print (str(e))


# #########################################################################
# Transform tweets

for tweet in tweets:

	# ########################################################
	if tweet["full_text"] != '':
		tweet["text"] = tweet["full_text"]

	tweet.pop("full_text")


	# ########################################################
	hashtags = set()
	for hashtag in tweet["hashtags"]:
		hashtags.add(hashtag["text"].lower())

	tweet["hashtags"] = list(hashtags)

	cryptos = set()
	if 'bitcoin' in hashtags or 'btc' in hashtags:
		cryptos.add('BTC')


	# ########################################################
	words = tweet["text"].split(" ")

	for word in words:
		if re.match(r'(\$)[a-zA-Z]*$', word):
			next_crypto = re.sub(r'[^\w]', '', word.upper())

			cryptos.add(next_crypto)

	tweet["cryptos"] = list(cryptos)


	# ########################################################
	# Sentiment Analyst
	polarity = sentimentAnalyst(tweet["text"])

	tweet["polarity"] = polarity


	# ########################################################
	# Loading tweets
	try:
	
		collection_dest.insert_one(tweet)

		# Deleting origin tweets
		collection_ori.delete_one({'_id': tweet["_id"]})

	except Exception as e:
	        print (str(e))

print ("\n Processed all data from tweets_staging collection. \n")
