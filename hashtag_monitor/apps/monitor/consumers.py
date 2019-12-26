import json

import channels.layers
from asgiref.sync import async_to_sync
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
from channels.generic.websocket import JsonWebsocketConsumer

from . import models
from . import serializers


@receiver(post_delete, sender=models.Hashtag)
def sync_hashtags(sender, instance, using, **kwargs):
    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        settings.TWEETER_SYNC_GROUP_NAME, {"type": 'sync', "message": ""})


class TweeterConsumer(JsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters = {"hashtag": None}

    def connect(self):
        self.accept()
        async_to_sync(self.channel_layer.group_add)(
            settings.TWEETER_SYNC_GROUP_NAME,
            self.channel_name
        )
        self._sync()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            settings.TWEETER_SYNC_GROUP_NAME,
            self.channel_name
        )

    def receive_json(self, text_data):
        if not isinstance(text_data, dict):
            return

        filter_changed = False
        content = text_data.get('content', None)
        content_type = text_data.get('content_type', None)
        if content_type == 'filter':
            for name, flter in content.items():
                if name in self.filters and flter != self.filters[name]:
                    self.filters[name] = flter
                    filter_changed = True

        if filter_changed:
            self._sync()

    def sync_new_tweets_from_hashtag(self, event):
        hashtag_name = event.get('hashtag', None)
        if not hashtag_name:
            return
        if not self.filters['hashtag'] or self.filters['hashtag'] == hashtag_name:
            self._sync()

    def _sync(self):
        # Hashtags
        hashtags = models.Hashtag.objects.all().order_by('name')
        hashtag_serializer = serializers.HashtagSerializer(hashtags, many=True)

        # Latest Tweets
        tweets = models.Tweet.get_latest_tweets(hashtag_name=self.filters['hashtag'],
                                                        count=settings.LATEST_TWEETS_NB)
        tweet_serializer = serializers.TweetSerializer(tweets, many=True)

        # Summary
        summary = models.Tweet.get_summary(
            hashtag_name=self.filters['hashtag'])

        tweets_per_hashtag = models.Hashtag.get_tweets_count_per_hashtag()
        tweets_per_day = models.Tweet.get_hashtag_tweets_per_day(
            num_days=7)
        tweets_per_lang = models.Tweet.get_tweets_per_lang(
            top=3, hashtag_name=self.filters['hashtag'])

        content = {
            'selected_hashtag': self.filters['hashtag'],
            'hashtags': hashtag_serializer.data,
            'tweets': tweet_serializer.data,
            'summary': summary,
            'tweets_per_hashtag': tweets_per_hashtag,
            'tweets_per_day': tweets_per_day,
            'tweets_per_lang': tweets_per_lang
        }

        self.send_json({"content_type": 'sync', "content": content})

    def sync(self, _=None):
        self._sync()
