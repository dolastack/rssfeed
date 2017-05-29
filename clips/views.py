from django.shortcuts import render
from .models import Video, VideoFeed, YoutubeFeed
# Create your views here.

def videos_list(request):
    videos = Video.objects.all()
    print(videos)
    context = {'videos': videos}
    template = 'base.html'
    return render(request, template, context)

def get_videos():
    videos = Video.objects.all()
    return videos
