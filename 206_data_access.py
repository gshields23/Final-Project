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

# 1 - Write functions to get and cache data from Twitter 															- Done! But might be wrong
# 2 - Write function to get and cache data from OMDB 																- Done!
# 3 - Define a class Movie - must accept a dictionary, should have 3 instance variables, 2 methods					-
# 4 - Pick 3 movie title search terms of OMDB 																		- Done!
# 5 - Make a request to OMDB on each of those search terms, using your function, then accumulate in dictionary		-
# 6 - Create a list of instances of class Movie (using dictionaries from OMDB request)								-
# 7 - Use Twitter to search for one star actor in each movie,get info about each user who posted a tweet about them -
# 8 - Create database file with 3 tables																			- Done!
# 9 - Load data into databases																						- Done! (may have to change)
#10 - Process data and create an output file 																		-
#11 - Write that data to a text file as a summary stats page														-
																													
																													#1/2 way done!



# I want to set up my class Movie here. I know a lot of my code will change once I get this class set up.


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


#OMDB search
#create movie objects
#search twitter using movie objects 



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

#OMDB CACHING - here is where I get and cache data from OMDB. 
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


movieinfo = []
for movie in movie_titles:
	x = Movie(getdata_omdb(movie))
	movieinfo.append(x)



#TWITTER API - here is my first function about retrieving information about a user specifically on Twitter.
#I tested it with Ryan Gosling's username. He's the highest paid actor in La La Land (or the first mentioned)
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
#I thought that if I put in 'La La Land' I'd get data about all Tweets from La La Land, but I actually just got my
#personal information. When I put in 'ryangosling' I get all of his tweets. I'm not sure if this has to do with the fact
#that I don't have a class yet or not, but I'll need to fix this.
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
	


twitterinfo = []
for movie in movie_titles:
	if movie == 'Lion':
		print (movie)
		y = getTwitterMentions(movie)
		for x in y['statuses']:
			print (x['text'])	


#diction = getdata_omdb('La La Land') #What I'm using to enter info into my database
#This code successfully works and I am more confident in it than my Twitter data.

#Code that creates a database file and tables as your project plan explains, such that your program can be run over and over again without error and without duplicate rows in your tables.
#I don't know how to specifically cover for having duplicates or not. I think by having the specific IDs as the primary key,
#everything will be unique.
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



# #TWITTER PROCESSING FOR USERS - here I'm mining for the specific data that I want to upload to the database (for OMDB too)
# users_userid = []
# users_screenname = []
# users_favs = []
# users_followers = []

# for users in users_list:
# 	users_userid.append(users['user']['id_str'])
# 	users_screenname.append(users['user']['screen_name'])
# 	users_favs.append(users['user']['favourites_count'])
# 	users_followers.append(users['user']['followers_count']) #I added this to see which actor would have the most followers

# user_list = list(zip(users_userid, users_screenname, users_favs, users_followers))

# for users in user_list:
# 	z = 'INSERT OR IGNORE INTO Users VALUES (?, ?, ?, ?)'
# 	cur.execute(z, users)


# # #OMDB PROCESSING
# id = []
# title = []
# director = []
# num_langs = []
# imdb_rating = []
# firstactor = []


# id.append(diction['imdbID'])
# title.append(diction['Title'])
# director.append(diction['Director'])
# num_langs.append(len(diction['Language']))
# imdb_rating.append(diction['imdbRating'])
# firstactor.append(diction['Actors'].split(',', 1)[0]) #I had to do this to get the first full name listed


# omdb_zip = zip(id, title, director, num_langs, imdb_rating, firstactor)
# omdb_list = list(omdb_zip)

# # print(type(omdb_zip))

# for movie_info in omdb_list:
# 	y = 'INSERT OR IGNORE INTO Movies VALUES (?,?,?,?,?,?)'
# 	cur.execute(y, movie_info)

# print(firstactor)

#TWITTER PROCESSING FOR TWEETS (MENTIONS: BE SURE TO USE THE MOVIE ID NOT THE MOVIE TITLE)
#I made this one last because it refers to other tables (Movies)
# tweets_text = []
# tweets_id = []
# tweets_user = []
# tweets_movie = []
# tweets_numfavs = []
# tweets_numrt = []

# for x in mentions_list:
# 	tweets_text.append(x['text'])
# 	tweets_id.append(x['id'])
# 	tweets_user.append(x['user']['name'])
# 	tweets_movie.append('none')
# 	tweets_numfavs.append(x['user']['favourites_count'])
# 	tweets_numrt.append(x['retweet_count'])


# tweets_list = list(zip(tweets_text, tweets_id, tweets_user, tweets_movie, tweets_numfavs, tweets_numrt))

# for info in tweets_list:
# 	y = 'INSERT OR IGNORE INTO Tweets VALUES (?,?,?,?,?,?)'
# 	cur.execute(y, info)

# conn.commit()

# conn.close()




# #CREATING A CSV FILE
# outfile = open('finalproject.csv', 'w')
# outfile.write('self.title, self.list_actors\n')


# for x in possible_airports:
#     try:
#         outfile.write('{}, {}, {}, {}\n'.format(*extract_airport_data(x)))

#     except:
#         print "Failed for airport " + x


#Tests at the end of your file that accord with those instructions (will test that you completed those instructions correctly!)
class Tests(unittest.TestCase):
	def test1(self): #tests that there are 6 rows in the Tweets table
		conn = sqlite3.connect('final_project.db') 
		cur = conn.cursor()
		cur.execute('SELECT * FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(len(result[0])==6)
		conn.close()

	def test2(self): #tests that there are 4 rows in the Users table
		conn = sqlite3.connect('final_project.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result[0])==4)
		conn.close()
	
	def test3(self): #tests that there are 6 rows in the Movies table
		conn = sqlite3.connect('final_project.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Movies');
		result = cur.fetchall()
		self.assertTrue(len(result[0])==6)
		conn.close()

	def test4(self): #tests that first actor returns one string, the full name of an actor
		self.assertEqual(len(firstactor), 1)

	def test5(self): #tests that the Movie id is a string instead of an integer (I had an issue with this where I expected it to be an integer and it wasn't!)
	 	self.assertEqual(type(id[0]),type(""))

	def test6(self): #tests that my list for OMBD is indeed a list
		self.assertEqual(type(omdb_list),type([]))

	def test7(self):
		self.assertEqual(type(mentions_list), type([]))

	def test8(self): 
		self.assertEqual(type(user_list),type([]))



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

    

if __name__ == "__main__":
	unittest.main(verbosity=2)

# Remember to invoke your tests so they will run! (Recommend using the verbosity=2 argument.)