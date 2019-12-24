import datetime

import tweepy
from django.conf import settings



def get_twitter_api():
    auth = tweepy.OAuthHandler(
        settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
    auth.set_access_token(settings.TWITTER_ACCESS_TOKEN,
                          settings.TWITTER_ACCESS_TOKEN_SECRET)
    return tweepy.API(auth, wait_on_rate_limit=True, parser=tweepy.parsers.JSONParser())

def convert_to_datetime(twitter_time):
    return datetime.datetime.strptime(twitter_time, "%a %b %d %H:%M:%S %z %Y")