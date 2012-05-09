# 
# Tracker Client - A Google Analytics Integration
# A Python module for interacting with the Tracker web service.
# 
# Written by /rob, 29 July 2010
#
# Usage:
# 
# Tracker Client uses the Tracker web service to allow Python apps like those found on Boxee to store view and event
# tracking data on Google Analytics.  To track a page view, simply call the method with the option of passing a 
# parameter for the window's ID or canonical name for easy reporting (e.g. "home").  To track an event, call the
# method with event argument with the category as the value (e.g. "Content", "Video"), action argument with an
# appropriate value (e.g. "Play", "Pause") and label argument (e.g. The title of the content being played).  Value
# is optional.
#
# Returns false if fail.  Returns transparent GIF if success.
#
# Examples:
# 
# Instantiate object:
# myTracker = tracker.Tracker()
#
# Instantiate object with your own Google Analytics code.
# myTracker = tracker.Tracker("UA-xxxxxxx-x")
#
# Track page view:
# tracker.Tracker.trackView()
# 
# Track page view with non-default window:
# tracker.Tracker.trackView("browse")
# 
# Track Play event:
# myTracker.trackEvent("Video", "Play", "Foo Bar")

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
		print description
		item.SetReportToServer(False)
		if len(content) > 0:
			content = content[content.find("<![CDATA[") + 9 : content.find("]]>")]
			content = content[0 : content.find("<div class=\"feedflare\">")]
			serving = content[content.find("<em>serves ") + 11 : content.find("</em>")]
			thumbnailURL = content[content.find("<img src=\"") + 10 : len(content)]
			thumbnailURL = thumbnailURL[0 : thumbnailURL.find("\">")]
			ingredientsHTML = content[content.find("<ul>") : content.find("</ul>") + 5]
			instructionsHTML = content[content.find("</ul>") + 5 : len(content)]
			item.SetThumbnail(thumbnailURL)
			item.SetProperty("serving", "Serves " + serving)
			item.SetProperty("ingredients", ingredientsHTML)
			item.SetProperty("instructions", "instructionsHTML")
			
			items.append(item)
	
	mc.GetWindow(14000).GetList(100).SetItems(items)
	mc.HideDialogWait()
	mc.GetWindow(14000).GetControl(100).SetFocus()