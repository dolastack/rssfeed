from background_task import background
from .models import  Article, Feed
import feedparser, datetime, pytz,facebook
import datetime
#from rssfeed.settings import DISPLAY_LIST
#from .views import save_article

from facebook import GraphAPIError
#from .tasks import feed_update

#Articles to display
#display_set
# Create your views here.


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

@background(schedule=300)
def post_to_facebook():
    """Post new articles to facebook"""

    NEW_ARTICLES = []
    time_delta = datetime.datetime.now() - datetime.timedelta(minutes=15)

    articles = Article.objects.filter(publication_date__gte = time_delta).order_by("-publication_date")
    for article in articles:
        if article not in DISPLAYED_ARTICLES:
            NEW_ARTICLES.append(article)
            DISPLAYED_ARTICLES.append(article)

    if  len(NEW_ARTICLES) > 0:
        #NEW_ARTICLES = sorted(NEW_ARTICLES, key=lambda art : art.publication_date, reverse=True )
        for temp in NEW_ARTICLES:

            attachment = {"name":temp.title ,  "link" :temp.url ,
                          "description": temp.description}
            try:
                status = api.put_wall_post(temp.title, attachment)
            except GraphAPIError:
                print("There is a problem ", GraphAPIError)

@background(schedule=60)
def feed_update():
    """background task to get update from feed """
    FEED_LIST = Feed.objects.all()
    for feed in FEED_LIST:
        feedData = feedparser.parse(feed.url)
        if feedData.status == 304:
            # no changes
            pass
        else:
            feed.title = feedData.feed.title
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
        ptime = datetime.datetime(*(entry.published_parsed[0:6]), tzinfo=datetime.timezone.utc)
        ptimetz = ptime.astimezone()
        dateString = ptimetz.strftime('%Y-%m-%d %H:%M:%S')
        article.publication_date = dateString
        article.feed = dfeed
        article.setID()
        article.save()
