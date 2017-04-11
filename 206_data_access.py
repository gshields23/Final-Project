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

# Begin filling in instructions....








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