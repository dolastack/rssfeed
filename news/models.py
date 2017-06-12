from django.db import models
import hashlib, feedparser
# Create your models here.
import datetime

class Feed(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class ArticlesManager(models.Manager):
    def articles_after(self, **kwargs):
        """get articles produced after a duration of time"""
        if kwargs is not None:
            for duration, value in kwargs.items():
                if duration == "minutes":
                    time_delta = datetime.datetime.now() - datetime.timedelta(minutes=value)
                elif duration == "days":
                    time_delta = datetime.datetime.now() - datetime.timedelta(days=value)
                elif duration == "hours":
                    time_delta = datetime.datetime.now() - datetime.timedelta(hours=value)
                return self.filter(publication_date__gte = time_delta).order_by("-publication_date")

class Article(models.Model):
    feed = models.ForeignKey(Feed)
    title = models.CharField(max_length=200)
    url = models.URLField()
    description = models.TextField()
    publication_date = models.DateTimeField()
    article_id = models.CharField(max_length=200, primary_key=True)
    objects = ArticlesManager()
    
    def setID(self):
        idm = hashlib.sha1()
        temp = self.title + self.publication_date + self.url
        idm.update(temp.encode())
        self.article_id = idm.hexdigest()

    def __str__(self):
        return self.title
