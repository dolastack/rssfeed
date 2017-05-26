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

def get_feed_db():
    feeds = Feed.objects.all()

# facebook api
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

@background(schedule=1)
def get_articles_to_display():
    print("whats up")
    time_delta = datetime.datetime.now() + datetime.timedelta(days=30)
    articles = Article.objects.filter(pulication_date__lte = time_delta)
    for article in articles:
        if article not in display_list:
            display_list.append(article)
        else:
            pass
    display_list = sorted(DISPLAY_LIST, key=lambda art : art.pulication_date, reverse=True )


@background(schedule=10)
def post_to_facebook():
    articles = Article.objects.all()
    articles = sorted(articles, key=lambda art : art.pulication_date, reverse=True )
    cfg = {
    "page_id"      : "216809822168608",  # Step 1
    "access_token" : "EAAUQOV9z9PUBAOA9cCLMQm4WnaEzJ413txqNoTYrw9ZBe0LsJszcAZBcVeeAVVerqJYpNihuooF7ZCkCQSZBkGZCJzdPwTKKU5JZAlczNV1kXSYJUh0vo04CvRIvgQVhRZA9qXX2iUQS8XXjfYcFOpVrhx8zLr2ZCCAZD"   # Step 3
    }
    api = get_api(cfg)

    for article in articles:
        try:
            status = api.put_wall_post(article)
            print("sent")
        except GraphAPIError:
            pass

@background(schedule=20)
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
    """save article to database"""
    #timezone = pytz.timezone("America/New_York")
    for entry in dfeedData.entries:
        article = Article()
        article.title = entry.title
        article.url = entry.link
        article.description = entry.description
        d = datetime.datetime(*(entry.published_parsed[0:6]))
        #d = timezone.localize(d)
        dateString = d.strftime('%Y-%m-%d %H:%M:%S')
        article.pulication_date = dateString
        article.feed = dfeed
        article.setID()
        article.save()
