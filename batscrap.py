
import re
import requests
from lxml import html
from time import sleep
from pprint import pprint
from pymongo import MongoClient
from datetime import datetime
import logging

def main():
	# base_url = "https://dc.fandom.com/wiki/Detective_Comics_Vol_1_"
	base_url = "https://dc.fandom.com/wiki/Batman_Vol_1_"
	scraper = BatScraper()
	scraper.scrape( base_url, 450, 451 )

class BatScraper:

	months = {'january':'01', 'february':'02', 'march':'03', 'april':'04', 'may':'05', 'june':'06',
		'july':'07', 'august':'08', 'september':'09', 'october':'10', 'november':'11', 'december':'12'}

	def scrape(self, base_url:str, minimum: int, maximum = None, nap: int = 1 ):

		if maximum is None:
			maximum = minimum

		now = datetime.now()
		timestamp = now.strftime("%Y-%m-%d %H:%M:%S")


		self.started_log = False
		log_time  = now.strftime("%Y-%m-%d_%H-%M-%S")
		
		def log(message: str, level: int = logging.ERROR):
			if not self.started_log:
				self.started_log = True
				logging.basicConfig( 
					handlers = [ logging.StreamHandler(),
						logging.FileHandler( filename= f"errors_{log_time}.log")],
					format = "%(levelname)s | %(message)s")
			logging.log( level, message )
		# log


		mongo = MongoClient('localhost', 27017)
		db = mongo["BatScrap"]["issue"]
		
		for number in range( minimum, maximum+1 ):

			url = base_url + str(number)

			print( f"Requesting `{url}`... ", end='')
			response = requests.get( url)

			print( 'parsing... ', end='')
			tree = html.fromstring( response.content)

			data = {}

			one_shot = tree.xpath("//*[@data-source='OneShot']//text()")
			data['publication'] = one_shot[0]
			
			match = re.search( '\d+', one_shot[1])
			data['issue_number'] = match[0]

			data['one_shot'] = "".join( one_shot)
			data['issue'] = "".join( tree.xpath("//*[@class='page-header__title']/text()"))

			main_story = tree.xpath("//*[@data-source='StoryTitle1']//text()")
			data['main_story'] = "".join( main_story)

			event = tree.xpath("//*[@data-source='Event']//a")
			if event:
				data['event'] = {
					"title": event[0].xpath("text()")[0],
					"link":  event[0].xpath("@href")[0] }

			data['cover'] = tree.xpath("//img[@alt='Cover']/@src")[0]

			month, year = tree.xpath("//h2[contains(@class,'pi-title')]//a[contains(@title,'Category')]//text()")
			month_number = self.months[ month.lower() ]
			data['date'] = f"{month}, {year}"
			date_key = f"{year}-{month_number}"
			data['date_key']  = int( year + month_number )

			data['stories'] = []
			stories = tree.xpath("//h2[contains(@class,'pi-header')]")
			for story in stories:
				title = story.xpath("descendant-or-self::*/text()")
				title = "".join( title)
				# if not any( term in title.lower() for term in ['variant cover artists']):
				if 'variant cover artists' not in title.lower():
					data['stories'].append( title)
			
			data['next'] = None
			link_next = tree.xpath("//*[@data-source='NextIssue']/a/@href")
			if link_next:
				data['next'] = link_next[0]

			data['prev'] = None
			link_prev = tree.xpath("//*[@data-source='PreviousIssue']/a/@href")
			if link_prev:
				data['prev'] = link_prev[0]
			
			data['url'] = url
			data['updated'] = timestamp
			_id = date_key +'|'+ data['publication'] +'|'+ data['issue_number']

			try:
				db.replace_one( {'_id': _id}, data, upsert = True)
			except Exception as exp:
				pass # log type(exp), exp
			# pprint(data)
			
			print( f"parsed: {_id}", end='')

			if number < maximum and nap > 0:
				print(" ; sleeping...")
				sleep(nap)
			else:
				print()
		
		mongo.close()
	# scrape
# BatScraper

if __name__ == '__main__': main()