from .models import YoutubeVideo, YoutubeFeed
import datetime
import feedparser, facebook

from pytz import timezone
from celery.task.schedules import crontab
from celery.decorators import periodic_task

import pickle, redis

DISPLAYED_VIDEOS = []
# facebook api

redis = redis.StrictRedis(host='localhost', port=6379, db=9)

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
@periodic_task(run_every=(crontab( minute="*/18")))
def get_latest_videos():
    time_delta = datetime.datetime.now() - datetime.timedelta(minutes=20)
    videos = YoutubeVideo.objects.filter(publication_date__gte = time_delta).order_by("-publication_date")
    for video in videos:

        video_pickled = pickle.dumps(video)
        redis.lpush('videos', video_pickled)

@periodic_task(run_every=(crontab( minute="*/39")))
def post_video_to_facebook():
    """Post new articles to facebook"""
    for i in range(2):
        if redis.llen('videos') > 0:
            #get the first element
            video_unpickled = redis.rpop('videos')
            video = pickle.loads(video_unpickled)

            attachment = {"name":video.title ,  "link" :video.url , "description": video.description}
            try:
                status = api.put_wall_post(video.title, attachment )
            except facebook.GraphAPIError:
                print("There is a problem ", GraphAPIError)


def save_video(feedData, video_feed):
    for entry in feedData.entries:
        video = YoutubeVideo()
        video.title = entry.title
        video.description = entry.description
        video.url = entry.link

        utc = timezone('UTC')
        eastern = timezone('US/Eastern')
        utc_dt = datetime.datetime(*(entry.published_parsed[0:6]),  tzinfo=utc)
        #timezone naive datetime
        loc_dt = utc_dt.astimezone(eastern)

        #dateString = loc_dt.strftime('%Y-%m-%d %H:%M:%S')
        #timezone('US/Eastern').localize(dateString)
        video.publication_date = loc_dt.strftime('%Y-%m-%d %H:%M:%S')

        video.video_feed = video_feed
        #video.get_embed_code()
        video.setID()
        video.save()

#@background(schedule=50)
@periodic_task(run_every=(crontab(minute="*/15")))
def youtube_feed_update():
    """background task to get update from feed """
    FEED_LIST = YoutubeFeed.objects.all()
    for youtube_feed in FEED_LIST:
        feedData = feedparser.parse(youtube_feed.full_url)
        try:
            youtube_feed.title = feedData.feed.title
        except AttributeError:
            youtube_feed.title = "No title"
        youtube_feed.save()
        save_video(feedData, youtube_feed)
