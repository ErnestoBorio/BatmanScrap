import re
import requests
from lxml import html
from time import sleep
from pprint import pprint
from pymongo import MongoClient
from datetime import datetime
import logging
import sys

def main( argv):
	# base_url = "https://dc.fandom.com/wiki/Batman_Vol_1_"
	base_url = argv[1] if len(argv)>=2 else "https://dc.fandom.com/wiki/Detective_Comics_Vol_1_"
	start = int(argv[2]) if len(argv)>=3 else 27
	stop = int(argv[3]) if len(argv)>=4 else 881

	print(f"Starting scrape of {base_url} ...")
	scraper = BatScraper()
	scraper.scrape( base_url, start, stop )
	print(f"Finished {base_url} ({start}..{stop})")

class BatScraper:

	months = {'january':'01', 'february':'02', 'march':'03', 'april':'04', 'may':'05', 'june':'06',
		'july':'07', 'august':'08', 'september':'09', 'october':'10', 'november':'11', 'december':'12'}

	def scrape(self, base_url:str, minimum: int, maximum = None, nap: float = 1 ):

		if maximum is None:
			maximum = minimum

		now = datetime.now()
		timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

		started_log = False
		log_time  = now.strftime("%Y-%m-%d_%H-%M-%S")
		def log(message, level: int = logging.ERROR):
			nonlocal started_log
			if not started_log:
				started_log = True
				logging.basicConfig( 
					handlers = [ logging.StreamHandler(),
						logging.FileHandler( filename= f"errors_{log_time}.log")],
					format = "%(levelname)s | %(message)s")
			logging.log( level, message )


		def skip( consecutive_skips: int ) -> bool:
			if consecutive_skips >= 10:
				log( f"Reached {consecutive_skips} consecutive skips, something's wrong, aborting.")
				return false
			return true

		mongo = MongoClient('localhost', 27017)
		db = mongo["BatScrap"]["issue"]
		db_info = mongo["BatScrap"]["info"]
		db_log = mongo["BatScrap"]["log"]

		db_log_key = f"{timestamp}|{base_url}|{minimum}:{maximum}" 
		db_log.insert_one({
			'_id': db_log_key,
			'base_url': base_url,
			'from': minimum,
			'to': maximum,
			'started': timestamp,
			'status': 'started'
		})
		
		last_cookies = {}
		successful_parses = 0
		skips = 0
		consecutive_skips = 0 # number of consecutive requests skipped due to http or parsing error

		for number in range( minimum, maximum+1 ):
			url = base_url + str(number)

			print( f"Requesting `{url}`... ", end='')
			response = requests.get( url,
				headers = {'User-Agent': 
					"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"},
				cookies = last_cookies
			)

			if not response.ok:
				log({
					'url': url,
					'http status': response.status_code,
					'reason': response.reason,
					'response': response.text
				}) 
				consecutive_skips += 1
				skips += 1
				if not skip( consecutive_skips):
					return
				continue

			if response.cookies:
				last_cookies = response.cookies # return them the cookies they set, just in case

			print( 'parsing... ', end='')
			xml = html.fromstring(response.content)

			data = {}

			issue = xml.xpath("//*[@class='page-header__title']/text()")
			if issue:
				data['issue'] = "".join(issue)

			one_shot = xml.xpath("//*[@data-source='OneShot']//text()")
			if one_shot:
				data['publication'] = one_shot[0]
				match = re.search( '\d+', one_shot[1])
				data['number'] = int(match[0])
				data['one_shot'] = "".join( one_shot)
			elif issue: # if there's no one-shot, try with issue
				parts = data['issue'].split(" ")
				data['publication'] = " ".join( parts[0:-1])
				data['number'] = int(parts[-1])
			else:
				log(f"{url} : Can't get publication and issue number from [one-shot] or [issue], skipping this URI.")
				log({ 'issue': issue, 'one_shot': one_shot })
				consecutive_skips += 1
				skips += 1
				if not skip(consecutive_skips):
					return
				continue
			
			dateinfo = xml.xpath("//h2[contains(@class,'pi-title')]//a[contains(@title,'Category')]//text()")
			if len(dateinfo) == 2:
				month, year = dateinfo
				month_number = self.months[month.lower()]
				data['date'] = f"{month}, {year}"
				date_key = f"{year}-{month_number}"
				data['date_key']  = int(year + month_number)
			else:
				log( f"{url} : Can't get date info, skipping this URI." )
				log({'dateinfo': dateinfo})
				skips += 1
				consecutive_skips += 1
				if not skip( consecutive_skips):
					return
				continue
			
			main_story = xml.xpath("//*[@data-source='StoryTitle1']//text()")
			if main_story:
				data['main_story'] = "".join(main_story).strip()
			else:
				print( f"{url} : Couldn't retrieve main_story.")
			
			main_story_link = xml.xpath("//*[@data-source='StoryTitle1']/a")
			if main_story_link:
				rel = main_story_link[0].xpath("@rel")
				if (not rel) or (rel[0] != 'nofollow'):
					data['main_story_link'] = [
						main_story_link[0].xpath("@title")[0],
						main_story_link[0].xpath("@href")[0]]

			event = xml.xpath("//*[@data-source='Event']")
			if event:
				event_text = event[0].xpath("descendant-or-self::*/text()")
				data['event'] = "".join(event_text).strip()
				event_link = event[0].xpath("descendant-or-self::a")
				if event_link:
					data['event_link'] = {
						'title': event_link[0].xpath("@title")[0],
						'href' : event_link[0].xpath("@href")[0]}

			covers = xml.xpath("//aside[contains(@class,'portable-infobox')]//figure//img")
			if covers:
				data['covers']={}
				for cover in covers:
					cover_type = cover.xpath("@alt")[0]
					while cover_type in data['covers']:
						cover_type += '>'
					data['covers'][cover_type] = [
						cover.xpath("@src")[0],
						cover.xpath('@srcset')[0]]
			else:
				print( f"{url} : Couldn't retrieve cover.")

			stories = xml.xpath("//h2[contains(@class,'pi-header')]")
			if stories:
				data['stories'] = []
				for story in stories:
					title = story.xpath("descendant-or-self::*/text()")
					title = "".join( title)
					# if not any( term in title.lower() for term in ['variant cover artists']):
					if 'variant cover artists' not in title.lower():
						data['stories'].append( title)
			else:
				print( f"{url} : Couldn't retrieve stories.")
			
			link_next = xml.xpath("//*[@data-source='NextIssue']/a/@href")
			if link_next:
				data['next'] = link_next[0]

			link_prev = xml.xpath("//*[@data-source='PreviousIssue']/a/@href")
			if link_prev:
				data['prev'] = link_prev[0]
			
			data['url'] = url
			data['updated'] = timestamp
			_id = date_key +'|'+ data['publication'] +'|'+ str(data['number'])

			# Ok if we didn't skip by now, then this request looks good
			consecutive_skips = 0
			successful_parses += 1

			info = {
				'last_run': timestamp,
				'successful_parses': successful_parses,
				'skips': skips,
				'last_url': url,
				'from': minimum,
				'to': maximum,
				'last_number': number,
				'last_data': data,
				'last_parse': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			}
			
			try:
				db.replace_one({'_id': _id}, data, upsert= True)
				db_info.replace_one({'_id': 'unique'}, info, upsert= True)
				db_log.update_one({'_id': db_log_key},
					{'$set':{
						'successful_parses': successful_parses,
						'skips': skips,
						'last_number': number,
						'last_url': url,
						'last_parse': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
					}}
				)
			except Exception as exp:
				log( f"{url} : DB error "+ type(exp) +":"+ exp )
			
			print( f"parsed: {_id}", end='')

			if number < maximum and nap > 0:
				print(" ; sleeping...")
				sleep(nap)
			else:
				print()
		# end for
		
		db_log.update_one({'_id': db_log_key},
			{'$set':{
				'status': 'completed',
				'successful_parses': successful_parses,
				'skips': skips,
				'completed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			}}
		)
		mongo.close()
	# scrape
# BatScraper

if __name__ == '__main__':
	main( sys.argv)