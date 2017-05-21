from django.contrib import admin
from .models import Article, Feed
# Register your models here.

admin.site.register(Feed)
admin.site.register(Article)
