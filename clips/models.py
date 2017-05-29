from django.db import models
import hashlib
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
