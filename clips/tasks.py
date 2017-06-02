from .models import YoutubeVideo, YoutubeFeed
import datetime
import feedparser, facebook
from background_task import background


DISPLAYED_VIDEOS = []
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

@background(schedule=500)
def post_video_to_facebook():
    """Post new articles to facebook"""
    print("sending to face")
    NEW_VIDEOS = []
    time_delta = datetime.datetime.now() - datetime.timedelta(minutes=60)

    videos = YoutubeVideo.objects.filter(publication_date__gte = time_delta).order_by("-publication_date")
    for video in videos:
        if video not in DISPLAYED_VIDEOS:
            NEW_VIDEOS.append(video)
            DISPLAYED_VIDEOS.append(video)
    print ("the lenght here" ,len(NEW_VIDEOS), " and ", len(DISPLAYED_VIDEOS))
    if  len(NEW_VIDEOS) > 0:
        #NEW_ARTICLES = sorted(NEW_ARTICLES, key=lambda art : art.publication_date, reverse=True )
        for temp in NEW_VIDEOS:
            attachment = {"name":temp.title ,  "link" :temp.url ,
                          "description": temp.description}
            try:
                status = api.put_wall_post(temp.title, attachment )
            except facebook.GraphAPIError:
                print("There is a problem ", GraphAPIError)


def save_video(feedData, video_feed):
    for entry in feedData.entries:
        video = YoutubeVideo()
        video.title = entry.title
        video.description = entry.description
        video.url = entry.link

        ptime = datetime.datetime(*(entry.published_parsed[0:6]), tzinfo=datetime.timezone.utc)
        ptimetz = ptime.astimezone()
        dateString = ptimetz.strftime('%Y-%m-%d %H:%M:%S')
        video.publication_date = dateString
        video.video_feed = video_feed
        #video.get_embed_code()
        video.setID()
        video.save()

@background(schedule=50)
def youtube_feed_update():
    """background task to get update from feed """
    FEED_LIST = YoutubeFeed.objects.all()
    for youtube_feed in FEED_LIST:

        feedData = feedparser.parse(youtube_feed.full_url)
        if feedData.status == 304:
            # no changes
            pass
        else:
            youtube_feed.title = feedData.feed.title
            youtube_feed.save()
            save_video(feedData, youtube_feed)
