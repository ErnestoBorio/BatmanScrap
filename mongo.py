
from pymongo import MongoClient
from pprint import pprint
cl = MongoClient('localhost', 27017)
db = cl["BatScrap"]["issue"]

x = db.update_many(
	{},
	{ '$unset':{'number_int': True}})

cl.close()