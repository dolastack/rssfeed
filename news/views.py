from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import  Article, Feed
from .forms import FeedForm
from background_task import background
from django.utils import timezone
import feedparser, datetime
from .tasks import  save_article


from django.core.cache.backends.base import DEFAULT_TIMEOUT

from django.views.decorators.cache import cache_page
from django.conf import settings
#from rssfeed.settings import display_list

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
display_list = getattr(settings, 'DISPLAY_LIST')


@cache_page(CACHE_TTL)
def articles_list(request):
    time_delta = datetime.datetime.now() - datetime.timedelta(days=20)

    display_list = Article.objects.filter(pulication_date__gte = time_delta)
    display_list = sorted(display_list, key=lambda art : art.pulication_date, reverse=True )

    rowsd = [display_list[x:x+1] for x in range(0, len(display_list), 1)]
    paginator = Paginator(rowsd, 30)
    page = request.GET.get('page')
    try:
        rows = paginator.page(page)
    except PageNotAnInteger:
        rows = paginator.page(1)
    except EmptyPage:
        rows = paginator.page(paginator.num_pages)

    context = {'rows' : rows}
    return render (request, 'news/articles_list.html' , context)

@cache_page(CACHE_TTL)
def feeds_list(request):
    feeds = Feed.objects.all()
    return render(request, 'news/feeds_list.html', {'feeds': feeds})



def new_feed(request):
    """to create new feed"""
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

        return redirect('news.views.feeds_list')
    else:
        form = FeedForm()
        return render(request , 'news/new_feed.html', {'form':form})
