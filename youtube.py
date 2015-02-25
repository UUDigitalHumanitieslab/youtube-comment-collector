import feedparser
import csv
import time

VIDEO_ID = 'vnKZ4pdSU-s'


def dump_comments(feed):
    comments = list()
    for entry in feed.entries:
        value = entry.content[0].value.replace('\n', ' ')
        comment = [entry.author, str(get_nationality(entry)), entry.published, value]
        comment = [i.encode('utf-8') for i in comment]
        comments.append(comment)
    return comments


def get_nationality(entry):
    feed = feedparser.parse(entry.author_detail.href)
    try:
        location = feed.entries[0].yt_location
    except (AttributeError, IndexError) as e:
        location = 'unknown'
    return location


def main():
    with open('comments.csv', 'wb') as csv_file:
        csv_writer = csv.writer(csv_file, dialect='excel', delimiter=';', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['username', 'location', 'published', 'comment'])

        print 'Now parsing feed 1...'
        feed = feedparser.parse('https://gdata.youtube.com/feeds/api/videos/' + VIDEO_ID + '/comments')
        csv_writer.writerows(dump_comments(feed))

        for i in range(25):
            next_url = ''
            for l in feed.feed.links:
                if l.rel == 'next':
                    next_url = l.href

            time.sleep(5)  # Wait 5 seconds to prevent reaching request limit
            print 'Now parsing feed ' + str(i + 2) + '...'
            feed = feedparser.parse(next_url)
            csv_writer.writerows(dump_comments(feed))

if __name__ == "__main__":
    main()
