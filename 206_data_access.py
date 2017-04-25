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
from collections import Counter
import sqlite3
import twitter_info
import re

# Steps of the Project:

# 1 - Write functions to get and cache data from Twitter 															- Done! 
# 2 - Write function to get and cache data from OMDB 																- Done!
# 3 - Define a class Movie - must accept a dictionary, should have 3 instance variables, 2 methods					- Done!
# 4 - Pick 3 movie title search terms of OMDB 																		- Done!
# 5 - Make a request to OMDB on each of those search terms, using your function, then accumulate in dictionary		- Done!
# 6 - Create a list of instances of class Movie (using dictionaries from OMDB request)								- Done!
# 7 - Use Twitter to search for one star actor in each movie,get info about each user who posted a tweet about them - Done!
# 8 - Create database file with 3 tables, Create queries															- **MAKE QUERIES**
# 9 - Load data into databases																						- Done!
#10 - Process data and create an output file, Write that data to a text file as a summary stats page				-													-
#11 - Make tests for the entire code 																				- Done!

																												

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
		
	def __str__(self): #still figuring out what to do with this
		return "{} from {}".format(self.list_actors, self.title) 

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


#There was a lot of controversy on Oscar night. I want to see which "best movie" nominated movie 
#is actually the most popular. Moonlight won the Oscar, but let's see how their follower base matches up!


#QUERY 1 - sort function, most retweets
x = 'SELECT SUM(Tweets.number_retweets), Tweets.movie_title FROM Tweets GROUP BY movie_title'
cur.execute(x)
movie_rt = cur.fetchall()
print("\nQUERY 1")
sorted_retweets = sorted(movie_rt, reverse = True)
print(sorted_retweets)


#QUERY 2 
y = 'SELECT SUM(Users.num_favs), Tweets.movie_title FROM Users INNER JOIN Tweets GROUP BY movie_title'
cur.execute(y)
favs_users = cur.fetchall()
sorted_favorites = sorted(favs_users, reverse = True)

print("\nQUERY 2")
print(sorted_favorites)

#QUERY 3 - reg ex
z = 'SELECT SUM(Tweets.number_retweets), Movies.movie_title, Movies.awards FROM Movies INNER JOIN Tweets ON Tweets.movie_title = Movies.movie_title GROUP BY Tweets.movie_title'
cur.execute(z)
lst_awards = cur.fetchall()
print("\nQUERY 3")
for x in lst_awards:
	#print(x)
	regex_z = r"(?:Won).[0-9]"
	sep_awards = re.findall(regex_z, x[2])
	output = '{}, {}'.format(x[1], sep_awards)
	print(output)



# sorted_awards = lst_awards.split(" ").sort([1])
# print(sorted_awards)


#QUERY 4
a = 'SELECT Movies.movie_title, Tweets.number_retweets FROM Tweets INNER JOIN Movies ON Tweets.movie_title = Movies.movie_title WHERE Tweets.number_retweets > 1000'
cur.execute(a)
movieRT_lst = cur.fetchall()
print("\nQUERY 4")

x = [element[0] for element in movieRT_lst]
c = Counter(x)
print(c)


# #CREATING A txt FILE
outfile = open('finalproject.txt', 'w')
outfile.write("\n                      Summary Statistics for Movies & Twitter \n")
outfile.write("\nThe 2017 Oscars spiked controversy when 'Moonlight' took home Best Film, even though 'La La Land' was mistakenly announced first as the winner. People around the world argued for what they felt was the better movie. I decided to look at Twitter data for 'La La Land,' 'Moonlight,' and 'Lion' to see which movie spiked the most discussion online, for better or for worse.")


outfile.close()

conn.close()

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
	
	def test3(self): #tests that there are 7 rows in the Movies table
		conn = sqlite3.connect('final_project.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Movies');
		result = cur.fetchall()
		self.assertTrue(len(result[0])==7)
		conn.close()

	def test4(self): #tests that the Movie id is a string instead of an integer (I had an issue with this where I expected it to be an integer and it wasn't!)
	 	self.assertEqual(type(id[0]),type(""))

	def test5(self): #tests that my list for OMBD is indeed a list
		self.assertEqual(type(omdb_list),type([]))

	def test6(self):
		m = Movie(getdata_omdb('La La Land'))
		self.assertEqual(len(m.getDatabaseInfo()), 8)

	def test7(self):
		m = Movie(getdata_omdb('La La Land'))
		self.assertEqual(type(m.getTitle()), type(""))

	def test8(self): 
		m = Movie(getdata_omdb('La La Land'))
		self.assertEqual(type(m.getDatabaseInfo()), type((1,2,3)))
 
	def test9(self): 
		m = Movie(getdata_omdb('Moonlight'))
		self.assertEqual(type(m.id), type(""))

	# def test10(self):
	# 	t = Twitter(getTwitterMentions('La La Land'))
	# 	self.assertEqual(type(t.text), type(1))

	def test11(self):
		m = Movie(getdata_omdb('Lion'))
		self.assertEqual(len(m.__str__().split()), 10)


if __name__ == "__main__":
	unittest.main(verbosity=2)



