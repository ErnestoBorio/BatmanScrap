
from pymongo import MongoClient

mongo = MongoClient('localhost', 27017)
col = mongo["BatScrap"]["issue"]

cur = col.find( 
	projection= ['publication', 'number', 'date', 'date_key', 'main_story', 'event'],
	sort= [('date_key',1), ('publication',-1), ('issue',1)]
	)

for i in cur:
	date = str(i['date_key'])
	date = date[0:4] +'-'+ date[4:]

	pub: str = i['publication']
	if pub.startswith('Batman'):
		pub = 'BM'+ pub[-1]
	elif pub.startswith('Detective'):
		pub = 'DC'+ pub[-1]
	else:
		pub = '??? '+ pub
	
	if 'event' in i:
		event = ' ('+ i['event'] +')'
	else:
		event = ''

	print( f"{date} | {pub} %3d | {i['main_story']} {event}" % (i['number']))