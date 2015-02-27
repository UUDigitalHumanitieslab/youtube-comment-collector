import feedparser
import requests
import csv
import time

VIDEO_ID = 'vnKZ4pdSU-s'
API_KEY = ''
GPLUS = 'https://www.googleapis.com/plus/v1/people/'


def dump_comments(feed):
	comments = list()
	for entry in feed.entries:
		body = entry.content[0].value.replace('\n', ' ')
		
		author_feed = feedparser.parse(entry.author_detail.href)
		location = get_author_attr(author_feed, 'yt_location')
		gender = get_author_attr(author_feed, 'yt_gender')
		books = get_author_attr(author_feed, 'yt_books')
		aboutme = get_author_attr(author_feed, 'yt_aboutme')
		company = get_author_attr(author_feed, 'yt_company')
		hobbies = get_author_attr(author_feed, 'yt_hobbies')
		hometown = get_author_attr(author_feed, 'yt_hometown')
		occupation = get_author_attr(author_feed, 'yt_occupation')
		school = get_author_attr(author_feed, 'yt_school')
		statistics = get_author_stats(author_feed)
		reply_count = entry.yt_replycount
		activity_id = entry.id.split(':')[-1]

		r = requests.get(GPLUS + entry.yt_googleplususerid, params={'key' : API_KEY})
		j = r.json()
		firstname = j.get('name', {}).get('givenName', '')
		lastname = j.get('name', {}).get('familyName', '')
		birthday = j.get('birthday', '')
		gender = j.get('gender', '')
		
		comment = [entry.author, firstname, lastname, location, \
			birthday, gender, books, aboutme, company, hobbies, hometown, \
			occupation, school, statistics, reply_count, activity_id, entry.published, body]
		comment = [i.encode('utf-8') for i in comment] # todo: correct?
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
	

def main():
	with open('comments.csv', 'wb') as csv_file:
		csv_writer = csv.writer(csv_file, dialect='excel', delimiter=';', quoting=csv.QUOTE_MINIMAL)
		heading = ['username', 'firstname', 'lastname', 'location', \
			'birthday', 'gender', 'books', 'aboutme', 'company', 'hobbies', 'hometown', \
			'occupation', 'school', 'statistics', 'replycount', 'activity_id', 'published', 'comment']
		csv_writer.writerow(heading)

		print 'Now parsing feed 1...'
		feed = feedparser.parse('https://gdata.youtube.com/feeds/api/videos/' + VIDEO_ID + '/comments?v=2.1')
		csv_writer.writerows(dump_comments(feed))
		next_url = get_next_url(feed)

		for i in range(0):
			print 'Now parsing feed ' + str(i + 2) + '...'
			feed = get_next_feed(next_url)
			csv_writer.writerows(dump_comments(feed))
			next_url = get_next_url(feed, next_url)


def get_next_feed(next_url):
	"""Try a few times to get the next feed URL, wait a few seconds on error""" 
	for attempt in range(5):
		feed = feedparser.parse(next_url)
		if feed.status == 403: 
			print 'Waiting 20 seconds before retrying'
			time.sleep(20)
		else: 
			return feed
	else:
		raise ValueError("Feed unreachable")


def get_next_url(feed, current_url=''):
	"""Try a few times to get the next feed URL, wait a few seconds on error""" 
	next_url = ''
	for l in feed.feed.links:
		if l.rel == 'next':
			next_url = l.href
	return next_url


if __name__ == "__main__":
	main()
