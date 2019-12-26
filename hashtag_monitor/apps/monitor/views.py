from datetime import datetime, timedelta, date
import re
import json

import tweepy
from django.db.models import Sum, Count
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction
from django.conf import settings
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import TruncDay

from . import forms
from . import twitter_utils as twt_utl
from . import tasks
from . import models
from . import consumers
from . import serializers


def get_default_context(request, **extra_context):
    summary = models.Tweet.get_summary()

    tweets = models.Tweet.get_latest_tweets(
        count=settings.LATEST_TWEETS_NB)
    tweet_serializer = serializers.TweetSerializer(tweets, many=True)

    hashtags = models.Hashtag.get_hashtags_sorted()
    hashtag_serializer = serializers.HashtagSerializer(hashtags, many=True)

    hashtag_form = forms.HashtagForm()

    tweets_per_hashtag = models.Hashtag.get_tweets_count_per_hashtag()
    tweets_per_day = models.Tweet.get_hashtag_tweets_per_day(num_days=7)
    tweets_per_lang = models.Tweet.get_tweets_per_lang()

    context = {
        'hashtag_list': hashtag_serializer.data,
        'tweet_list': tweet_serializer.data,
        'summary': summary,
        'hashtag_form': hashtag_form,
        'tweets_per_hashtag': tweets_per_hashtag,
        'tweets_per_day': tweets_per_hashtag,
        'tweets_per_lang': tweets_per_lang
    }

    for k, v in extra_context.items():
        context[k] = v

    return context


def get_hashtag_tweets(hashtag):
    twitter_api = twt_utl.get_twitter_api()
    tweets = twitter_api.search(q=hashtag.name,
                                result_type='recent',
                                count=100,
                                include_entities=True)

    tweets = models.Tweet.create_from_json(
        hashtag.name, *tweets['statuses'])
    if tweets:
        consumers.sync()
        tasks.get_remaining_tweets_in_background(twitter_api=twitter_api,
                                             hashtag_name=hashtag.name,
                                             max_id=tweets[-1].id - 1,
                                             history_length=400,
                                             job_name=f"populate_{hashtag.name}")


def hashtag_delete(request, name):
    deleted = models.Hashtag.delete_if_exists(name)
    if deleted:
        consumers.sync()
    return HttpResponseRedirect(reverse('monitor:index'))


def hashtag_create(request):
    context, err = {}, None
    if request.method == 'POST':
        form = forms.HashtagForm(request.POST or None)
        if form.is_valid():
            with transaction.atomic():
                hashtag = form.save()
                try:
                    get_hashtag_tweets(hashtag)
                except tweepy.RateLimitError:
                    err = "We reached the Twitter's rate limit. Wait a few minutes and retry..."
                except tweepy.TweepError:
                    err = "Something happened on your request. Please retry..."
                else:
                    return HttpResponseRedirect(reverse('monitor:index'))
    else:
        form = forms.HashtagForm()
    context = get_default_context(request,
                                  hashtag_form=form,
                                  twitter_error=err)
    return render(request, "monitor/index.html", context)


def index(request, hashtag_form=None):
   # old_selected_hashtag = request.session.get('selected_hashtag', None)
    context = get_default_context(request)

    return render(request, 'monitor/index.html', context)
