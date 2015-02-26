import feedparser
import csv
import time

VIDEO_ID = 'vnKZ4pdSU-s'


def dump_comments(feed):
	comments = list()
	for entry in feed.entries:
		body = entry.content[0].value.replace('\n', ' ')
		
		author_feed = feedparser.parse(entry.author_detail.href)
		firstname = get_author_attr(author_feed, 'yt_firstname')
		lastname = get_author_attr(author_feed, 'yt_lastname')
		location = get_author_attr(author_feed, 'yt_location')
		age = get_author_attr(author_feed, 'yt_age')
		gender = get_author_attr(author_feed, 'yt_gender')
		books = get_author_attr(author_feed, 'yt_books')
		aboutme = get_author_attr(author_feed, 'yt_aboutme')
		company = get_author_attr(author_feed, 'yt_company')
		hobbies = get_author_attr(author_feed, 'yt_hobbies')
		hometown = get_author_attr(author_feed, 'yt_hometown')
		occupation = get_author_attr(author_feed, 'yt_occupation')
		school = get_author_attr(author_feed, 'yt_school')
		statistics = get_author_stats(author_feed)
		
		comment = [entry.author, firstname, lastname, location, \
			age, gender, books, aboutme, company, hobbies, hometown, \
			occupation, school, statistics, entry.published, body]
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
			'age', 'gender', 'books', 'aboutme', 'company', 'hobbies', 'hometown', \
			'occupation', 'school', 'statistics', 'published', 'comment']
		csv_writer.writerow(heading)

		print 'Now parsing feed 1...'
		feed = feedparser.parse('https://gdata.youtube.com/feeds/api/videos/' + VIDEO_ID + '/comments')
		feed, next_url = get_next_url(feed)
		csv_writer.writerows(dump_comments(feed))

		for i in range(25):
			print 'Now parsing feed ' + str(i + 2) + '...'
			feed = feedparser.parse(next_url)
			feed, next_url = get_next_url(feed, next_url)
			csv_writer.writerows(dump_comments(feed))
			
			
def get_next_url(feed, current_url=''):
# Try a few times to get the next feed URL, wait a few seconds on error
	for attempt in range(5):
		try: 
			next_url = ''
			for l in feed.feed.links:
				if l.rel == 'next':
					next_url = l.href
		except AttributeError: 
			print 'Waiting some time before retrying'
			feed = feedparser.parse(current_url)
			time.sleep(5) 
		else: 
			return feed, next_url
	else:
		return None

if __name__ == "__main__":
	main()
