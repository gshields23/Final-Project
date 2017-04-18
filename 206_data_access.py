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

CACHE_FNAME = "206finalproject_cache.json"
try:
	cache_file = open(CACHE_FNAME,'r')
	cache_contents = cache_file.read()
	cache_file.close()
	CACHE_DICTION = json.loads(cache_contents)
except:
	CACHE_DICTION = {}

#TWITTER API
def getTwitterUsername(actor_username):
	unique_identifier = "twitter_{}".format(actor_username)
	if unique_identifier in CACHE_DICTION:
		print('using cached data for', actor_username)
		#twitter_results = CACHE_DICTION[unique_identifier]
		statuses = CACHE_DICTION[unique_identifier]
		pass
	else:
		print('getting data from internet for', actor_username)
		statuses = api.user_timeline(screen_name=actor_username, count = 100) #how to get username from the actors listed in the dictionary???
		CACHE_DICTION[unique_identifier] = statuses
		f=open(CACHE_FNAME, 'w')
		f.write(json.dumps(CACHE_DICTION))
		f.close()

	#return CACHE_DICTION[unique_identifier]
	
	return statuses

actors = getTwitterUsername('La La Land')

def getTwitterMentions(title):
	unique_identifier = "twitter_{}".format(title)
	if unique_identifier in CACHE_DICTION:
		print('using cached data for', title)
		#twitter_results = CACHE_DICTION[unique_identifier]
		statuses = CACHE_DICTION[unique_identifier]
		pass
	else:
		print('getting data from internet for', title)
		statuses = api.search(q=title, count = 100)
		CACHE_DICTION[unique_identifier] = statuses
		f=open(CACHE_FNAME, 'w')
		f.write(json.dumps(CACHE_DICTION))
		f.close()

	#return CACHE_DICTION[unique_identifier]
	return statuses
	

mentions = getTwitterMentions('La La Land')

#OMDB CACHING
def getdata_omdb(title):
	unique_identifier = "omdb_{}".format(title)

	if unique_identifier in CACHE_DICTION:
		print('using cached data for', title)
		omdb_dict = CACHE_DICTION[unique_identifier]
		return omdb_dict

	else:
		print('getting data from internet for', title)
		params_dict = {}
		params_dict['t'] = title
		response = requests.get('http://www.omdbapi.com/', params = params_dict)
		omdb_dict = json.loads(response.text)
		CACHE_DICTION[unique_identifier] = omdb_dict
		f=open(CACHE_FNAME, 'w')
		f.write(json.dumps(CACHE_DICTION))
		f.close()

		return omdb_dict

title = getdata_omdb('La La Land')

#Code that creates a database file and tables as your project plan explains, such that your program can be run over and over again without error and without duplicate rows in your tables.

conn = sqlite3.connect('finalproject.db')
cur = conn.cursor()


#USERS TABLE
cur.execute('DROP TABLE IF EXISTS Users')
table = 'CREATE TABLE IF NOT EXISTS '
table += 'Users (user_id INTEGER PRIMARY KEY, user_screenname TEXT, num_favs INTEGER, retweets INTEGER)'
cur.execute(table)

#MOVIES TABLE
cur.execute('DROP TABLE IF EXISTS Movies')
table = 'CREATE TABLE IF NOT EXISTS '
table += 'Movies (id INTEGER PRIMARY KEY, movie_title TEXT, director TEXT, num_languages INTEGER, imdb_rating INTEGER, top_actor TEXT)'
cur.execute(table)

#TWEETS TABLE
cur.execute('DROP TABLE IF EXISTS Tweets')
table = 'CREATE TABLE IF NOT EXISTS '
table += 'Tweets (tweet TEXT, tweet_id INTEGER PRIMARY KEY, user_id TEXT NOT NULL, movie_title TEXT NOT NULL, number_favorites INTEGER, number_retweets INTEGER, FOREIGN KEY (user_id) REFERENCES Users(user_id) on UPDATE SET NULL, FOREIGN KEY (movie_title) REFERENCES Movies(movie_title) on UPDATE SET NULL)'
cur.execute(table)


conn.close()


#TWITTER PROCESSING
# users_userid = []
# users_screenname = []
# users_favs = []
# users_descrip = []

# for users in umich_tweets:
# 	users_userid.append(users['user']['id_str'])
# 	users_screenname.append(users['user']['screen_name'])
# 	users_favs.append(users['user']['favourites_count'])
# 	users_descrip.append(users['user']['description'])

# user_list = list(zip(users_userid, users_screenname, users_favs, users_descrip))

# for users in user_list:
# 	z = 'INSERT OR IGNORE INTO Users VALUES (?, ?, ?, ?)'
# 	cur.execute(z, users)

# for x in umich_tweets:
# 	for u in x['entities']['user_mentions']:
# 		unique_identifier = "user_{}".format(u['screen_name'])
# 		if unique_identifier in CACHE_DICTION:
# 			my_var = CACHE_DICTION[unique_identifier]
# 		else:
# 			my_var = api.get_user(u['screen_name'])
# 			CACHE_DICTION[unique_identifier] = my_var
# 			f=open(CACHE_FNAME, 'w')
# 			f.write(json.dumps(CACHE_DICTION))
# 			f.close()


#OMDB PROCESSING
#for actors in omdb_info:



#Tests at the end of your file that accord with those instructions (will test that you completed those instructions correctly!)

# # Put your tests here, with any edits you now need from when you turned them in with your project plan.
# class Tests(unittest.TestCase):
# 	def test1(self): #tests that get_rating returns an integer
# 		self.assertEqual(type(get_rating()), type(int))

# 	def test2(self): #tests that get_director returns a string
# 		self.assertEqual(type(get_director()), type(""))

# 	def test3(self): #tests that get_title returns a string
# 		self.assertEqual(type(get_title()), type(""))
 
# 	def test4(self): #tests that input of class Movie is a dictionary
# 		self.assertEqual(type(Movie()), type({}))

# 	def test5(self): #tests that get_actors returns a list 
# 		self.assertEqual(type(get_actors()), type([]))

# 	def test6(self): #tests that get_langs returns an integer
# 		self.assertEqual(type(get_langs()), type(int))

# 	def test7(self): #tests that there are 6 rows in the Tweets table
# 		conn = sqlite3.connect('final_project.db') #not sure what the db will be called yet
# 		cur = conn.cursor()
# 		cur.execute('SELECT * FROM Tweets');
# 		result = cur.fetchall()
# 		self.assertTrue(len(result[1])==6)
# 		conn.close()

# 	def test8(self): #tests that the list that get_actors contains strings
# 		self.assertEqual(type(test8[0],type(["Emma Stone", "Ryan Gosling"])))

    

# if __name__ == "__main__":
# 	unittest.main(verbosity=2)

# Remember to invoke your tests so they will run! (Recommend using the verbosity=2 argument.)