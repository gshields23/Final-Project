###### INSTRUCTIONS ###### 

# An outline for preparing your final project assignment is in this file.

# Below, throughout this file, you should put comments that explain exactly what you should do for each step of your project. You should specify variable names and processes to use. For example, "Use dictionary accumulation with the list you just created to create a dictionary called tag_counts, where the keys represent tags on flickr photos and the values represent frequency of times those tags occur in the list."

# You can use second person ("You should...") or first person ("I will...") or whatever is comfortable for you, as long as you are clear about what should be done.

# Some parts of the code should already be filled in when you turn this in:
# - At least 1 function which gets and caches data from 1 of your data sources, and an invocation of each of those functions to show that they work 
# - Tests at the end of your file that accord with those instructions (will test that you completed those instructions correctly!)
# - Code that creates a database file and tables as your project plan explains, such that your program can be run over and over again without error and without duplicate rows in your tables.
# - At least enough code to load data into 1 of your database tables (this should accord with your instructions/tests)

######### END INSTRUCTIONS #########

# Put all import statements you need here.
import unittest
import json
import requests
import tweepy
import collections
import sqlite3
import twitter_info


# MY INSTRUCTIONS: 

#I want to test three recent Oscar nominee movies: La La Land, Moonlight, and Lion
#For the users, I'll see which star actor from each movie has the most followers, aka who is considered most 'popular'
#For the search, I'll see the data of amount of mentions of the movies to see which is the most popular. It'd be interesting to see if 
#Moonlight and their actors win or not, because that movie was awarded Best Movie. I'd like to see a timeline of popularity boosts. 
#Originally I wanted to do this on the night of the Oscars but that won't work b/c of Twitter's time constraint
#I think this is fun because there was so much controversy over La La Land & Moonlight.

#I have successfully cached data and created databases. 
#I have the right set up for entering code into my database, but it's based off specific searches. I have 
#to figure out how I can do this for any type of movie.

# Steps of the Project:

# 1 - Write functions to get and cache data from Twitter 															- Done! 
# 2 - Write function to get and cache data from OMDB 																- Done!
# 3 - Define a class Movie - must accept a dictionary, should have 3 instance variables, 2 methods					- Done!
# 4 - Pick 3 movie title search terms of OMDB 																		- Done!
# 5 - Make a request to OMDB on each of those search terms, using your function, then accumulate in dictionary		- Done!
# 6 - Create a list of instances of class Movie (using dictionaries from OMDB request)								- 
# 7 - Use Twitter to search for one star actor in each movie,get info about each user who posted a tweet about them - 
# 8 - Create database file with 3 tables, Create queries															- **MAKE QUERIES**
# 9 - Load data into databases																						- Done!
#10 - Process data and create an output file 																		-
#11 - Write that data to a text file as a summary stats page														-
#12 - Make tests for the entire code 																				-

																												

movie_titles = ['Moonlight', 'La La Land', 'Lion']

class Movie():
	def __init__(self, diction):
		self.title = diction['Title']
		self.director = diction['Director'].split(',')[0]
		self.imdb_rating = diction['Ratings']
		self.list_actors = diction['Actors']
		self.num_langs = len(diction['Language'])
		self.actor = diction['Actors'].split(',', 1)[0]
		

	def __str__(self): #still figuring out what to do with this
		return "{} from {}".format(self.list_actors, self.title)

	def getActor(self):
		return self.actor

	def getTitle(self):
		return self.title

class Twitter():
	def __init__(self, diction):
		self.text = diction['statuses']['text']
		self.id = diction['id']
		self.user = diction['user']['name']
		self.movie = 'none'
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
		params_dict['t'] = title #this is super helpful for this project. If the title changes, it's easy to get different data
		response = requests.get('http://www.omdbapi.com/', params = params_dict)
		omdb_dict = json.loads(response.text)
		CACHE_DICTION[unique_identifier] = omdb_dict
		f=open(CACHE_FNAME, 'w')
		f.write(json.dumps(CACHE_DICTION))
		f.close()

		return omdb_dict


#TWITTER CACHING 
def getTwitterUsername(actor_username):
	unique_identifier = "twitter_{}".format(actor_username)
	if unique_identifier in CACHE_DICTION:
		print('using cached Twitter data for', actor_username)
		statuses = CACHE_DICTION[unique_identifier]
		pass
	else:
		print('getting data from Twitter for', actor_username)
		statuses = api.user_timeline(screen_name=actor_username, count = 100)
		CACHE_DICTION[unique_identifier] = statuses
		f=open(CACHE_FNAME, 'w')
		f.write(json.dumps(CACHE_DICTION))
		f.close()

	return statuses


def getTwitterMentions(title): #Here is my data for seeing all public tweets/mentions on Twitter. 
	unique_identifier = "twitter_{}".format(title)
	if unique_identifier in CACHE_DICTION:
		print('using cached Twitter data for', title)
		#twitter_results = CACHE_DICTION[unique_identifier]
		statuses = CACHE_DICTION[unique_identifier]
		pass
	else:
		print('getting data from Twitter for', title)
		statuses = api.search(q=title, count = 100) #search should sift through all public data
		CACHE_DICTION[unique_identifier] = statuses
		f=open(CACHE_FNAME, 'w')
		f.write(json.dumps(CACHE_DICTION))
		f.close()

	return statuses
	


#Code that creates a database file and tables as your project plan explains, such that your program can be run over and over again without error and without duplicate rows in your tables.

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
table += 'Movies (id TEXT PRIMARY KEY, movie_title TEXT, director TEXT, num_languages INTEGER, imdb_rating INTEGER, top_actor TEXT)'
cur.execute(table)

#TWEETS TABLE
cur.execute('DROP TABLE IF EXISTS Tweets')
table = 'CREATE TABLE IF NOT EXISTS '
table += 'Tweets (tweet TEXT, tweet_id INTEGER PRIMARY KEY, user_id TEXT NOT NULL, movie_title TEXT NOT NULL, number_favorites INTEGER, number_retweets INTEGER, FOREIGN KEY (user_id) REFERENCES Users(user_id) on UPDATE SET NULL, FOREIGN KEY (movie_title) REFERENCES Movies(movie_title) on UPDATE SET NULL)'
cur.execute(table)


#OMDB DATA - doesn't work
movieinfo = []
id = []
title = []
director = []
num_langs = []
imdb_rating = []
firstactor = []
for movie in movie_titles:
	x = Movie(getdata_omdb(movie))
	movieinfo.append(x)

# id.append(diction['imdbID'])
# title.append(diction['Title'])
# director.append(diction['Director'])
# num_langs.append(len(diction['Language']))
# imdb_rating.append(diction['imdbRating'])
# firstactor.append(diction['Actors'].split(',', 1)[0]) #I had to do this to get the first full name listed

omdb_zip = zip(id, title, director, num_langs, imdb_rating, firstactor)
omdb_list = list(omdb_zip)


for movie_info in omdb_list:
	y = 'INSERT OR IGNORE INTO Movies VALUES (?,?,?,?,?,?)'
	cur.execute(y, movie_info)

#TWEETS DATA - works
# twitterinfo = []
tweets_text = []
tweets_id = []
tweets_user = []
tweets_movie = []
tweets_numfavs = []
tweets_numrt = []

for movie in movie_titles:
	twitobject = getTwitterMentions(movie)
	for lst in twitobject['statuses']:
		tweets_text.append((lst['text']))
		tweets_id.append(lst['id'])
		tweets_user.append(lst['user']['name'])
		tweets_numfavs.append(lst['user']['favourites_count'])
		tweets_numrt.append(lst['retweet_count'])
		if 'Moonlight' in lst['text']:
			tweets_movie.append('Moonlight')
		if 'Lion' in lst['text']:
			tweets_movie.append('Lion')
		if 'La La Land' in lst['text']:
			tweets_movie.append('La La Land')


tweets_list = list(zip(tweets_text, tweets_id, tweets_user, tweets_movie, tweets_numfavs, tweets_numrt))

# print(twitobject)

for info in tweets_list:
	y = 'INSERT OR IGNORE INTO Tweets VALUES (?,?,?,?,?,?)'
	cur.execute(y, info)


# USERS DATA 

users_userid = []
users_screenname = []
users_favs = []
users_followers = []

# for users in tweets_list:
# 	users_userid.append(tweets_list['user']['id_str'])
# 	users_screenname.append(tweets_list['user']['screen_name'])
# 	users_favs.append(tweets_list['user']['favourites_count'])
# 	users_followers.append(tweets_list['user']['followers_count']) #I added this to see which actor would have the most followers

# tweets_list = list(zip(tweets_text, tweets_id, tweets_user, tweets_movie, tweets_numfavs, tweets_numrt))

# for info in tweets_list:
# 	y = 'INSERT OR IGNORE INTO Tweets VALUES (?,?,?,?,?,?)'
# 	cur.execute(y, info)

conn.commit()




#QUERIES
x = 'SELECT * FROM Tweets WHERE number_favorites > 5'
cur.execute(x)
total = cur.fetchall()
num_of_users = len(total) #287


# #CREATING A CSV FILE
outfile = open('finalproject.csv', 'w')
outfile.write('\n')
outfile.write('data')

# f = open('file.txt','w')
# a = input('final project')
# f.close()


# for x in possible_airports:
#     try:
#         outfile.write('{}, {}, {}, {}\n'.format(*extract_airport_data(x)))

#     except:
#         print "Failed for airport " + x



conn.close()

#Tests at the end of your file that accord with those instructions (will test that you completed those instructions correctly!)
# class Tests(unittest.TestCase):
# 	def test1(self): #tests that there are 6 rows in the Tweets table
# 		conn = sqlite3.connect('final_project.db') 
# 		cur = conn.cursor()
# 		cur.execute('SELECT * FROM Tweets');
# 		result = cur.fetchall()
# 		self.assertTrue(len(result[0])==6)
# 		conn.close()

# 	def test2(self): #tests that there are 4 rows in the Users table
# 		conn = sqlite3.connect('final_project.db')
# 		cur = conn.cursor()
# 		cur.execute('SELECT * FROM Users');
# 		result = cur.fetchall()
# 		self.assertTrue(len(result[0])==4)
# 		conn.close()
	
# 	def test3(self): #tests that there are 6 rows in the Movies table
# 		conn = sqlite3.connect('final_project.db')
# 		cur = conn.cursor()
# 		cur.execute('SELECT * FROM Movies');
# 		result = cur.fetchall()
# 		self.assertTrue(len(result[0])==6)
# 		conn.close()

# 	def test4(self): #tests that first actor returns one string, the full name of an actor
# 		self.assertEqual(len(firstactor), 1)

# 	def test5(self): #tests that the Movie id is a string instead of an integer (I had an issue with this where I expected it to be an integer and it wasn't!)
# 	 	self.assertEqual(type(id[0]),type(""))

# 	def test6(self): #tests that my list for OMBD is indeed a list
# 		self.assertEqual(type(omdb_list),type([]))

# 	def test7(self):
# 		self.assertEqual(type(mentions_list), type([]))

# 	def test8(self): 
# 		self.assertEqual(type(user_list),type([]))



	# def test6(self): #tests that get_rating returns an integer
	# 	self.assertEqual(type(get_rating()), type(int))

	# def test7(self): #tests that get_director returns a string
	# 	self.assertEqual(type(get_director()), type(""))

	# def test8(self): #tests that get_title returns a string
	# 	self.assertEqual(type(get_title()), type(""))
 
	# def test9(self): #tests that input of class Movie is a dictionary
	# 	self.assertEqual(type(Movie()), type({}))

	# def test10(self): #tests that get_actors returns a list 
	# 	self.assertEqual(type(get_actors()), type([]))

	# def test11(self): #tests that get_langs returns an integer
	# 	self.assertEqual(type(get_langs()), type(int))

	# def test12(self): #tests that the list that get_actors contains strings
	# 	self.assertEqual(type(test10[0],type(["Emma Stone", "Ryan Gosling"])))

    
             