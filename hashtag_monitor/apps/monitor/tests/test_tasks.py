import datetime
import random
import pytz
from asyncio import Future

import tweepy
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from mock import Mock, patch, MagicMock

# Create your tests here.
from ..models import Tweet, User, Hashtag, COLORS_PALETTE
from .. import tasks
from .. import twitter_utils as twt_utl


async def async_magic():
    pass

MagicMock.__await__ = lambda x: async_magic().__await__()


@patch("asgiref.sync.async_to_sync")
@patch("channels.layers")
@patch("apscheduler.schedulers.background.BackgroundScheduler.add_job")
class TasksTests(TestCase):
    @patch("tweepy.API")
    def test_sync_with_tweeter_must_parallelize(self, tweepy_mock, add_job_mock, *args):
        Hashtag.objects.create(name="#Test")
        Hashtag.objects.create(name="#Test2")
        Hashtag.objects.create(name="#Test3")
        tasks.sync_with_tweeter()
        self.assertEqual(3, add_job_mock.call_count)

    def test_get_tweets_should_add_new_tweets(self, add_job_mock, channels_mock, aps_send_mock):
        d = pytz.utc.localize(datetime.datetime.utcnow())
        new_tweets = {"statuses": [
            {
                "id": 1,
                "text": "Test",
                "created_at": d.strftime("%a %b %d %H:%M:%S %z %Y"),
                'entities': {'hashtags': []},
                "user": {
                    'id': 1,
                    'name': "test",
                    'screen_name': "stest",
                    'created_at': d.strftime("%a %b %d %H:%M:%S %z %Y")
                }
            }
        ]}
        tweepy.API.search = MagicMock(return_value=new_tweets)
        Hashtag.objects.create(name="#Test")
        tasks.get_tweets("#Test")
        self.assertEqual(1, Tweet.objects.count())
        self.assertEqual(1, Hashtag.objects.count())
        self.assertEqual(1, User.objects.count())

    @patch("tweepy.API")
    def test_get_remaining_tweets_in_background_should_start_task_in_background(self, tweepy_mock, add_job_mock, *args):
        tasks.get_remaining_tweets_in_background(None, None, None, None)
        self.assertEqual(1, add_job_mock.call_count)
