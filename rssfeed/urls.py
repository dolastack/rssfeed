"""rssfeed URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from news.tasks import post_to_facebook, feed_update
from clips.tasks import youtube_feed_update

#Run the background task to update feed
#get_articles_to_display(repeat=30)
#post_to_facebook(repeat=120)
feed_update(repeat=180)
youtube_feed_update(repeat=300)

urlpatterns = [
    url(r'^news/', include('news.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^', include('news.urls')),
]
