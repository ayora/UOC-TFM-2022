from flask import Flask, render_template

from flask_pymongo import PyMongo

from datetime import date, datetime, timedelta

# ############################################################################

app = Flask(__name__, static_folder='static', static_url_path='')

app.config.from_pyfile('cryptowebapp.cfg')

if app.config['ENV'] == 'development':
	app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

mongo = PyMongo(app)


@app.template_filter('format_porcentage')
def format_porcentage(number):
	return f'{round(number * 100.0, 2):,}'+'%'


# ############################################################################

@app.route('/', defaults={'time': None})
@app.route('/<int:time>')
def home(time):

	if time is None:
		date = datetime.now() - timedelta(days=1)
	else:
		date = datetime.now() - timedelta(days=time)

	# twitter users more active
	pipeline = [
				{ '$match': { "followers": { '$gt': 0}, 'created_at': { '$gte': date } } },
				{ '$group': { '_id': { 'username': "$username", 'followers': "$followers" }, 'count': {'$sum':1} } },
				{ '$sort': { 'count':-1, '_id.followers':-1 }},
				{ '$limit': 10 }
				]

	result = mongo.db.tweets.aggregate(pipeline)

	twitter_users_active = list(result)

	# cryptos more tweeted
	pipeline = [
				{ '$unwind': '$cryptos' },
				{ '$match': { "followers": { '$gt': 0}, 'created_at': { '$gte': date } } },
				{ '$group': { 
					'_id': {
						'crypto': "$cryptos"}, 
						'count': {'$sum':1}, 
						'positive_polarity': { '$sum' : { '$cond': [ { '$gt': [ '$polarity' , 0 ] }, 1, 0 ] } }, 
						'neutral_polarity': { '$sum' : { '$cond': [ { '$eq': [ '$polarity' , 0 ] }, 1, 0 ] } },
						'negative_polarity': { '$sum' : { '$cond': [ { '$lt': [ '$polarity' , 0 ] }, 1, 0 ] } } 
					} 
				},
				{ '$sort': {'count':-1, 'positive_polarity':-1, 'neutral_polarity':-1} },
				{ '$limit': 10 }
			]

	result = mongo.db.tweets.aggregate(pipeline)

	cryptos_tweeted = list(result)

	# hastags more tweeted
	pipeline = [
				{ '$unwind': '$hashtags' },
				{ '$match': { "followers": { '$gt': 0}, 'created_at': { '$gte': date } } },
				{ '$group': { 
					'_id': {
						'hashtag': "$hashtags"}, 
						'count': {'$sum':1}, 
						'positive_polarity': { '$sum' : { '$cond': [ { '$gt': [ '$polarity' , 0 ] }, 1, 0 ] } }, 
						'neutral_polarity': { '$sum' : { '$cond': [ { '$eq': [ '$polarity' , 0 ] }, 1, 0 ] } },
						'negative_polarity': { '$sum' : { '$cond': [ { '$lt': [ '$polarity' , 0 ] }, 1, 0 ] } } 
					} 
				},
				{ '$sort': {'count':-1, 'positive_polarity':-1, 'neutral_polarity': -1} },
				{ '$limit': 10 }
			]

	result = mongo.db.tweets.aggregate(pipeline)

	hashtags_tweeted = list(result)

	# search for new cryptos
	pipeline = [
				{ '$unwind': '$cryptos' },
				{ '$match': { "followers": { '$gt': 0}, 'created_at': { '$gte': date } } },
				{ '$group': { 
					'_id': {'crypto': "$cryptos"}
					} 
				}
			]

	result = mongo.db.tweets.aggregate(pipeline)

	cryptos_after_limit = list(result)

	pipeline = [
				{ '$unwind': '$cryptos' },
				{ '$match': { "followers": { '$gt': 0}, 'created_at': { '$lt': date } } },
				{ '$group': { 
					'_id': {'crypto': "$cryptos"}
					} 
				}
			]

	result = mongo.db.tweets.aggregate(pipeline)

	cryptos_before_limit = list(result)

	old_cryptos = []
	for c in cryptos_before_limit:
		old_cryptos.append(c['_id'])

	new_cryptos = [ crypto for crypto in cryptos_after_limit if crypto['_id'] not in old_cryptos ]

	return render_template('index.html', 
		time=time,
		twitter_users=twitter_users_active, 
		cryptos_tweeted=cryptos_tweeted, 
		hashtags_tweeted=hashtags_tweeted,
		new_cryptos=new_cryptos[0:10])



