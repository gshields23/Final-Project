###### INSTRUCTIONS ###### 

# An outline for preparing your final project assignment is in this file.

# Below, throughout this file, you should put comments that explain exactly what you should do for each step of your project. You should specify variable names and processes to use. For example, "Use dictionary accumulation with the list you just created to create a dictionary called tag_counts, where the keys represent tags on flickr photos and the values represent frequency of times those tags occur in the list."

# You can use second person ("You should...") or first person ("I will...") or whatever is comfortable for you, as long as you are clear about what should be done.

# Some parts of the code should already be filled in when you turn this in:
# - At least 1 function which gets and caches data from 1 of your data sources, and an invocation of each of those functions to show that they work 
# - Tests at the end of your file that accord with those instructions (will test that you completed those instructions correctly!)
# - Code that creates a database file and tables as your project plan explains, such that your program can be run over and over again without error and without duplicate rows in your tables.
# - At least enough code to load data into 1 of your dtabase tables (this should accord with your instructions/tests)

######### END INSTRUCTIONS #########

# Put all import statements you need here.
import unittest
import json
import requests
import tweepy
import collections
import sqlite3
import twitter_info

# Begin filling in instructions....

#I want to test three recent Oscar nominee movies: La La Land, Moonlight, and Lion
#For the users, I'll see who has the most favorites/retweets 
#For the search, I'll see the data of amount of mentions of the movies during the actual Oscar night
#Time constraint???

#At least 1 function which gets and caches data from 1 of your data sources, and an invocation of each of those functions to show that they work 

#TWITTER SET UP CODE
consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

CACHE_FNAME = "finalproject_cache.json"
try:
	cache_file = open(CACHE_FNAME,'r')
	cache_contents = cache_file.read()
	cache_file.close()
	CACHE_DICTION = json.loads(cache_contents)
except:
	CACHE_DICTION = {}

#TWITTER API
def getTwitterUsername(actor_username):
	unique_identifier = "twitter_{}".format(username)
	if unique_identifier in CACHE_DICTION:
		print('using cached data for', username)
		#twitter_results = CACHE_DICTION[unique_identifier]
		statuses = CACHE_DICTION[unique_identifier]
		pass
	else:
		print('getting data from internet for', username)
		#twitter_results = api.user_timeline(id = username)
		statuses = api.GetUserTimeline(screen_name=actor_username, count = 50) #how to get username from the actors listed in the dictionary???
		CACHE_DICTION[unique_identifier] = twitter_results
		f=open(CACHE_FNAME, 'w')
		f.write(json.dumps(CACHE_DICTION))
		f.close()

	#return CACHE_DICTION[unique_identifier]
	
	return statuses

def getTwitterMentions(title):
	unique_identifier = "twitter_{}".format(username)
	if unique_identifier in CACHE_DICTION:
		print('using cached data for', username)
		#twitter_results = CACHE_DICTION[unique_identifier]
		statuses = CACHE_DICTION[unique_identifier]
		pass
	else:
		print('getting data from internet for', username)
		#twitter_results = api.user_timeline(id = username)
		statuses = api.GetUserTimeline(screen_name=title, count = 50) #WHAT DO I DO FOR MENTIONS
		CACHE_DICTION[unique_identifier] = twitter_results
		f=open(CACHE_FNAME, 'w')
		f.write(json.dumps(CACHE_DICTION))
		f.close()

	#return CACHE_DICTION[unique_identifier]
	return statuses
	

getTwitterMentions('La La Land')

#OMDB CACHING
# r = request.get(url)
# json.text = r.text
# dict = json.loads(json.text)

# dict['Title'] = 'La La Land'


#Code that creates a database file and tables as your project plan explains, such that your program can be run over and over again without error and without duplicate rows in your tables.

conn = sqlite3.connect('finalproject.db')
cur = conn.cursor()

#TWEETS TABLE
cur.execute('DROP TABLE IF EXISTS Tweets')
statement = 'CREATE TABLE IF NOT EXISTS '
statement += 'Tweets (tweet TEXT, tweet ID INTEGER PRIMARY KEY, user TEXT NOT NULL, FOREIGN KEY (user) REFERENCES Users(user) on UPDATE SET NULL, movie TEXT NOT NULL, FOREIGN KEY (movie) REFERENCES Users(movie) on UPDATE SET NULL, number favorites INTEGER, number retweets INTEGER)'
cur.execute(statement)

#USERS TABLE
cur.execute('DROP TABLE IF EXISTS Users')
table = 'CREATE TABLE IF NOT EXISTS '
table += 'Users (user_id INTEGER PRIMARY KEY, screen_name TEXT, num_favs INTEGER, retweets INTEGER)'
cur.execute(table)

#MOVIES TABLE
cur.execute('DROP TABLE IF EXISTS Movies')
table = 'CREATE TABLE IF NOT EXISTS '
table += 'Movies (id INTEGER PRIMARY KEY, title TEXT, director TEXT, num_languages INTEGER, imdb_rating INTEGER, top_actor TEXT)'
cur.execute(table)

#At least enough code to load data into 1 of your database tables (this should accord with your instructions/tests)






#Tests at the end of your file that accord with those instructions (will test that you completed those instructions correctly!)

# Put your tests here, with any edits you now need from when you turned them in with your project plan.
class Tests(unittest.TestCase):
	def test1(self): #tests that get_rating returns an integer
		self.assertEqual(type(get_rating()), type(int))

	def test2(self): #tests that get_director returns a string
		self.assertEqual(type(get_director()), type(""))

	def test3(self): #tests that get_title returns a string
		self.assertEqual(type(get_title()), type(""))
 
	def test4(self): #tests that input of class Movie is a dictionary
		self.assertEqual(type(Movie()), type({}))

	def test5(self): #tests that get_actors returns a list 
		self.assertEqual(type(get_actors()), type([]))

	def test6(self): #tests that get_langs returns an integer
		self.assertEqual(type(get_langs()), type(int))

	def test7(self): #tests that there are 6 rows in the Tweets table
		conn = sqlite3.connect('final_project.db') #not sure what the db will be called yet
		cur = conn.cursor()
		cur.execute('SELECT * FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==6)
		conn.close()

	def test8(self): #tests that the list that get_actors contains strings
		self.assertEqual(type(test8[0],type(["Brad Pitt", "George Clooney"])))

    

if __name__ == "__main__":
	unittest.main(verbosity=2)

# Remember to invoke your tests so they will run! (Recommend using the verbosity=2 argument.)