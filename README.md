# youtube-comment-collector
The script *youtube.py* collects comments and metadata from [YouTube](https://www.youtube.com) 
videos using the (now deprecated) [V2 API](https://developers.google.com/youtube/2.0/developers_guide_protocol). 
The script uses the [feedparser package](https://pythonhosted.org/feedparser/) for parsing the YouTube feeds, 
and the [requests](http://docs.python-requests.org/) library for parsing the Google Plus JSON responses. 
Run the script with `python youtube.py` after you have set your API key in `example.cfg`. 