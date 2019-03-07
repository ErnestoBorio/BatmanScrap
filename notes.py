
# (?:https?://)(?:www\.)zipcomic\.com/(?:.+)/(:<folder>[^/]+)/(?<file>.+)\.(?<ext>[^\.]+)

response.headers._store['set-cookie'] = ('Set-Cookie', 'wikia_beacon_id=eL0...}; path=/')
response.headers._store['content-encoding'] = ('Content-Encoding', 'gzip')

xpath("descendant-or-self::*/text()")
# si mismo y todos sus descendientes

xpath("descendant-or-self::*[self::h2 or self::a]")
# si mismo y todos sus descendientes que sean h2 o a

# issue
response.xpath("//*[@class='page-header__title']/text()").getall()
['Detective Comics Vol 1 500']

# title (concatenar)
response.xpath("//*[@data-source='StoryTitle1']//text()").getall() 
['The Bat-Man: "', 'The Case of the Chemical Syndicate', '"']

# issue
r.xpath("//*[@data-source='OneShot']//text()").getall()
['Detective Comics Vol 1', ' #500']

# stories
r.xpath("//h2[contains(text(), 'Bat') or contains(text(), 'bat') or contains(text(), 'Robin')] [contains(@class,'pi-header')]//text()").getall()
['Batman: "To Kill a Legend"',
 'Batman: "Once Upon a Time..."',
 'Batman: "The Batman Encounters – Gray Face"',
 'Batman and Deadman: "What Happens When a Batman Dies?"']

# link next
a = r.xpath("//*[@data-source='NextIssue']/a")

	a.xpath("text()").get()                                                                                                                                                                
	'Detective Comics # 501'

	a.xpath("@href").get()                                                                                                                                                                 
	'/wiki/Detective_Comics_Vol_1_501'

	a.xpath("@title").get()                                                                                                                                                                
	'Detective Comics Vol 1 501'
# y lo mismo para previous, si hiciera falta
a = r.xpath("//*[@data-source='PreviousIssue']/a")
# Si r.xpath("//*[@data-source='NextIssue']/a") devuelve [] es que no hay next issue.

#date
r.xpath("//h2[contains(@class,'pi-title')]//a[contains(@title,'Category')]//text()").getall()                                                                                          
['March', '1981']