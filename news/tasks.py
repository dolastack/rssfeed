from background_task import background
from .models import  Article, Feed
import feedparser, datetime,facebook
import datetime

from pytz import timezone

from facebook import GraphAPIError
from celery.task.schedules import crontab
from celery.decorators import periodic_task

import redis
import pickle
# Create your views here.



redis = redis.StrictRedis(host='localhost', port=6379, db=9)

DISPLAYED_ARTICLES = []
# facebook api
cfg = {
"page_id"      : "216809822168608",  # Step 1
"access_token" : "EAAL3F6fnlNkBAMXksivgtM6XFSZBcbmHRJUG3MogBPz2hsuZAPXaG0ky8C1TbxZAJZAOCgT5V2hFocJlWaBW6VRXiYmEt4twneETXeZCuPvbJxNrhNyZAHKHjNR3upSBU3fmHZAQ3TZA3Ky06HjZAoAy1zHpzYewlM20ZD"   # Step 3
}

def get_api(cfg):
  graph = facebook.GraphAPI(cfg['access_token'])
  # Get page token to post as the page. You can skip
  # the following if you want to post as yourself.
  resp = graph.get_object('me/accounts')
  page_access_token = None
  for page in resp['data']:
    if page['id'] == cfg['page_id']:
      page_access_token = page['access_token']
  graph = facebook.GraphAPI(page_access_token)
  return graph

api = get_api(cfg)

#periodically get new videos
@periodic_task(run_every=(crontab( minute="*/15")))
def get_latest_articles():
    time_delta = datetime.datetime.now() - datetime.timedelta(minutes=15)
    articles = Article.objects.filter(publication_date__gte = time_delta).order_by("-publication_date")
    for article in articles:
        pickled_article = pickle.dumps(article)
        redis.lpush('articles', pickled_article)
    print("the length ", len(DISPLAYED_ARTICLES))

@periodic_task(run_every=(crontab( minute="*/32")))
def post_to_facebook():
    """Post new articles to facebook"""
    print("the length ", len(DISPLAYED_ARTICLES))
    for i in range(2):
        if redis.llen('articles') > 0:
            #get the first element
            #article = DISPLAYED_ARTICLES.pop(0)
            article_unpickled = redis.rpop('articles')
            article = pickle.loads(article_unpickled)

            attachment = {"name":article.title ,  "link" :article.url , "description": article.description}
            try:
                status = api.put_wall_post(article.title, attachment )
            except facebook.GraphAPIError:
                print("There is a problem ", GraphAPIError)


#@background(schedule=60)
@periodic_task(run_every=(crontab(minute="*/10")))
def feed_update():
    """background task to get update from feed """

    FEED_LIST = Feed.objects.all()
    for feed in FEED_LIST:
        feedData = feedparser.parse(feed.url)
        try:
            feed.title = feedData.feed.title
        except AttributeError:
            feed.title = "No title"
        feed.save()
        save_article(feedData,feed)

def save_article(dfeedData, dfeed):
    """ get articles from feeds and save article to database"""
    #timezone = pytz.timezone("America/New_York")
    for entry in dfeedData.entries:
        article = Article()
        article.title = entry.title
        article.url = entry.link
        article.description = entry.description

        utc = timezone('UTC')
        eastern = timezone('US/Eastern')
        utc_dt = datetime.datetime(*(entry.published_parsed[0:6]), tzinfo=utc)
        #timezone naive datetime
        loc_dt = utc_dt.astimezone(eastern)

        #dateString = loc_dt.strftime('%Y-%m-%d %H:%M:%S')
        #timezone('US/Eastern').localize(dateString)
        article.publication_date = loc_dt.strftime('%Y-%m-%d %H:%M:%S')
        article.feed = dfeed
        article.setID()
        article.save()
