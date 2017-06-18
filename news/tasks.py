from background_task import background
from .models import  Article, Feed
import feedparser, datetime,facebook
import datetime
from django.db.models.signals import post_save
from pytz import timezone

from facebook import GraphAPIError
from celery.task.schedules import crontab
from celery.decorators import periodic_task

import redis
import pickle
# Create your views here.


redis = redis.StrictRedis(host='localhost', port=6379, db=9)

# facebook api
cfg = {
"page_id"      : "216809822168608",  # Step 1
"access_token" : "EAAL3F6fnlNkBAMXksivgtM6XFSZBcbmHRJUG3MogBPz2hsuZAPXaG0ky8C1TbxZAJZAOCgT5V2hFocJlWaBW6VRXiYmEt4twneETXeZCuPvbJxNrhNyZAHKHjNR3upSBU3fmHZAQ3TZA3Ky06HjZAoAy1zHpzYewlM20ZD"   # Step 3
}

DISPLAYED_ARTICLES = []

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
def get_latest_article(sender,  **kwargs):
    #videos = YoutubeVideo.objects.videos_after(minutes=12)
    if kwargs['created']:
        article = kwargs['instance']

        redis.lpush('articles', article.article_id )

#post save signal connect
post_save.connect(get_latest_article, sender=Article)

@periodic_task(run_every=(crontab( minute="*/18")))
def post_to_facebook():
    """Post new articles to facebook"""

    for i in range(5):
        if redis.llen('articles') > 0:

            article = Article.objects.get(article_id = redis.lpop('articles'))

            attachment = {"name":article.title ,  "link" :article.url , "description": article.description}
            try:
                status = api.put_wall_post(article.title, attachment )
            except facebook.GraphAPIError as er:
                print("There is a problem ", str(er))


@periodic_task(run_every=(crontab(minute="*/7")))
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
