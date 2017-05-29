from django.contrib import admin
from .models import Article, Feed
from .forms import FeedForm
# Register your models here.
import feedparser
from .tasks import save_article

class FeedAdmin(admin.ModelAdmin):
    list_display = ('title', 'url')
    def save_model(self, request, obj, form, change ):
            if request.method == "POST":
                form = FeedForm(request.POST)
                if form.is_valid():
                    feed = form.save(commit=False)

                    existingFeed = Feed.objects.filter(url = feed.url)
                    if len(existingFeed) == 0:
                        feedData = feedparser.parse(feed.url)
                        feed.title = feedData.feed.title
                        feed.save()
                        save_article(feedData, feed)

admin.site.register(Feed, FeedAdmin)
admin.site.register(Article)
