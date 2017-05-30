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

@background(schedule=10)
def post_to_facebook():
    """Post new articles to facebook"""
    print("sending to face")
    NEW_ARTICLES = []
    time_delta = datetime.datetime.now() - datetime.timedelta(minutes=60)
    display_list = Article.objects.filter(pulication_date__gte = time_delta).order_by("-pulication_date")
    for article in articles:
        if article not in DISPLAYED_ARTICLES:
            NEW_ARTICLES.append(article)
            DISPLAYED_ARTICLES.append(article)
    print ("the lenght here" ,len(NEW_ARTICLES), " and ", len(DISPLAYED_ARTICLES))
    if  len(NEW_ARTICLES) > 0:
        NEW_ARTICLES = sorted(NEW_ARTICLES, key=lambda art : art.pulication_date, reverse=True )
        cfg = {
        "page_id"      : "216809822168608",  # Step 1
        "access_token" : "EAAUQOV9z9PUBAOA9cCLMQm4WnaEzJ413txqNoTYrw9ZBe0LsJszcAZBcVeeAVVerqJYpNihuooF7ZCkCQSZBkGZCJzdPwTKKU5JZAlczNV1kXSYJUh0vo04CvRIvgQVhRZA9qXX2iUQS8XXjfYcFOpVrhx8zLr2ZCCAZD"   # Step 3
        }
        api = get_api(cfg)

        for NEW_ARTICLE in NEW_ARTICLES:
            try:
                status = api.put_wall_post(NEW_ARTICLE)
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
    """ get articles from feeds and save article to database"""
    #timezone = pytz.timezone("America/New_York")
    for entry in dfeedData.entries:
        article = Article()
        article.title = entry.title
        article.url = entry.link
        article.description = entry.description
        d = datetime.datetime(*(entry.published_parsed[0:6]))
        #d = timezone.localize(d)
        dateString = d.strftime('%Y-%m-%d %H:%M:%S')
        article.publication_date = dateString
        article.feed = dfeed
        article.setID()
        article.save()
