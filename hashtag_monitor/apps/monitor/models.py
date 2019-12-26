import datetime

import numpy as np

from django.db.models.signals import pre_delete, post_save, post_delete
from django.dispatch import receiver
from django.db import models, transaction
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from . import twitter_utils as twt_utls


def validate_not_empty(value):
    if len(value) == 0:
        raise ValidationError("Empty values are not allowed.")


def validate_hashtag_not_empty(value):
    if len(value) < 2:
        raise ValidationError(
            "A hashtag must contain at least 1 character besides #.")


def validate_is_hashtag(value):
    if not isinstance(value, str) or not value.startswith("#"):
        raise ValidationError(
            f'{value} is not a hashtag. Did you mean #{value}?.')


def validate_is_not_duplicate(value):
    try:
        if Hashtag.objects.get(name__iexact=value):
            raise ValidationError('A hashtag is not case sensitive')
    except ObjectDoesNotExist:
        pass


def validate_nb_hashtag(value):
    max_nb = 10
    if Hashtag.objects.count() == max_nb:
        raise ValidationError(f"The maximum number of hashtags is {max_nb}.")


COLORS_PALETTE = ['#3b465e', '#2e3951', '#1c2a48', '#1c2331', '#e53935', '#d32f2f', '#c62828', '#b71c1c', '#d81b60', '#c2185b', '#ad1457', '#880e4f', '#8e24aa', '#7b1fa2', '#6a1b9a', '#4a148c', '#5e35b1', '#512da8', '#4527a0', '#311b92', '#3949ab', '#303f9f', '#283593', '#1a237e', '#1e88e5', '#1976d2', '#1565c0', '#0d47a1', '#039be5', '#0288d1', '#0277bd', '#01579b', '#00acc1', '#0097a7', '#00838f', '#006064', '#00897b', '#00796b', '#00695c', '#004d40',
                  '#43a047', '#388e3c', '#2e7d32', '#1b5e20', '#7cb342', '#689f38', '#558b2f', '#33691e', '#c0ca33', '#afb42b', '#9e9d24', '#827717', '#fdd835', '#fbc02d', '#f9a825', '#f57f17', '#ffb300', '#ffa000', '#ff8f00', '#ff6f00', '#fb8c00', '#f57c00', '#ef6c00', '#e65100', '#f4511e', '#e64a19', '#d84315', '#bf360c', '#6d4c41', '#5d4037', '#4e342e', '#3e2723', '#546e7a', '#455a64', '#37474f', '#263238', '#757575', '#616161', '#424242', '#212121']


class Hashtag(models.Model):
    name = models.CharField('Hashtag name',
                            primary_key=True,
                            max_length=500,
                            blank=False,
                            validators=[validate_is_hashtag,
                                        validate_nb_hashtag,
                                        validate_is_not_duplicate,
                                        validate_hashtag_not_empty])
    color = models.CharField("Color class",
                             choices=[(c, c) for c in COLORS_PALETTE],
                             max_length=50,
                             default=None,
                             validators=[validate_not_empty],
                             null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.color:
            self.color = np.random.choice(COLORS_PALETTE)

    def __str__(self):
        return f"{self.name}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.full_clean()
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    @classmethod
    def get_or_create(cls, hashtag_name):
        try:
            hashtag = cls.objects.get(pk=hashtag_name)
        except ObjectDoesNotExist:
            hashtag = cls.objects.create(pk=hashtag_name)
        return hashtag

    @classmethod
    def get_tweets_count_per_hashtag(cls):
        query = cls.objects.all().annotate(
            count=Count('tweet')).values().order_by('-count')
        return {q['name']: {'count': q['count'], 'color': q['color']} for q in query}

    @classmethod
    def get_hashtags_sorted(cls):
        return cls.objects.all().order_by('name')

    @classmethod
    def delete_if_exists(cls, hashtag_name):
        try:
            hashtag = cls.objects.get(pk=hashtag_name)
            with transaction.atomic():
                hashtag.delete()
        except ObjectDoesNotExist:
            return False
        else:
            return True


class User(models.Model):
    id = models.BigIntegerField('Twitter user id',
                                primary_key=True)
    name = models.CharField('Username',
                            max_length=100,
                            blank=False,
                            default=None,
                            validators=[validate_not_empty])

    screen_name = models.CharField('Username',
                                   max_length=100, blank=False,
                                   default=None,
                                   validators=[validate_not_empty])

    created_at = models.DateField("Date created", null=False, blank=False)

    friends_count = models.IntegerField('Friends count', default=0)

    followers_count = models.IntegerField('Followers count', default=0)

    profile_image = models.URLField("Profile image url",
                                    default=None,
                                    null=True,
                                    blank=True)

    def __str__(self):
        return f"{self.name}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.full_clean()
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)


    @classmethod
    def update_or_create(cls, author):
        usr, _ = cls.objects.update_or_create(
            pk=author.id,
            defaults={
                'name': author.name,
                'screen_name': author.screen_name,
                'created_at': author.created_at,
                'friends_count': author.friends_count,
                'followers_count': author.followers_count,
                'profile_image': author.profile_image
            })
        return usr

    @classmethod
    def create_from_json(cls, twitter_json):
        created_at = twt_utls.convert_to_datetime(twitter_json['created_at'])
        usr, _ = cls.objects.update_or_create(
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

class Tweet(models.Model):
    id = models.BigIntegerField('Twitter tweet id', primary_key=True)
    quoted_tweet = models.ForeignKey('self',
                                     on_delete=models.CASCADE,
                                     null=True,
                                     related_name='tweet_quoted',
                                     default=None,
                                     blank=True)
    retweeted = models.ForeignKey('self',
                                  on_delete=models.CASCADE,
                                  null=True,
                                  related_name='tweet_retweeted',
                                  default=None,
                                  blank=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    hashtags = models.ManyToManyField(Hashtag)

    created_at = models.DateTimeField("Date created")

    text = models.TextField("Text", blank=False, default=None)

    lang = models.CharField("Language",
                            max_length=3,
                            default='und',
                            null=False,
                            blank=False)

    retweet_count = models.IntegerField("Retweets", default=0)

    source = models.CharField("Source",
                              max_length=500,
                              null=True,
                              default=None,
                              blank=True)

    url = models.CharField("Link to tweet",
                           max_length=100,
                           null=True,
                           default=None,
                           blank=True)

    filter_level = models.CharField("Twitter filter level",
                                    max_length=50,
                                    default=None,
                                    null=True,
                                    blank=True)

    def __str__(self):
        """Returns a string representation of a message."""
        return f"{self.author.name} published '{self.text}' on {self.created_at.strftime('%A, %d %B, %Y at %X')}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.retweeted is not None:
            self.retweet_count = 0

        self.full_clean()
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    @classmethod
    def get_since_id(cls, hashtag_name=None):
        try:
            if hashtag_name:
                return cls.objects.filter(hashtags__in=[hashtag_name]).latest('pk').id
            else:
                return cls.objects.latest('pk').id
        except ObjectDoesNotExist:
            return None

    @classmethod
    def get_max_id(cls, hashtag_name=None):
        try:
            if hashtag_name:
                return cls.objects.filter(hashtags__in=[hashtag_name]).earliest('pk').id
            else:
                return cls.objects.earliest('pk').id
        except ObjectDoesNotExist:
            return None

    @classmethod
    def get_tweets_per_lang(cls, top=0, hashtag_name=None):
        if hashtag_name:
            tweets = cls.objects.filter(hashtags__in=[hashtag_name])
        else:
            tweets = cls.objects.all()
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

    @classmethod
    def get_hashtag_tweets_per_day(cls, num_days=7):
        base = datetime.datetime.today().date()
        tweets_per_day = {
            h.name: {
                "color": h.color,
                "values": {
                    (base - datetime.timedelta(days=x)).strftime("%d/%m"): 0
                    for x in range(num_days-1, 0, -1)
                },
            } for h in Hashtag.objects.all()
        }

        query = cls.objects.filter(created_at__date__gt=base - datetime.timedelta(days=num_days)).values(
            'created_at__date', 'hashtags').annotate(count=Count('created_at__date')).order_by("-count")
        for q in query:
            if q['hashtags'] in tweets_per_day:
                date = q['created_at__date'].strftime("%d/%m")
                tweets_per_day[q['hashtags']]['values'][date] = q['count']
        return tweets_per_day

    @classmethod
    def get_summary(cls, hashtag_name=None):
        if hashtag_name:
            tweets = cls.objects.filter(hashtags__in=[hashtag_name])
        else:
            tweets = cls.objects.exclude(hashtags=None).all()
        summary = tweets.aggregate(reach=Coalesce(Sum('author__followers_count'), 0),
                                   tweets_count=Count('pk'),
                                   retweet_count=Coalesce(
                                       Sum('retweet_count'), 0),
                                   users=Count('author'))
        return summary

    @classmethod
    def get_latest_tweets(cls, hashtag_name=None, count=100):
        if hashtag_name:
            tweets = cls.objects.filter(
                hashtags__in=[hashtag_name]).order_by('-created_at')[:count]
        else:
            tweets = cls.objects.exclude(
                hashtags=None).all().order_by('-created_at')[:count]
        return tweets

    @classmethod
    def create_from_json(cls, hashtag_name, *tweeter_json):
        def create_tweet(data, hashtag=None):
            quoted_tweet = data.get('quoted_status', None)
            retweeted = data.get('retweeted_status', None)
            extended_tweet = data.get('extended_tweet', None)
            hashtags = [Hashtag.objects.get(
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
                ht = Hashtag.objects.filter(
                    pk__iexact=f"#{h['text']}").first()
                if ht:
                    hashtags.append(ht)

            created_at = twt_utls.convert_to_datetime(data['created_at'])
            author = User.create_from_json(data['user'])
            tweet, created = cls.objects.get_or_create(
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


@receiver(pre_delete, sender=Hashtag)
def cascade_delete_tweets(sender, instance, **kwargs):
    for tweet in instance.tweet_set.all():
        if tweet.hashtags.count() <= 1:
            tweet.delete()

@receiver(post_delete, sender=Tweet)
def cascade_delete_users(sender, instance, **kwargs):
    if instance.author.tweet_set.count() == 0:
        instance.author.delete()
