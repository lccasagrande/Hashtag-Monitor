import logging
import json

import tweepy
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from rest_framework.renderers import JSONRenderer
from apscheduler.schedulers.background import BackgroundScheduler

from . import twitter_utils as twt_utl
from . import models
from . import consumers
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
    scheduler.add_job(models.Tweet.remove_trash,
                      'interval',
                      minutes=settings.CLEAN_TRASH_FROM_DB_EVERY,
                      id='db_clean_trash',
                      name='db_clean_trash',
                      replace_existing=True)

    scheduler.add_job(sync_with_tweeter,
                      'interval',
                      minutes=settings.TWEETER_SYNC_MINUTES,
                      id='tweeter_sync',
                      name='tweeter_sync',
                      replace_existing=True)
    scheduler.start()


def run_in_background(call, id=None):
    assert callable(call)
    return MonitorScheduler().add_job(call, id=id, name=id, replace_existing=True)


def get_tweets(hashtag_name):
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
            consumers.sync()
            max_id = new_tweets[-1].id - 1
            tweets = twitter_api.search(q=hashtag_name,
                                        result_type='recent',
                                        count=100,
                                        since_id=since_id,
                                        max_id=max_id)


def sync_with_tweeter():
    for hashtag in models.Hashtag.objects.all():
        get_tweets(hashtag.name)


def get_remaining_tweets_in_background(twitter_api, hashtag_name, max_id, history_length, job_name):
    def run_task():
        count = 100
        max_tweets = history_length
        if max_tweets is not None:
            assert max_tweets > 0
            count = min(max_tweets, 100)
            max_tweets -= 100

        tweets = twitter_api.search(q=hashtag_name,
                                    result_type='recent',
                                    count=count,
                                    max_id=max_id)
        while tweets['statuses']:
            try:
                new_tweets = models.Tweet.create_from_json(hashtag_name,
                                                           *tweets['statuses'])
            except ObjectDoesNotExist:
                break
            else:
                if not new_tweets:
                    break

                if max_tweets is not None:
                    count = min(max_tweets, 100)
                    max_tweets -= 100
                if count <= 0:
                    break

                consumers.sync()
                tweets = twitter_api.search(q=hashtag_name,
                                            result_type='recent',
                                            count=count,
                                            max_id=new_tweets[-1].id - 1)
    return run_in_background(run_task, id=job_name)
