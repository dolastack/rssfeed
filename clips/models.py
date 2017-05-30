from django.db import models
import hashlib
import re
# Create your models here.

class VideoFeed(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField()

class YoutubeFeed(VideoFeed):
    channel = models.CharField(max_length=200)
    external_id = models.CharField(max_length=200)



class Video(models.Model):
    video_feed = models.ForeignKey(VideoFeed, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    publication_date = models.DateTimeField()
    url = models.URLField()
    description = models.TextField()
    video_id = models.CharField(max_length=200, primary_key=True)
    def setID(self):
        idm = hashlib.sha1()
        temp = self.title + self.publication_date + self.url
        idm.update(temp.encode())
        self.video_id = idm.hexdigest()

class YoutubeVideo(Video):
    embed_code = models.CharField(blank=True, max_length=200)
    def get_embed_code(self):
        regex_str = r'(https:\/\/www.youtube.com\/)watch\?v\=(.+)'
        regex = re.compile(regex_str)
        matches = regex.findall(self.url)
        self.embed_code = matches[0][0] + "embed/" + matches[0][1]
