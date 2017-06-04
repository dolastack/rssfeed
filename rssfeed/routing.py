from news.tasks import post_to_facebook, feed_update

channel_routing = [route("background-feed_update" ,feed_update )]
