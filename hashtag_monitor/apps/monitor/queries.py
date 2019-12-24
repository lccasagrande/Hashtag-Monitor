import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce

from . import models
from . import twitter_utils as twt_utls


class TweetQueries():
    @staticmethod
    def get_tweets_per_lang(top=0, hashtag_name=None):
        if hashtag_name:
            tweets = models.Tweet.objects.filter(hashtags__in=[hashtag_name])
        else:
            tweets = models.Tweet.objects.all()
        query = tweets.values("lang").annotate(count=Count(
            'lang')).values("lang", "count").order_by("-count")
        if top > 0:
            results = {q['lang']: q['count']
                       for q in query[:top] if q['lang'] != 'und'}
            results['others'] = sum(q['count']
                                    for q in query[top:] if q['lang'] != 'und')
            results['others'] += sum(q['count']
                                     for q in query if q['lang'] == 'und')
        else:
            results = {q['lang']: q['count']
                       for q in query if q['lang'] != 'und'}
            results['others'] = sum(q['count']
                                    for q in query if q['lang'] == 'und')
        return results

    @staticmethod
    def get_hashtag_tweets_per_day(num_days=7):
        base = datetime.datetime.today().date()
        tweets_per_day = {
            h.name: {
                "color": h.color,
                "values": {
                    (base - datetime.timedelta(days=x)).strftime("%d/%m"): 0
                    for x in range(num_days-1, 0, -1)
                },
            } for h in models.Hashtag.objects.all()
        }

        query = models.Tweet.objects.filter(created_at__date__gt=base - datetime.timedelta(days=num_days)).values(
            'created_at__date', 'hashtags').annotate(count=Count('created_at__date')).order_by("-count")
        for q in query:
            if q['hashtags'] in tweets_per_day:
                date = q['created_at__date'].strftime("%d/%m")
                tweets_per_day[q['hashtags']]['values'][date] = q['count']
        return tweets_per_day

    @staticmethod
    def get_summary(hashtag_name=None):
        if hashtag_name:
            tweets = models.Tweet.objects.filter(hashtags__in=[hashtag_name])
        else:
            tweets = models.Tweet.objects.exclude(hashtags=None).all()
        summary = tweets.aggregate(reach=Coalesce(Sum('author__followers_count'), 0),
                                   tweets_count=Count('pk'),
                                   retweet_count=Coalesce(
                                       Sum('retweet_count'), 0),
                                   users=Count('author'))
        return summary

    @staticmethod
    def get_latest_tweets(hashtag_name=None, count=100):
        if hashtag_name:
            tweets = models.Tweet.objects.filter(
                hashtags__in=[hashtag_name]).order_by('-created_at')[:count]
        else:
            tweets = models.Tweet.objects.exclude(
                hashtags=None).all().order_by('-created_at')[:count]
        return tweets

    @staticmethod
    def create_from_json(hashtag_name, *tweeter_json):
        def create_tweet(data, hashtag=None):
            quoted_tweet = data.get('quoted_status', None)
            retweeted = data.get('retweeted_status', None)
            extended_tweet = data.get('extended_tweet', None)
            hashtags = [models.Hashtag.objects.get(
                pk=hashtag)] if hashtag else []

            if quoted_tweet:
                quoted_tweet, _ = create_tweet(quoted_tweet, None)
                if quoted_tweet.hashtags.exists():
                    hashtags.extend(quoted_tweet.hashtags.all())

            if retweeted:
                retweeted, _ = create_tweet(retweeted, hashtag_name)
                if retweeted.hashtags.exists():
                    hashtags.extend(retweeted.hashtags.all())

            if extended_tweet:
                text = extended_tweet.get('full_text', data['text'])
                mentioned_hashtags = extended_tweet['entities']['hashtags']
            else:
                text = data['text']
                mentioned_hashtags = data['entities']['hashtags']

            for h in mentioned_hashtags:
                ht = models.Hashtag.objects.filter(
                    pk__iexact=f"#{h['text']}").first()
                if ht:
                    hashtags.append(ht)

            created_at = twt_utls.convert_to_datetime(data['created_at'])
            author = UserQueries.create_from_json(data['user'])
            tweet, created = models.Tweet.objects.get_or_create(
                pk=data['id'],
                defaults={
                    'author': author,
                    'quoted_tweet': quoted_tweet,
                    'retweeted': retweeted,
                    'created_at': created_at,
                    'text': text,
                    'lang': data.get('lang', "und"),
                    'retweet_count': data.get('retweet_count', 0),
                    'source': data.get('source', None),
                    'url': None,
                    'filter_level': data.get('filter_level', None)
                })
            for h in hashtags:
                tweet.hashtags.add(h)
            return tweet, created

        tweets = []
        with transaction.atomic():
            for j in tweeter_json:
                tweet, created = create_tweet(j, hashtag_name)
                if created:
                    tweets.append(tweet)
        return tweets


class HashtagQueries():
    def get_or_create(hashtag_name):
        try:
            hashtag = models.Hashtag.objects.get(pk=hashtag_name)
        except ObjectDoesNotExist:
            hashtag = models.Hashtag.objects.create(pk=hashtag_name)
        return hashtag

    @staticmethod
    def get_tweets_count_per_hashtag():
        query = models.Hashtag.objects.all().annotate(
            count=Count('tweet')).values().order_by('-count')
        return {q['name']: {'count': q['count'], 'color': q['color']} for q in query}

    @staticmethod
    def get_hashtags_sorted():
        return models.Hashtag.objects.all().order_by('name')

    @staticmethod
    def delete_if_exists(hashtag_name):
        try:
            hashtag = models.Hashtag.objects.get(pk=hashtag_name)
            with transaction.atomic():
                hashtag.delete()
        except ObjectDoesNotExist:
            return False
        else:
            return True


class UserQueries():
    @staticmethod
    def update_or_create(author):
        usr, _ = models.User.objects.update_or_create(
            pk=author.id,
            defaults={
                'name': author.name,
                'screen_name': author.screen_name,
                'location': author.location,
                'friends_count': author.friends_count,
                'followers_count': author.followers_count,
                'created_at': author.created_at,
                'profile_image': author.profile_image_url_https
            })
        return usr

    @staticmethod
    def create_from_json(twitter_json):
        created_at = twt_utls.convert_to_datetime(twitter_json['created_at'])
        usr, _ = models.User.objects.update_or_create(
            pk=twitter_json['id'],
            defaults={
                'name': twitter_json['name'],
                'screen_name': twitter_json['screen_name'],
                'friends_count': twitter_json.get('friends_count', 0),
                'followers_count': twitter_json.get('followers_count', 0),
                'created_at': created_at,
                'profile_image': twitter_json.get('profile_image_url_https', None)
            })
        return usr
