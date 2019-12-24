import datetime
import random

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

# Create your tests here.
from ..models import Tweet, User, Hashtag, COLORS_PALETTE
from ..queries import TweetQueries, HashtagQueries, UserQueries


class TweetQueriesTest(TestCase):
    def test_get_tweets_per_lang(self):
        a1 = User.objects.create(
            id=1, name="T", screen_name="T", created_at=datetime.datetime.now())
        Tweet.objects.create(id=1,
                             author=a1,
                             created_at=datetime.datetime.now(),
                             text="a",
                             lang='pt')
        Tweet.objects.create(id=2,
                             author=a1,
                             created_at=datetime.datetime.now(),
                             text="a",
                             lang='en')
        Tweet.objects.create(id=3,
                             author=a1,
                             created_at=datetime.datetime.now(),
                             text="a")
        query = TweetQueries.get_tweets_per_lang()

        self.assertIn("pt", query)
        self.assertIn("en", query)
        self.assertIn("others", query)
        self.assertEqual(1, query['pt'])
        self.assertEqual(1, query['en'])
        self.assertEqual(1, query['others'])

    def test_get_tweets_per_lang_for_hashtag(self):
        h1 = Hashtag.objects.create(name="#Test")
        a1 = User.objects.create(
            id=1, name="T", screen_name="T", created_at=datetime.datetime.now())
        t1 = Tweet.objects.create(id=1,
                                  author=a1,
                                  created_at=datetime.datetime.now(),
                                  text="a",
                                  lang='pt')
        t2 = Tweet.objects.create(id=2,
                                  author=a1,
                                  created_at=datetime.datetime.now(),
                                  text="a",
                                  lang='en')
        t1.hashtags.add(h1)
        t2.hashtags.add(h1)
        Tweet.objects.create(id=3,
                             author=a1,
                             created_at=datetime.datetime.now(),
                             text="a")

        query = TweetQueries.get_tweets_per_lang(hashtag_name=h1.name)

        self.assertIn("pt", query)
        self.assertIn("en", query)
        self.assertEqual(1, query['pt'])
        self.assertEqual(1, query['en'])
        self.assertEqual(0, query['others'])

    def test_get_top_tweets_per_lang(self):
        a1 = User.objects.create(
            id=1, name="T", screen_name="T", created_at=datetime.datetime.now())
        Tweet.objects.create(id=1,
                             author=a1,
                             created_at=datetime.datetime.now(),
                             text="a",
                             lang='pt')
        Tweet.objects.create(id=2,
                             author=a1,
                             created_at=datetime.datetime.now(),
                             text="a",
                             lang='en')
        Tweet.objects.create(id=3,
                             author=a1,
                             created_at=datetime.datetime.now(),
                             lang='en',
                             text="a")

        Tweet.objects.create(id=4,
                             author=a1,
                             created_at=datetime.datetime.now(),
                             text="a")

        query = TweetQueries.get_tweets_per_lang(top=1)

        self.assertIn("en", query)
        self.assertIn("others", query)
        self.assertNotIn("pt", query)
        self.assertEqual(2, query['others'])
        self.assertEqual(2, query['en'])

    def test_get_top_tweets_per_lang_for_hashtag(self):
        h1 = Hashtag.objects.create(name="#Test")
        a1 = User.objects.create(
            id=1, name="T", screen_name="T", created_at=datetime.datetime.now())
        t1 = Tweet.objects.create(id=1,
                                  author=a1,
                                  created_at=datetime.datetime.now(),
                                  text="a",
                                  lang='pt')
        t2 = Tweet.objects.create(id=2,
                                  author=a1,
                                  created_at=datetime.datetime.now(),
                                  text="a",
                                  lang='en')
        t3 = Tweet.objects.create(id=3,
                                  author=a1,
                                  created_at=datetime.datetime.now(),
                                  text="a",
                                  lang='en')
        t1.hashtags.add(h1)
        t2.hashtags.add(h1)
        t3.hashtags.add(h1)
        Tweet.objects.create(id=4,
                             author=a1,
                             created_at=datetime.datetime.now(),
                             text="a",
                             lang='fr')

        query = TweetQueries.get_tweets_per_lang(top=1, hashtag_name=h1.name)

        self.assertNotIn("fr", query)
        self.assertIn("en", query)
        self.assertEqual(2, query['en'])
        self.assertEqual(1, query['others'])

    def test_get_hashtag_tweets_per_day(self):
        h1 = Hashtag.objects.create(name="#Test")
        h2 = Hashtag.objects.create(name="#Test2")
        a1 = User.objects.create(
            id=1, name="T", screen_name="T", created_at=datetime.datetime.now())
        t1 = Tweet.objects.create(id=1,
                                  author=a1,
                                  created_at=datetime.datetime.now(),
                                  text="a",
                                  lang='pt')
        t2 = Tweet.objects.create(id=2,
                                  author=a1,
                                  created_at=datetime.datetime.now(),
                                  text="a",
                                  lang='en')
        t3 = Tweet.objects.create(id=3,
                                  author=a1,
                                  created_at=datetime.datetime.now(),
                                  text="a",
                                  lang='en')
        t1.hashtags.add(h1)
        t2.hashtags.add(h1)
        t3.hashtags.add(h1)
        t4 = Tweet.objects.create(id=4,
                                  author=a1,
                                  created_at=datetime.datetime.now(),
                                  text="a",
                                  lang='fr')
        t4.hashtags.add(h2)

        query = TweetQueries.get_hashtag_tweets_per_day()
        date = datetime.datetime.now().strftime("%d/%m")

        self.assertIn(h1.name, query)
        self.assertIn(h2.name, query)
        self.assertIn(date, query[h1.name]["values"])
        self.assertIn(date, query[h2.name]["values"])
        self.assertEqual(3, query[h1.name]["values"][date])
        self.assertEqual(1, query[h2.name]["values"][date])

    def test_get_hashtag_tweets_per_day_with_max_days(self):
        h1 = Hashtag.objects.create(name="#Test")
        h2 = Hashtag.objects.create(name="#Test2")
        a1 = User.objects.create(
            id=1, name="T", screen_name="T", created_at=datetime.datetime.now())
        t1 = Tweet.objects.create(id=1,
                                  author=a1,
                                  created_at=(datetime.datetime.now(
                                  ) - datetime.timedelta(days=2)),
                                  text="a")
        t2 = Tweet.objects.create(id=2,
                                  author=a1,
                                  created_at=(datetime.datetime.now(
                                  ) - datetime.timedelta(days=1)),
                                  text="a")
        t3 = Tweet.objects.create(id=3,
                                  author=a1,
                                  created_at=datetime.datetime.now(),
                                  text="a")
        t1.hashtags.add(h1)
        t2.hashtags.add(h1)
        t3.hashtags.add(h1)
        t4 = Tweet.objects.create(id=4,
                                  author=a1,
                                  created_at=datetime.datetime.now(),
                                  text="a")
        t4.hashtags.add(h2)

        query = TweetQueries.get_hashtag_tweets_per_day(num_days=2)
        date = (datetime.datetime.now()).strftime("%d/%m")
        day_before = (datetime.datetime.now() -
                      datetime.timedelta(days=1)).strftime("%d/%m")

        self.assertIn(h1.name, query)
        self.assertIn(h2.name, query)
        self.assertIn(date, query[h1.name]["values"])
        self.assertIn(date, query[h2.name]["values"])
        self.assertEqual(2, len(query[h1.name]["values"]))
        self.assertEqual(2, len(query[h2.name]["values"]))
        self.assertEqual(1, query[h1.name]["values"][date])
        self.assertEqual(1, query[h1.name]["values"][day_before])
        self.assertEqual(1, query[h2.name]["values"][date])
        self.assertEqual(0, query[h2.name]["values"][day_before])

    def test_get_summary_must_exclude_tweets_without_hashtag(self):
        followers_count = 100
        h1 = Hashtag.objects.create(name="#Test")
        h2 = Hashtag.objects.create(name="#Test2")
        a1 = User.objects.create(
            id=1, name="T", screen_name="T", created_at=datetime.datetime.now(), followers_count=followers_count)
        a2 = User.objects.create(
            id=2, name="T", screen_name="T", created_at=datetime.datetime.now(), followers_count=followers_count)
        a3 = User.objects.create(
            id=3, name="T", screen_name="T", created_at=datetime.datetime.now(), followers_count=followers_count)
        t1 = Tweet.objects.create(id=1,
                                  author=a1,
                                  created_at=(datetime.datetime.now(
                                  ) - datetime.timedelta(days=2)),
                                  text="a")
        t2 = Tweet.objects.create(id=2,
                                  author=a1,
                                  created_at=(datetime.datetime.now(
                                  ) - datetime.timedelta(days=1)),
                                  retweet_count=1,
                                  text="a")
        t3 = Tweet.objects.create(id=3,
                                  author=a3,
                                  created_at=datetime.datetime.now(),
                                  retweeted=t2,
                                  text="a")
        t1.hashtags.add(h1)
        t2.hashtags.add(h1)
        t3.hashtags.add(h1)
        t4 = Tweet.objects.create(id=4,
                                  author=a1,
                                  created_at=datetime.datetime.now(),
                                  text="a")
        summary = TweetQueries.get_summary()
        self.assertEqual(followers_count*3, summary['reach'])
        self.assertEqual(3, summary['tweets_count'])
        self.assertEqual(1, summary['retweet_count'])
        self.assertEqual(3, summary['users'])

    def test_get_summary_for_hashtag(self):
        followers_count = 100
        h1 = Hashtag.objects.create(name="#Test")
        h2 = Hashtag.objects.create(name="#Test2")
        a1 = User.objects.create(
            id=1, name="T", screen_name="T", created_at=datetime.datetime.now(), followers_count=followers_count)
        a2 = User.objects.create(
            id=2, name="T", screen_name="T", created_at=datetime.datetime.now(), followers_count=followers_count)
        a3 = User.objects.create(
            id=3, name="T", screen_name="T", created_at=datetime.datetime.now(), followers_count=followers_count)
        t1 = Tweet.objects.create(id=1,
                                  author=a1,
                                  created_at=(datetime.datetime.now(
                                  ) - datetime.timedelta(days=2)),
                                  text="a")
        t2 = Tweet.objects.create(id=2,
                                  author=a1,
                                  created_at=(datetime.datetime.now(
                                  ) - datetime.timedelta(days=1)),
                                  retweet_count=1,
                                  text="a")
        t3 = Tweet.objects.create(id=3,
                                  author=a3,
                                  created_at=datetime.datetime.now(),
                                  retweeted=t2,
                                  text="a")
        t1.hashtags.add(h1)
        t2.hashtags.add(h1)
        t3.hashtags.add(h2)
        t4 = Tweet.objects.create(id=4,
                                  author=a1,
                                  created_at=datetime.datetime.now(),
                                  text="a")
        t4.hashtags.add(h2)
        summary = TweetQueries.get_summary(h1.name)
        self.assertEqual(followers_count*2, summary['reach'])
        self.assertEqual(2, summary['tweets_count'])
        self.assertEqual(1, summary['retweet_count'])
        self.assertEqual(2, summary['users'])

    def test_get_latest_tweets_must_exclude_tweets_without_hashtag(self):
        h1 = Hashtag.objects.create(name="#Test")
        a1 = User.objects.create(
            id=1, name="T", screen_name="T", created_at=datetime.datetime.now())
        t1 = Tweet.objects.create(id=1,
                                  author=a1,
                                  created_at=(datetime.datetime.now(
                                  ) - datetime.timedelta(days=2)),
                                  text="a")
        t2 = Tweet.objects.create(id=2,
                                  author=a1,
                                  created_at=(datetime.datetime.now(
                                  ) - datetime.timedelta(days=1)),
                                  retweet_count=1,
                                  text="a")
        t3 = Tweet.objects.create(id=3,
                                  author=a1,
                                  created_at=datetime.datetime.now(),
                                  retweeted=t2,
                                  text="a")
        t1.hashtags.add(h1)
        t2.hashtags.add(h1)
        tweets = TweetQueries.get_latest_tweets(count=100)
        self.assertEqual(2, len(tweets))

    def test_get_latest_tweets_with_count(self):
        h1 = Hashtag.objects.create(name="#Test")
        a1 = User.objects.create(
            id=1, name="T", screen_name="T", created_at=datetime.datetime.now())
        t1 = Tweet.objects.create(id=1,
                                  author=a1,
                                  created_at=(datetime.datetime.now(
                                  ) - datetime.timedelta(days=2)),
                                  text="a")
        t2 = Tweet.objects.create(id=2,
                                  author=a1,
                                  created_at=(datetime.datetime.now(
                                  ) - datetime.timedelta(days=1)),
                                  retweet_count=1,
                                  text="a")
        t3 = Tweet.objects.create(id=3,
                                  author=a1,
                                  created_at=datetime.datetime.now(),
                                  retweeted=t2,
                                  text="a")
        t1.hashtags.add(h1)
        t2.hashtags.add(h1)
        t3.hashtags.add(h1)
        tweets = TweetQueries.get_latest_tweets(count=2)
        self.assertEqual(2, len(tweets))

    def test_get_latest_tweets_with_hashtag(self):
        h1 = Hashtag.objects.create(name="#Test")
        h2 = Hashtag.objects.create(name="#Test2")
        a1 = User.objects.create(
            id=1, name="T", screen_name="T", created_at=datetime.datetime.now())
        t1 = Tweet.objects.create(id=1,
                                  author=a1,
                                  created_at=(datetime.datetime.now(
                                  ) - datetime.timedelta(days=2)),
                                  text="a")
        t2 = Tweet.objects.create(id=2,
                                  author=a1,
                                  created_at=(datetime.datetime.now(
                                  ) - datetime.timedelta(days=1)),
                                  retweet_count=1,
                                  text="a")
        t3 = Tweet.objects.create(id=3,
                                  author=a1,
                                  created_at=datetime.datetime.now(),
                                  retweeted=t2,
                                  text="a")
        t1.hashtags.add(h1)
        t2.hashtags.add(h1)
        t3.hashtags.add(h2)
        tweets = TweetQueries.get_latest_tweets(
            count=100, hashtag_name=h2.name)
        self.assertEqual(1, len(tweets))


class HashtagQueriesTests(TestCase):
    def test_get_or_create_must_get_hashtag(self):
        h1 = Hashtag.objects.create(name="#Test")
        h2 = HashtagQueries.get_or_create("#Test")
        self.assertEqual(h1, h2)

    def test_get_or_create_must_create_new_hashtag(self):
        h1 = Hashtag.objects.create(name="#Test")
        h2 = HashtagQueries.get_or_create("#Test2")
        self.assertEqual(2, Hashtag.objects.count())

    def test_get_tweets_per_hashtag(self):
        h1 = Hashtag.objects.create(name="#Test")
        h2 = Hashtag.objects.create(name="#Test2")
        h3 = Hashtag.objects.create(name="#Test3")
        a1 = User.objects.create(
            id=1, name="T", screen_name="T", created_at=datetime.datetime.now())
        t1 = Tweet.objects.create(id=1,
                                  author=a1,
                                  created_at=(datetime.datetime.now(
                                  ) - datetime.timedelta(days=2)),
                                  text="a")
        t2 = Tweet.objects.create(id=2,
                                  author=a1,
                                  created_at=(datetime.datetime.now(
                                  ) - datetime.timedelta(days=1)),
                                  retweet_count=1,
                                  text="a")
        t3 = Tweet.objects.create(id=3,
                                  author=a1,
                                  created_at=datetime.datetime.now(),
                                  retweeted=t2,
                                  text="a")
        t1.hashtags.add(h1)
        t2.hashtags.add(h1)
        t3.hashtags.add(h2)
        query = HashtagQueries.get_tweets_count_per_hashtag()
        self.assertEqual(2, query[h1.name]['count'])
        self.assertEqual(1, query[h2.name]['count'])
        self.assertEqual(0, query[h3.name]['count'])

    def test_get_hashtags_sorted(self):
        h1 = Hashtag.objects.create(name="#C")
        h2 = Hashtag.objects.create(name="#B")
        h3 = Hashtag.objects.create(name="#A")
        hashtags_sorted = HashtagQueries.get_hashtags_sorted()
        self.assertEqual(h3, hashtags_sorted[0])
        self.assertEqual(h2, hashtags_sorted[1])
        self.assertEqual(h1, hashtags_sorted[2])

    def test_delete_if_exists(self):
        h1 = Hashtag.objects.create(name="#Test")
        deleted = HashtagQueries.delete_if_exists('#Test')
        self.assertEqual(0, Hashtag.objects.count())
        self.assertTrue(deleted)

    def test_delete_if_exists_should_not_throw_exception(self):
        deleted = HashtagQueries.delete_if_exists('#Test')
        self.assertFalse(deleted)


class UserQueriesTests():
    def test_update_or_create_should_update_when_user_exist(self):
        a1 = User.objects.create(
            id=1, name="T", screen_name="T", created_at=datetime.datetime.now())
        new_a = User(id=1, name="A", screen_name="B", created_at=datetime.datetime.now(), friends_count=10)

        UserQueries.update_or_create(new_a)
        self.assertEqual(1, User.objects.count())
        self.assertEqual("A", a1.name)
        self.assertEqual("B", a1.screen_name)
        self.assertEqual(10, a1.friends_count)

    def test_update_or_create_should_create_when_user_not_exist(self):
        a1 = User.objects.create(
            id=1, name="T", screen_name="T", created_at=datetime.datetime.now())
        new_a = User(id=2, name="A", screen_name="B", created_at=datetime.datetime.now(), friends_count=10)

        UserQueries.update_or_create(new_a)
        self.assertEqual(2, User.objects.count())
