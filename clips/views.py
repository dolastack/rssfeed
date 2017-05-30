from django.shortcuts import render
from .models import YoutubeVideo, VideoFeed, YoutubeFeed
# Create your views here.
import datetime

def videos_list(request):
    videos = YoutubeVideo.objects.all()
    context = {'videos': videos}
    template = 'base.html'
    return render(request, template, context)

def get_videos():
    time_delta = datetime.datetime.now() - datetime.timedelta(days=7)
    videos = YoutubeVideo.objects.filter(publication_date__gte = time_delta).order_by("-publication_date")
    return videos
