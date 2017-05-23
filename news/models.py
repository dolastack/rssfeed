from django.db import models
import hashlib, feedparser
# Create your models here.


class Feed(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Article(models.Model):
    feed = models.ForeignKey(Feed)
    title = models.CharField(max_length=200)
    url = models.URLField()
    description = models.TextField()
    pulication_date = models.DateTimeField()
    article_id = models.CharField(max_length=200, primary_key=True)
    def setID(self):
        idm = hashlib.sha1()
        temp = self.title + self.pulication_date + self.url
        idm.update(temp.encode())
        self.article_id = idm.hexdigest()

    def __str__(self):
        return self.title
