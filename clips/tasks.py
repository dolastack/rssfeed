from .models import YoutubeVideo
import datetime

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
        video.get_embed_code()
        video.setID()
        video.save()
