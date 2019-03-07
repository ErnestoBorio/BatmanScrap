
from petruza.misc import obj
import requests
from lxml import html

months = {'january':'01', 'february':'02', 'march':'03', 'april':'04', 'may':'05', 'june':'06',
	'july':'07', 'august':'08', 'september':'09', 'october':'10', 'november':'11', 'december':'12'}

base_url = "https://dc.fandom.com"
url = "https://dc.fandom.com/wiki/Detective_Comics_Vol_1_364"
response = requests.get( url)
tree = html.fromstring( response.content)

data = obj()
data.url = url

data.issue = "".join( tree.xpath("//*[@class='page-header__title']/text()"))
data.one_shot = "".join( tree.xpath("//*[@data-source='OneShot']//text()"))

main_story = tree.xpath("//*[@data-source='StoryTitle1']//text()")
data.main_story = "".join( main_story)

date = tree.xpath("//h2[contains(@class,'pi-title')]//a[contains(@title,'Category')]//text()")
month = date[0]
year = date[1]
month_number = months[ month.lower() ]
data.date = obj()
data.date.text = ', '.join( date)
data.date.key  = f"{year}-{month_number}"

data.stories = []
stories = tree.xpath("//h2[contains(@class,'pi-header')]")
for story in stories:
	title = story.xpath("descendant-or-self::*/text()")
	title = "".join( title)
	if any( term in title.lower() for term in ['bat','robin'] ):
		data.stories.append( title)

data.next = None
link_next = tree.xpath("//*[@data-source='NextIssue']/a")
if link_next:
	data.next = obj()
	data.next.text  = link_next[0].xpath("text()")[0]
	data.next.url   = base_url+ link_next[0].xpath("@href")[0]
	data.next.title = link_next[0].xpath("@title")[0]

data.prev = None
link_prev = tree.xpath("//*[@data-source='PreviousIssue']/a")
if link_prev:
	data.prev = obj()
	data.prev.text  = link_prev[0].xpath("text()")[0]
	data.prev.url   = base_url+ link_prev[0].xpath("@href")[0]
	data.prev.title = link_prev[0].xpath("@title")[0]

print( data)
pass