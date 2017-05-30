from .models import YoutubeVideo, YoutubeFeed
import datetime
import feedparser
from background_task import background


def save_video(feedData, video_feed):
    for entry in feedData.entries:
        video = YoutubeVideo()
        video.title = entry.title
        video.description = entry.description
        video.url = entry.link

        d = datetime.datetime(*(entry.published_parsed[0:6]))
        dateString = d.strftime('%Y-%m-%d %H:%M:%S')
        video.publication_date = dateString
        video.video_feed = video_feed
        #video.get_embed_code()
        video.setID()
        video.save()

@background(schedule=20)
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
