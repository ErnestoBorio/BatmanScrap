import requests
from lxml import html

number = 31

base_url = "https://dc.fandom.com/wiki/Detective_Comics_Vol_2_"
url = base_url + str(number)
response = requests.get( url, headers = {'User-Agent': 
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"})
xml = html.fromstring(response.content)
data = {}

def main():
	main_story()
	pass

def main_story():
	main_story = xml.xpath("//*[@data-source='StoryTitle1']//text()")
	if main_story:
		data['main_story'] = "".join(main_story).strip()
	main_story_link = xml.xpath("//*[@data-source='StoryTitle1']/a")
	if main_story_link:
		rel = main_story_link[0].xpath("@rel")
		if (not rel) or (rel[0] != 'nofollow'):
			data['main_story_link'] = [
				main_story_link[0].xpath("@title")[0],
				main_story_link[0].xpath("@href")[0]]
	debug = data
	pass

def test_covers():
	covers = xml.xpath("//*[contains(concat(' ',normalize-space(@class),' '), ' pi-image-collection-tab-content ')]//figure//img")
	if covers:
		data['covers']={}
		for cover in covers:
			cover_type = cover.xpath("@alt")[0]
			while cover_type in data['covers']:
				cover_type += '>'
			data['covers'][cover_type] = [
				cover.xpath("@src")[0],
				cover.xpath('@srcset')[0]]
		pass
	debug = data
	pass

def test_event():
	event = xml.xpath("//*[@data-source='Event']")
	text = event[0].xpath("descendant-or-self::*/text()")
	text = "".join(text).strip()
	link = event[0].xpath("descendant-or-self::a")
	if link:
		title = link[0].xpath("@title")[0]
		href = link[0].xpath("@href")[0]
	pass

if __name__ == '__main__':
	main()