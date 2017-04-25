# Put all import statements you need here.
import unittest
import json
import requests
import tweepy
from collections import Counter
import sqlite3
import twitter_info
import re
																								

movie_titles = ['Moonlight', 'La La Land', 'Lion']

class Movie():
	def __init__(self, diction):
		self.id = diction['imdbID']
		self.title = diction['Title']
		self.director = diction['Director'].split(',')[0]
		self.imdb_rating = diction['Ratings']
		self.list_actors = diction['Actors']
		self.num_langs = len(diction['Language'])
		self.actor = diction['Actors'].split(',', 1)[0]
		self.awards = diction['Awards']
		
	def __str__(self):
		return "{} = {}".format(self.title, self.awards) 


	def getActor(self):
		return self.actor

	def getTitle(self):
		return self.title

	def getDatabaseInfo(self):
		rating = self.imdb_rating[0]['Value']
		rating = float(rating.split('/')[0])
		return (self.id, self.title, self.director, rating, self.list_actors, self.num_langs, self.actor, self.awards)

class Twitter():
	def __init__(self, diction):
		self.text = diction['statuses']['text']
		self.id = diction['id']
		self.user = diction['user']['name']
		self.favorites = diction['user']['favourites_count']
		self.retweets = diction['retweet_count']
		self.userid = diction['user']['id_str']
		self.screenname = diction['user']['screen_name']
		self.followers = diction['user']['followers_count']


#TWITTER SET UP CODE - below is my set up for Twitter caching.
consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

CACHE_FNAME = "206finalproject_cache.json" #This creates the file where all my cached data is stored
try:
	cache_file = open(CACHE_FNAME,'r')
	cache_contents = cache_file.read()
	cache_file.close()
	CACHE_DICTION = json.loads(cache_contents)
except:
	CACHE_DICTION = {}

#OMDB CACHING  
def getdata_omdb(title):
	unique_identifier = "omdb_{}".format(title)

	if unique_identifier in CACHE_DICTION:
		print('using cached OMDB data for', title)
		omdb_dict = CACHE_DICTION[unique_identifier]
		return omdb_dict

	else:
		print('getting data from IMDB for', title)
		params_dict = {}
		params_dict['t'] = title 
		response = requests.get('http://www.omdbapi.com/', params = params_dict)
		omdb_dict = json.loads(response.text)
		CACHE_DICTION[unique_identifier] = omdb_dict
		f=open(CACHE_FNAME, 'w')
		f.write(json.dumps(CACHE_DICTION))
		f.close()

		return omdb_dict


#TWITTER CACHING 
def getTwitterUsername(user):
	unique_identifier = "twitter_{}".format(user)
	if unique_identifier in CACHE_DICTION:
		print('using cached Twitter data for', user)
		statuses = CACHE_DICTION[unique_identifier]
		pass
	else:
		print('getting data from Twitter for', user)	
		statuses = api.get_user(id=user)
		CACHE_DICTION[unique_identifier] = statuses
		f=open(CACHE_FNAME, 'w')
		f.write(json.dumps(CACHE_DICTION))
		f.close()
	
	return statuses


def getTwitterMentions(title): #Here is my data for seeing all public tweets/mentions on Twitter. 
	unique_identifier = "twitter_{}".format(title)
	if unique_identifier in CACHE_DICTION:
		print('using cached Twitter data for', title)
		statuses = CACHE_DICTION[unique_identifier]
		pass
	else:
		print('getting data from Twitter for', title)
		statuses = api.search(q=title, count = 20) 
		CACHE_DICTION[unique_identifier] = statuses
		f=open(CACHE_FNAME, 'w')
		f.write(json.dumps(CACHE_DICTION))
		f.close()

	return statuses
	

#DATABASE
conn = sqlite3.connect('final_project.db')
cur = conn.cursor()


#USERS TABLE
cur.execute('DROP TABLE IF EXISTS Users')
table = 'CREATE TABLE IF NOT EXISTS '
table += 'Users (user_id INTEGER PRIMARY KEY, user_screenname TEXT, num_favs INTEGER, followers INTEGER)'
cur.execute(table)

#MOVIES TABLE
cur.execute('DROP TABLE IF EXISTS Movies')
table = 'CREATE TABLE IF NOT EXISTS '
table += 'Movies (id TEXT PRIMARY KEY, movie_title TEXT, director TEXT, num_languages INTEGER, imdb_rating INTEGER, top_actor TEXT, awards TEXT)'
cur.execute(table)

#TWEETS TABLE
cur.execute('DROP TABLE IF EXISTS Tweets')
table = 'CREATE TABLE IF NOT EXISTS '
table += 'Tweets (tweet TEXT, tweet_id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, movie_title TEXT NOT NULL, number_favorites INTEGER, number_retweets INTEGER, FOREIGN KEY (user_id) REFERENCES Users(user_id) on UPDATE SET NULL, FOREIGN KEY (movie_title) REFERENCES Movies(movie_title) on UPDATE SET NULL)'
cur.execute(table)


#OMDB DATA 
movieinfo = []
id = []
title = []
director = []
num_langs = []
imdb_rating = []
firstactor = []
awards = []


for movie in movie_titles:
	current_movie = Movie(getdata_omdb(movie))
	movieinfo.append(current_movie)
	movie_tup = current_movie.getDatabaseInfo()

	id.append(movie_tup[0])
	title.append(movie_tup[1])
	director.append(movie_tup[2])
	num_langs.append(movie_tup[5])
	imdb_rating.append(movie_tup[3])
	firstactor.append(movie_tup[6])
	awards.append(movie_tup[7])

	omdb_zip = zip(id, title, director, num_langs, imdb_rating, firstactor, awards)
	omdb_list = list(omdb_zip)


	for movie_info in omdb_list:
		y = 'INSERT OR IGNORE INTO Movies VALUES (?,?,?,?,?,?,?)'
		cur.execute(y, movie_info)


#TWEETS DATA
tweets_text = []
tweets_id = []
tweets_user = []
tweets_movie = []
tweets_numfavs = []
tweets_numrt = []

twitter_users = []

for movie in movie_titles:
	twitobject = getTwitterMentions(movie)
	for lst in twitobject['statuses']:
		tweets_text.append((lst['text']))
		tweets_movie.append(movie)
		tweets_id.append(lst['id'])
		tweets_user.append(lst['user']['id'])
		tweets_numfavs.append(lst['user']['favourites_count'])
		tweets_numrt.append(lst['retweet_count'])
	
		userId = lst['user']['id']
		if userId not in twitter_users:
			twitter_users.append(userId)

		if lst['entities']['user_mentions'] != "":
			for x in lst['entities']['user_mentions']:
				if x['id'] not in twitter_users:
					twitter_users.append(x['id'])


tweets_list = list(zip(tweets_text, tweets_id, tweets_user, tweets_movie, tweets_numfavs, tweets_numrt))

for info in tweets_list:
	y = 'INSERT OR IGNORE INTO Tweets VALUES (?,?,?,?,?,?)'
	cur.execute(y, info)


# USERS DATA 
users_userid = []
users_screenname = []
users_favs = []
users_followers = []

for user in twitter_users:
	userobj = getTwitterUsername(user)
	users_userid.append(userobj['id'])
	users_screenname.append(userobj['screen_name'])		
	users_favs.append(userobj['favourites_count'])
	if 'status' in userobj:	
		users_followers.append(userobj['status']['retweet_count'])
	else:
		users_followers.append(0)

users_lst = list(zip(users_userid, users_screenname, users_favs, users_followers))

for info in users_lst:
	y = 'INSERT OR IGNORE INTO Users VALUES (?,?,?,?)'
	cur.execute(y, info)

conn.commit()

#QUERIES

#QUERY 1 - sort function, most retweets
x = 'SELECT SUM(Tweets.number_retweets), Tweets.movie_title FROM Tweets GROUP BY movie_title'
cur.execute(x)
movie_rt = cur.fetchall()
sorted_retweets = sorted(movie_rt, reverse = True)


#QUERY 2 
y = 'SELECT SUM(Users.num_favs), Tweets.movie_title FROM Users INNER JOIN Tweets GROUP BY movie_title'
cur.execute(y)
favs_users = cur.fetchall()
sorted_favorites = sorted(favs_users, reverse = True)


#QUERY 3 - reg ex
z = 'SELECT SUM(Tweets.number_retweets), Movies.movie_title, Movies.awards FROM Movies INNER JOIN Tweets ON Tweets.movie_title = Movies.movie_title GROUP BY Tweets.movie_title'
cur.execute(z)
lst_awards = cur.fetchall()
for x in lst_awards:
	regex_z = r"(?:Won).[0-9]"
	sep_awards = re.findall(regex_z, x[2])
	output = '{}, {}'.format(x[1], sep_awards)


#QUERY 4
a = 'SELECT Movies.movie_title, Tweets.number_retweets FROM Tweets INNER JOIN Movies ON Tweets.movie_title = Movies.movie_title WHERE Tweets.number_retweets > 1000'
cur.execute(a)
movieRT_lst = cur.fetchall()

x = [element[0] for element in movieRT_lst]
c = Counter(x)


# #CREATING A TXT FILE
outfile = open('finalproject.txt', 'w')
outfile.write("\n                      Summary Statistics for Movies & Twitter \n")
outfile.write("\nThe 2017 Oscars spiked controversy when 'Moonlight' took home Best Film, even though 'La La Land' was mistakenly announced first as the winner. People around the world argued for what they felt was the better movie. I decided to look at Twitter data for 'La La Land,' 'Moonlight,' and 'Lion' to see which movie spiked the most discussion online, for better or for worse. \n")

#awards
outfile.write("\nDATA FOR MOVIES AND OSCAR AWARDS:\n")
z = 'SELECT SUM(Tweets.number_retweets), Movies.movie_title, Movies.awards FROM Movies INNER JOIN Tweets ON Tweets.movie_title = Movies.movie_title GROUP BY Tweets.movie_title'
cur.execute(z)
lst_awards = cur.fetchall()
for x in lst_awards:
	regex_z = r"(?:Won).[0-9]"
	sep_awards = re.findall(regex_z, x[2])
	output = '{}, {}'.format(x[1], sep_awards)
	outfile.write("\n")
	outfile.write(output) 
outfile.write("\n(Empty brackets signify that no Oscar awards were given.)\n \n \n")

#retweets
outfile.write("DATA FOR MOVIES AND RETWEETS ON TWITTER:\n")
outfile.write("\nWhen looking at which movie's tweets had the most amount of retweets on Twitter, ")
outfile.write(str(sorted_retweets[0][1]))
outfile.write(" had the most amount of retweets with ")
outfile.write(str(sorted_retweets[0][0]))
outfile.write(" retweets in total. This implies that this movie has the most popularity on Twitter. \n \n")

#favorites
outfile.write("DATA FOR MOVIES AND FAVORITES ON TWITTER:\n")
outfile.write("\nWhen looking at which user discussing which movie had the most amount of favorites on Twitter, users who discussed ")
outfile.write(str(sorted_favorites[0][1]))
outfile.write(" had favorited the most amount of tweets with ")
outfile.write(str(sorted_favorites[0][0]))
outfile.write(" favorites in total. This implies that this movie's users are the most active on Twitter. \n \n")

outfile.write("The following data displays the movie title and how many tweets (discussing that movie) were retweeted more than 1000 times: \n")
outfile.write(str(c))
outfile.write("\n \n \n")

outfile.write("This data may prove that Twitter users disagree with the Academy on which movie deserves Best Film.")

outfile.close()

conn.close()

#Tests at the end of your file that accord with those instructions (will test that you completed those instructions correctly!)
class Tests(unittest.TestCase):
	def test_1(self): #tests that there are 6 rows in the Tweets table
		conn = sqlite3.connect('final_project.db') 
		cur = conn.cursor()
		cur.execute('SELECT * FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(len(result[0])==6)
		conn.close()

	def test_2(self): #tests that there are 4 rows in the Users table
		conn = sqlite3.connect('final_project.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result[0])==4)
		conn.close()
	
	def test_3(self): #tests that there are 7 rows in the Movies table
		conn = sqlite3.connect('final_project.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Movies');
		result = cur.fetchall()
		self.assertTrue(len(result[0])==7)
		conn.close()

	def test_4(self): #tests that the Movie id is a string instead of an integer (I had an issue with this where I expected it to be an integer and it wasn't!)
	 	self.assertEqual(type(id[0]),type(""))

	def test_5(self): #tests that my list for OMBD is indeed a list
		self.assertEqual(type(omdb_list),type([]))

	def test_6(self):
		m = Movie(getdata_omdb('La La Land'))
		self.assertEqual(len(m.getDatabaseInfo()), 8)

	def test_7(self):
		m = Movie(getdata_omdb('La La Land'))
		self.assertEqual(type(m.getTitle()), type(""))

	def test_8(self): 
		m = Movie(getdata_omdb('La La Land'))
		self.assertEqual(type(m.getDatabaseInfo()), type((1,2,3)))
 
	def test_9(self): 
		m = Movie(getdata_omdb('Moonlight'))
		self.assertEqual(type(m.id), type(""))

	def testb(self):
		m = Movie(getdata_omdb('Lion'))
		self.assertEqual(type(m.__str__().split()), type([]))

	def testc(self):
		self.assertEqual(type(sorted_favorites), type([]))

	def testd(self):
		self.assertEqual(type(sorted_retweets), type([]))

	def teste(self):
		self.assertEqual(type(output), type(""))

	def testf(self):
		self.assertEqual(type(x), type((1,2,3)))

	def testg(self):
		x = getdata_omdb('La La Land')
		self.assertEqual(type(x), type({}))

	def testg(self):
		x = getTwitterUsername('La La Land')
		self.assertEqual(type(x), type({}))

	def testg(self):
		x = getTwitterMentions('La La Land')
		self.assertEqual(type(x), type({}))


if __name__ == "__main__":
	unittest.main(verbosity=2)



