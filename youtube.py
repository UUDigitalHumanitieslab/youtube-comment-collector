import feedparser
import requests
import csv
import time
import ConfigParser


def main():
	config = ConfigParser.RawConfigParser()
	config.read('example.cfg')

	with open('comments.csv', 'wb') as csv_file:
		# write heading
		csv_file.write(u'\uFEFF'.encode('utf-8')) # the UTF-8 BOM to hint Excel we are using that...
		csv_writer = csv.writer(csv_file, dialect='excel', delimiter=';', quoting=csv.QUOTE_MINIMAL)
		heading = ['username', 'firstname', 'lastname', 'location', \
			'birthday', 'gender', 'aboutme', 'organizations', 'tagline', \
			'occupation', 'skills', 'statistics', 'replycount', 'activity_id', 'published', 'comment']
		csv_writer.writerow(heading)

		# get first feed
		url = 'https://gdata.youtube.com/feeds/api/videos/' + config.get('youtube', 'video_id') + '/comments'
		r = requests.get(url, params={'v': '2.1', 'orderby': 'published', 'max-results': '50'})

		# parse first feed
		i = 1
		print 'Now parsing feed ' + str(i) + '...'
		feed = feedparser.parse(r.url)
		csv_writer.writerows(dump_comments(feed, config))

		# get new comments while there's a next url
		next_url = get_next_url(feed)
		while next_url: 
			i += 1
			print 'Now parsing feed ' + str(i) + '...'
			feed = get_next_feed(next_url)
			csv_writer.writerows(dump_comments(feed, config))
			next_url = get_next_url(feed)


def get_next_feed(next_url):
	"""Try a few times to retrieve the feed, wait a few seconds on error""" 
	for attempt in range(5):
		feed = feedparser.parse(next_url)
		if feed.status == 403: 
			sleep = 30 * (attempt + 1)
			print 'Waiting ' + str(sleep) + ' seconds before retrying'
			time.sleep(sleep)
		else: 
			return feed
	else:
		raise ValueError("Feed unreachable")


def get_next_url(feed):
	"""Retrieve the next URL""" 
	next_url = ''
	for l in feed.feed.links:
		if l.rel == 'next':
			next_url = l.href
	return next_url


def dump_comments(feed, config):
	comments = list()
	for entry in feed.entries:
		body = entry.content[0].value.replace('\n', ' ')

		author_feed = feedparser.parse(entry.author_detail.href)
		google_id = get_author_attr(author_feed, 'yt_googleplususerid')
		r = requests.get(config.get('googleplus', 'url') + google_id, 
			params={'key' : config.get('googleplus', 'api_key')})
		j = r.json()

		firstname = j.get('name', {}).get('givenName', '')
		lastname = j.get('name', {}).get('familyName', '')
		location = get_author_attr(author_feed, 'yt_location')
		birthday = j.get('birthday', '')
		gender = j.get('gender', '')
		aboutme = j.get('aboutMe', '')
		organizations = str(j.get('organizations', ''))
		tagline = j.get('tagline', '')
		occupation = j.get('occupation', '')
		skills = j.get('skills', '')
		statistics = get_author_stats(author_feed)

		reply_count = entry.yt_replycount
		activity_id = entry.id.split(':')[-1]
		
		comment = [entry.author, firstname, lastname, location, \
			birthday, gender, aboutme, organizations, tagline, \
			occupation, skills, statistics, reply_count, activity_id, entry.published, body]
		comment = [i.encode('utf-8') for i in comment] 
		comments.append(comment)
	return comments


def get_author_attr(author_feed, attribute):
	try:
		value = getattr(author_feed.entries[0], attribute)
	except (AttributeError, IndexError) as e:
		value = ''
	return value
	

def get_author_stats(author_feed):
	try:
		value = author_feed.entries[0].yt_statistics
	except (AttributeError, IndexError) as e:
		value = ''
	return str(value)


if __name__ == "__main__":
	main()
