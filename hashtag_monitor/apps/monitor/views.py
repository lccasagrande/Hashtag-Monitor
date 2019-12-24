from datetime import datetime
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

from .forms import *
from . import twitter_utils as twt_utl
from .models import *
from . import tasks
from . import queries
from . import serializers

from django.db.models.functions import TruncDay

from datetime import timedelta, date


def get_default_context(request, **extra_context):
    summary = queries.TweetQueries.get_summary()

    tweets = queries.TweetQueries.get_latest_tweets(
        count=settings.LATEST_TWEETS_NB)
    tweet_serializer = serializers.TweetSerializer(tweets, many=True)

    hashtags = queries.HashtagQueries.get_hashtags_sorted()
    hashtag_serializer = serializers.HashtagSerializer(hashtags, many=True)

    hashtag_form = HashtagForm()

    tweets_per_hashtag = queries.HashtagQueries.get_tweets_count_per_hashtag()
    tweets_per_day = queries.TweetQueries.get_hashtag_tweets_per_day(num_days=7)
    tweets_per_lang = queries.TweetQueries.get_tweets_per_lang()


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

    tweets = queries.TweetQueries.create_from_json(
        hashtag.name, *tweets['statuses'])
    tasks.get_remaining_tweets_in_background(twitter_api,
                                             hashtag.name,
                                             max_id=tweets[-1].id - 1,
                                             job_name=hashtag.name)


def hashtag_delete(request, name):
    queries.HashtagQueries.delete_if_exists(name)
    return HttpResponseRedirect(reverse('monitor:index'))


def hashtag_create(request):
    context, err = {}, None
    if request.method == 'POST':
        form = HashtagForm(request.POST or None)
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
        form = HashtagForm()
    context = get_default_context(request,
                                  hashtag_form=form,
                                  twitter_error=err)
    return render(request, "monitor/index.html", context)


def index(request, hashtag_form=None):
   # old_selected_hashtag = request.session.get('selected_hashtag', None)
    context = get_default_context(request)

    return render(request, 'monitor/index.html', context)