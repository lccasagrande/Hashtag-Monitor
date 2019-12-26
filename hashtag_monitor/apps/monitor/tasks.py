import logging
import json

import channels.layers
import tweepy
from asgiref.sync import async_to_sync
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from rest_framework.renderers import JSONRenderer
from apscheduler.schedulers.background import BackgroundScheduler

from . import twitter_utils as twt_utl
from . import models
from . import serializers


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


@singleton
class MonitorScheduler(BackgroundScheduler):
    pass


def start():
    if settings.DEBUG:
        logging.basicConfig()
        logging.getLogger('apscheduler').setLevel(logging.DEBUG)

    scheduler = MonitorScheduler(daemon=True)
    scheduler.add_job(sync_with_tweeter,
                      'interval',
                      minutes=settings.TWEETER_SYNC_MINUTES,
                      id='tweeter_sync',
                      replace_existing=True)

    scheduler.start()


def get_tweets(hashtag_name):
    channel_layer = channels.layers.get_channel_layer()
    twitter_api = twt_utl.get_twitter_api()
    since_id = models.Tweet.get_since_id(hashtag_name=hashtag_name)
    tweets = twitter_api.search(q=hashtag_name,
                                result_type='recent',
                                count=100,
                                since_id=since_id)
    while tweets['statuses']:
        try:
            new_tweets = models.Tweet.create_from_json(hashtag_name,
                                                               *tweets['statuses'])
        except ObjectDoesNotExist:
            break
        else:
            if not new_tweets:
                break

            async_to_sync(channel_layer.group_send)(
                settings.TWEETER_SYNC_GROUP_NAME,
                {"type": 'sync_new_tweets_from_hashtag', "hashtag": hashtag_name})
            max_id = new_tweets[-1].id - 1
            tweets = twitter_api.search(q=hashtag_name,
                                        result_type='recent',
                                        count=100,
                                        since_id=since_id,
                                        max_id=max_id)


def sync_with_tweeter():
    for hashtag in models.Hashtag.objects.all():
        MonitorScheduler().add_job(lambda: get_tweets(hashtag.name),
                                   id=f"sync_{hashtag.name}",
                                   replace_existing=True)


def get_remaining_tweets_in_background(twitter_api, hashtag_name, max_id, job_name, max_days=1):
    def run_task():
        channel_layer = channels.layers.get_channel_layer()
        tweets = twitter_api.search(q=hashtag_name,
                                    result_type='recent',
                                    count=100,
                                    max_id=max_id)
        while tweets['statuses']:
            try:
                new_tweets = models.Tweet.create_from_json(hashtag_name,
                                                                   *tweets['statuses'])
            except ObjectDoesNotExist:
                break
            else:
                if new_tweets:
                    async_to_sync(channel_layer.group_send)(
                        settings.TWEETER_SYNC_GROUP_NAME,
                        {"type": 'sync_new_tweets_from_hashtag', "hashtag": hashtag_name})
                tweets = twitter_api.search(q=hashtag_name,
                                            result_type='recent',
                                            count=100,
                                            max_id=new_tweets[-1].id - 1)

        return

    return MonitorScheduler().add_job(run_task,
                                      id=job_name,
                                      replace_existing=True)
