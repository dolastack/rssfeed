from django.contrib import admin
from .models import Video,YoutubeFeed, VideoFeed
from .forms import YoutubeFeedForm
import feedparser
from .tasks import save_video

class VideoFeedAdmin(admin.ModelAdmin):
    list_display = ('title', 'url')

class YoutubeFeedAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if request.method == "POST":
            form = YoutubeFeedForm(request.POST)
            if form.is_valid():
                youtube_feed = form.save(commit=False)
                existingFeed = YoutubeFeed.objects.filter(external_id = youtube_feed.external_id)
                abs_url = youtube_feed.url + "?channel_id=" + youtube_feed.external_id
                print(abs_url)
                if len(existingFeed) == 0:
                    feedData = feedparser.parse(abs_url)
                    youtube_feed.title =  feedData.feed.title
                    youtube_feed.save()
                    save_video(feedData, youtube_feed)

# Register your models here.
admin.site.register(Video)
admin.site.register(VideoFeed , VideoFeedAdmin)
admin.site.register(YoutubeFeed, YoutubeFeedAdmin)
