from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import  Article, Feed
from .forms import FeedForm
from background_task import background
from django.utils import timezone

import feedparser, datetime


#from .tasks import feed_update

#Articles to display
#display_set
# Create your views here.

def articles_list(request):

    articles = Article.objects.all()
    #articles = list(set(articles))
    articles = sorted(articles, key=lambda art : art.pulication_date, reverse=True )
    rowsd = [articles[x:x+1] for x in range(0, len(articles), 1)]
    paginator = Paginator(rowsd, 50)

    page = request.GET.get('page')
    try:
        rows = paginator.page(page)
    except PageNotAnInteger:
        rows = paginator.page(1)
    except EmptyPage:
        rows = paginator.page(paginator.num_pages)

    context = {'rows' : rows}

    return render (request, 'news/articles_list.html' , context)

def feeds_list(request):
    feeds = Feed.objects.all()
    #FEED_LIST = feeds
    return render(request, 'news/feeds_list.html', {'feeds': feeds})

def index(request):
    feed_update(repeat=300)
    articles = Article.objects.all()
    articles = sorted(articles, key=lambda art : art.pulication_date, reverse=True )
    rows = [articles[x:x+2] for x in range(0, len(articles), 1)]
    return render (request, 'news/articles_list.html' , {'rows' : rows})

def save_article(dfeedData, dfeed):
    """save article to database"""
    #timezone = pytz.timezone("America/New_York")
    for entry in dfeedData.entries:
        article = Article()
        article.title = entry.title
        article.url = entry.link
        article.description = entry.description
        d = timezone.datetime(*(entry.published_parsed[0:6]))

        #d = timezone.localize(d)
        dateString = d.strftime('%Y-%m-%d %H:%M:%S')
        article.pulication_date = dateString
        article.feed = dfeed
        article.setID()
        article.save()


@background(schedule=10)
def feed_update():
    """background task to get update from feed """

    FEED_LIST = Feed.objects.all()
    for feed in FEED_LIST:
        feedData = feedparser.parse(feed.url)
        if feedData.status == 304:
            # no changes
            pass
        else:
            feed.title = feedData.feed.title
            feed.save()
            save_article(feedData,feed)

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
