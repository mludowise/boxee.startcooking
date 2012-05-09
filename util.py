import mc
import urllib2
import re

def clean_html_entities( text ):
	""" Convert html entities """
	try:
		text = text.replace( "&#8217;", "'" )
		text = text.replace( "&#8220;", "\"" )
		text = text.replace( "&#8221;", "\"" )
		text = text.replace( "&#160;", "" )
		text = text.replace( "&amp;", "&" )
		text = text.replace( "&gt;", ">" )
		text = text.replace( "&lt;", "<" )
		text = text.replace( "&quot;", '"' )
		text = text.replace( "&iacute;", 'i' )
		text = text.replace( "&#39;","'" )
		text = text.replace( "&rsquo;","’" )
		text = text.replace( "&nbsp;", ' ' )
		text = text.replace( "<br />","\n" )
		text = text.replace( "<br/>","\n" )
		text = text.replace( "<br>","\n" )
		text = text.replace( "<strong>","" )
		text = text.replace( "</strong>","" )
		text = text.replace( "<b>","" )
		text = text.replace( "</b>","" )
	except: 
		pass
	return text

def get_contents(xml, tag):
	if xml.find("<" + tag + ">") > 0:
		tempXML = xml[xml.find("<" + tag + ">") + len(tag) + 2: len(xml)]
		return tempXML[0 : tempXML.find("</" + tag + ">")]
	else:
		return ""

def parse_duration(durationString):
	if (len(durationString) != 8):
		return 0
	hours = durationString[0 : 2]
	minutes = durationString[3 : 5]
	seconds = durationString[6 : 8]
	return 3600 * int(hours) + 60 * int(minutes) + int(seconds)
	
def get_videos(url):
	response = urllib2.urlopen(url)
	res = response.read()
	response.close()
	rssItems = res.split("<item>")
	items = mc.ListItems()
	for rssItem in rssItems:
		item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
		title = get_contents(rssItem, "title")
		link = rssItem[rssItem.find("media:content url=\"") + 19 : len(rssItem)]
		link = link[0 : link.find("\"")]
		description = get_contents(rssItem, "itunes:subtitle")
		duration = get_contents(rssItem, "itunes:duration")
		content = get_contents(rssItem, "content:encoded")
		item.SetLabel(clean_html_entities(title))
		item.SetDuration(parse_duration(duration))
		item.SetProperty("duration", duration)
		item.SetPath(link)
		item.SetDescription(description)
		item.SetProperty("description", description)
		item.SetReportToServer(False)
		if len(content) > 0:
			content = content[content.find("<![CDATA[") + 9 : content.find("]]>")]
			content = content[0 : content.find("<div class=\"feedflare\">")]
			serving = content[content.find("<em>serves ") + 11 : content.find("</em>")]
			thumbnailURL = content[content.find("<img src=\"") + 10 : len(content)]
			thumbnailURL = thumbnailURL[0 : thumbnailURL.find("\">")]
			ingredientsHTML = content[content.find("<ul>") : content.find("</ul>") + 5]
			instructionsHTML = content[content.find("</ul>") + 5 : len(content)]
			instructionsHTML = content[content.find("<p>") + 3 : len(content)]
			instructionsHTML = instructionsHTML.replace("</p><p>", "\n\n")
			instructionsHTML = instructionsHTML[0 : instructionsHTML.find("</p>")]
			item.SetThumbnail(thumbnailURL)
			if len(serving) > 0:
				item.SetProperty("serving", "Serves " + serving)
			item.SetProperty("ingredients", ingredientsHTML)
			item.SetProperty("instructions", clean_html_entities(instructionsHTML))
			items.append(item)
	return items

def load_ingredients(ingredientsHTML):
   	ingredients = ingredientsHTML.split("</li>")
	
	items = mc.ListItems()
	for ingredient in ingredients:
		if ingredient.find("<li>") >= 0:
			ingredient = ingredient[ingredient.find("<li>") + 4 : len(ingredient)]
			item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
			item.SetLabel(clean_html_entities(ingredient))
			items.append(item)
	return items