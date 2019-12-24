import datetime
import random

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

# Create your tests here.
from ..models import Tweet, User, Hashtag, COLORS_PALETTE


class HashtagTests(TestCase):
    def test_hashtag_is_case_insensitive(self):
        h = Hashtag.objects.create(name="#Test")
        with self.assertRaises(ValidationError) as cm:
            Hashtag.objects.create(name="#TeSt")

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('name', cm.exception.message_dict)
        self.assertIn('A hashtag is not case sensitive', msgs[0])

    def test_duplicate_hashtag_must_raise_exception(self):
        h = Hashtag.objects.create(name="#Test")
        with self.assertRaises(ValidationError) as cm:
            Hashtag.objects.create(name="#Test")

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('name', cm.exception.message_dict)
        self.assertIn('A hashtag is not case sensitive', msgs[0])

    def test_invalid_hashtag_name_must_raise_exception(self):
        with self.assertRaises(ValidationError) as cm:
            Hashtag.objects.create(name="Test")
        msgs = list(cm.exception.message_dict.values())
        self.assertIn('name', cm.exception.message_dict)
        self.assertIn('Test is not a hashtag. Did you mean #Test?.', msgs[0])

    def test_hashtag_name_is_not_string_must_raise_exception(self):
        with self.assertRaises(ValidationError) as cm:
            Hashtag.objects.create(name=12)
        msgs = list(cm.exception.message_dict.values())
        self.assertIn('name', cm.exception.message_dict)
        self.assertIn('12 is not a hashtag. Did you mean #12?.', msgs[0])

    def test_hashtag_too_long_must_raise_exception(self):
        h = "#" + "".join('1' for _ in range(500))
        with self.assertRaises(ValidationError) as cm:
            Hashtag.objects.create(name=h)

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('name', cm.exception.message_dict)
        self.assertIn(
            'Ensure this value has at most 500 characters (it has 501).', msgs[0])

    def test_incomplete_hashtag_must_raise_exception(self):
        with self.assertRaises(ValidationError) as cm:
            Hashtag.objects.create(name="#")

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('name', cm.exception.message_dict)
        self.assertIn(
            'A hashtag must contain at least 1 character besides #.', msgs[0])

    def test_empty_hashtag_must_raise_exception(self):
        with self.assertRaises(ValidationError) as cm:
            Hashtag.objects.create(name="")

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('name', cm.exception.message_dict)
        self.assertIn('This field cannot be blank.', msgs[0])

    def test_hashtag_must_have_a_color(self):
        h = Hashtag.objects.create(name="#Test")
        self.assertIsNotNone(h.color)

    def test_hashtag_color_must_be_choosen_from_pallete(self):
        h = Hashtag.objects.create(name="#Test")
        self.assertIn(h.color, COLORS_PALETTE)


class UserTests(TestCase):
    def test_id_must_accept_bigint(self):
        big_int = 9223372036854775807
        user = User.objects.create(id=big_int,
                                   name="Opa",
                                   screen_name="Test",
                                   created_at=datetime.datetime.now())

        self.assertEqual(big_int, user.id)

    def test_name_cannot_be_empty(self):
        with self.assertRaises(ValidationError) as cm:
            h = User.objects.create(id=123,
                                    name="",
                                    screen_name="Test",
                                    created_at=datetime.datetime.now())

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('name', cm.exception.message_dict)
        self.assertIn('This field cannot be blank.', msgs[0])

    def test_name_cannot_be_null(self):
        with self.assertRaises(ValidationError) as cm:
            h = User.objects.create(id=123,
                                    screen_name="Test",
                                    created_at=datetime.datetime.now())

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('name', cm.exception.message_dict)
        self.assertIn('This field cannot be null.', msgs[0])

    def test_screen_name_cannot_be_null(self):
        with self.assertRaises(ValidationError) as cm:
            h = User.objects.create(id=123,
                                    name="Test",
                                    created_at=datetime.datetime.now())

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('screen_name', cm.exception.message_dict)
        self.assertIn('This field cannot be null.', msgs[0])

    def test_screen_name_cannot_be_empty(self):
        with self.assertRaises(ValidationError) as cm:
            h = User.objects.create(id=123,
                                    screen_name="",
                                    name="Test",
                                    created_at=datetime.datetime.now())

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('screen_name', cm.exception.message_dict)
        self.assertIn('This field cannot be blank.', msgs[0])

    def test_created_at_cannot_be_null(self):
        with self.assertRaises(ValidationError) as cm:
            h = User.objects.create(id=123,
                                    name="Test",
                                    screen_name="Test")

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('created_at', cm.exception.message_dict)
        self.assertIn('This field cannot be null.', msgs[0])

    def test_duplicate_user_must_raise_exception(self):
        User.objects.create(id=123,
                            name="Test",
                            screen_name="Test",
                            created_at=datetime.datetime.now())

        with self.assertRaises(ValidationError) as cm:
            User.objects.create(id=123,
                                name="Test",
                                screen_name="Test",
                                created_at=datetime.datetime.now())

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('id', cm.exception.message_dict)
        self.assertIn(
            "User with this Twitter user id already exists.", msgs[0])


class TweetTests(TestCase):
    def test_id_must_accept_bigint(self):
        big_int = 9223372036854775807
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        t = Tweet.objects.create(id=big_int,
                                 author=author,
                                 created_at=datetime.datetime.now(),
                                 text="a")
        self.assertEqual(big_int, t.id)

    def test_author_cannot_be_null(self):
        with self.assertRaises(ValidationError) as cm:
            Tweet.objects.create(id=1,
                                 created_at=datetime.datetime.now(),
                                 text="a")

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('author', cm.exception.message_dict)
        self.assertIn('This field cannot be null.', msgs[0])

    def test_date_cannot_be_null(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        with self.assertRaises(ValidationError) as cm:
            Tweet.objects.create(id=1,
                                 author=author,
                                 text="a")

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('created_at', cm.exception.message_dict)
        self.assertIn('This field cannot be null.', msgs[0])

    def test_text_cannot_be_null(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        with self.assertRaises(ValidationError) as cm:
            Tweet.objects.create(id=1,
                                 author=author,
                                 created_at=datetime.datetime.now())

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('text', cm.exception.message_dict)
        self.assertIn('This field cannot be null.', msgs[0])

    def test_text_cannot_be_empty(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        with self.assertRaises(ValidationError) as cm:
            Tweet.objects.create(id=1,
                                 author=author,
                                 text="",
                                 created_at=datetime.datetime.now())

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('text', cm.exception.message_dict)
        self.assertIn('This field cannot be blank.', msgs[0])

    def test_lang_cannot_be_empty(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        with self.assertRaises(ValidationError) as cm:
            Tweet.objects.create(id=1,
                                 author=author,
                                 lang="",
                                 text="A",
                                 created_at=datetime.datetime.now())

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('lang', cm.exception.message_dict)
        self.assertIn('This field cannot be blank.', msgs[0])

    def test_lang_cannot_be_null(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        with self.assertRaises(ValidationError) as cm:
            Tweet.objects.create(id=1,
                                 author=author,
                                 lang=None,
                                 text="A",
                                 created_at=datetime.datetime.now())

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('lang', cm.exception.message_dict)
        self.assertIn('This field cannot be null.', msgs[0])

    def test_lang_cannot_exceed_max_size(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        with self.assertRaises(ValidationError) as cm:
            Tweet.objects.create(id=1,
                                 author=author,
                                 lang="aaaa",
                                 text="A",
                                 created_at=datetime.datetime.now())

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('lang', cm.exception.message_dict)
        self.assertIn(
            'Ensure this value has at most 3 characters (it has 4).', msgs[0])

    def test_source_can_be_empty(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        t = Tweet.objects.create(id=1,
                                 author=author,
                                 lang="pt",
                                 text="A",
                                 source="",
                                 created_at=datetime.datetime.now())

        self.assertEqual(t.source, "")

    def test_source_can_be_null(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        t = Tweet.objects.create(id=1,
                                 author=author,
                                 lang="pt",
                                 text="A",
                                 source=None,
                                 created_at=datetime.datetime.now())

        self.assertEqual(t.source, None)

    def test_source_cannot_exceed_max_size(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        with self.assertRaises(ValidationError) as cm:
            Tweet.objects.create(id=1,
                                 author=author,
                                 lang="pt",
                                 text="A",
                                 source="".join("1" for _ in range(501)),
                                 created_at=datetime.datetime.now())

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('source', cm.exception.message_dict)
        self.assertIn(
            'Ensure this value has at most 500 characters (it has 501).', msgs[0])

    def test_url_cannot_exceed_max_size(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        with self.assertRaises(ValidationError) as cm:
            Tweet.objects.create(id=1,
                                 author=author,
                                 lang="pt",
                                 text="A",
                                 url="".join("1" for _ in range(101)),
                                 created_at=datetime.datetime.now())

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('url', cm.exception.message_dict)
        self.assertIn(
            'Ensure this value has at most 100 characters (it has 101).', msgs[0])

    def test_url_can_be_null(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        t = Tweet.objects.create(id=1,
                                 author=author,
                                 lang="pt",
                                 text="A",
                                 url=None,
                                 created_at=datetime.datetime.now())

        self.assertEqual(t.url, None)

    def test_url_can_be_empty(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        t = Tweet.objects.create(id=1,
                                 author=author,
                                 lang="pt",
                                 text="A",
                                 url="",
                                 created_at=datetime.datetime.now())

        self.assertEqual(t.url, "")

    def test_filter_can_be_empty(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        t = Tweet.objects.create(id=1,
                                 author=author,
                                 lang="pt",
                                 text="A",
                                 filter_level="",
                                 created_at=datetime.datetime.now())

        self.assertEqual(t.filter_level, "")

    def test_filter_can_be_null(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        t = Tweet.objects.create(id=1,
                                 author=author,
                                 lang="pt",
                                 text="A",
                                 filter_level=None,
                                 created_at=datetime.datetime.now())

        self.assertEqual(t.filter_level, None)

    def test_filter_cannot_exceed_max_size(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        with self.assertRaises(ValidationError) as cm:
            Tweet.objects.create(id=1,
                                 author=author,
                                 lang="pt",
                                 text="A",
                                 filter_level="".join("1" for _ in range(51)),
                                 created_at=datetime.datetime.now())

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('filter_level', cm.exception.message_dict)
        self.assertIn(
            'Ensure this value has at most 50 characters (it has 51).', msgs[0])

    def test_retweet_count_for_retweet_must_be_reseted(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        parent = Tweet.objects.create(id=1,
                                      author=author,
                                      retweet_count=20,
                                      text="A",
                                      created_at=datetime.datetime.now())
        retweet = Tweet.objects.create(id=2,
                                       author=author,
                                       created_at=datetime.datetime.now(),
                                       text="A",
                                       retweet_count=20,
                                       retweeted=parent)

        self.assertEqual(0, retweet.retweet_count)

    def test_retweet_count_for_tweet_cannot_be_reseted(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        parent = Tweet.objects.create(id=1,
                                      author=author,
                                      retweet_count=20,
                                      text="A",
                                      created_at=datetime.datetime.now())

        self.assertEqual(20, parent.retweet_count)

    def test_retweet_count_for_quoted_tweet_cannot_be_reseted(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        parent = Tweet.objects.create(id=1,
                                      author=author,
                                      retweet_count=20,
                                      text="A",
                                      created_at=datetime.datetime.now())

        tweet = Tweet.objects.create(id=2,
                                     author=author,
                                     created_at=datetime.datetime.now(),
                                     text="A",
                                     retweet_count=20,
                                     quoted_tweet=parent)
        self.assertEqual(20, tweet.retweet_count)

    def test_tweet_can_have_multiple_hashtags(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        tweet = Tweet.objects.create(id=1,
                                     author=author,
                                     retweet_count=20,
                                     text="A",
                                     created_at=datetime.datetime.now())
        h1 = Hashtag.objects.create(name="#Test1")
        h2 = Hashtag.objects.create(name="#Test2")

        tweet.hashtags.add(h1)
        tweet.hashtags.add(h2)
        self.assertEqual(2, tweet.hashtags.count())

    def test_tweet_must_be_deleted_when_there_is_not_a_hashtag(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        tweet = Tweet.objects.create(id=1,
                                     author=author,
                                     retweet_count=20,
                                     text="A",
                                     created_at=datetime.datetime.now())
        h1 = Hashtag.objects.create(name="#Test1")
        tweet.hashtags.add(h1)
        h1.delete()
        self.assertEqual(0, Tweet.objects.count())

    def test_tweet_must_not_be_deleted_when_there_is_a_hashtag(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        tweet = Tweet.objects.create(id=1,
                                     author=author,
                                     retweet_count=20,
                                     text="A",
                                     created_at=datetime.datetime.now())
        h1 = Hashtag.objects.create(name="#Test1")
        h2 = Hashtag.objects.create(name="#Test2")

        tweet.hashtags.add(h1)
        tweet.hashtags.add(h2)
        h1.delete()
        self.assertEqual(1, Tweet.objects.count())

    def test_tweet_must_be_deleted_when_author_is_deleted(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        tweet = Tweet.objects.create(id=1,
                                     author=author,
                                     retweet_count=20,
                                     text="A",
                                     created_at=datetime.datetime.now())
        author.delete()
        self.assertEqual(0, Tweet.objects.count())

    def test_tweet_must_be_deleted_when_quoted_tweet_is_deleted(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        parent = Tweet.objects.create(id=1,
                                      author=author,
                                      retweet_count=20,
                                      text="A",
                                      created_at=datetime.datetime.now())
        tweet = Tweet.objects.create(id=2,
                                     author=author,
                                     quoted_tweet=parent,
                                     text="A",
                                     created_at=datetime.datetime.now())
        parent.delete()
        self.assertEqual(0, Tweet.objects.count())

    def test_tweet_must_be_deleted_when_retweeted_is_deleted(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        parent = Tweet.objects.create(id=1,
                                      author=author,
                                      retweet_count=20,
                                      text="A",
                                      created_at=datetime.datetime.now())
        tweet = Tweet.objects.create(id=2,
                                     author=author,
                                     retweeted=parent,
                                     text="A",
                                     created_at=datetime.datetime.now())
        parent.delete()
        self.assertEqual(0, Tweet.objects.count())

    def test_get_since_id_must_return_latest_id(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        t1 = Tweet.objects.create(id=1,
                                  author=author,
                                  text="A",
                                  created_at=datetime.datetime.now())
        t2 = Tweet.objects.create(id=2,
                                  author=author,
                                  text="A",
                                  created_at=datetime.datetime.now())

        since_id = Tweet.get_since_id()
        self.assertEqual(2, since_id)

    def test_get_max_id_must_return_earliest_id(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        t1 = Tweet.objects.create(id=1,
                                  author=author,
                                  text="A",
                                  created_at=datetime.datetime.now())
        t2 = Tweet.objects.create(id=2,
                                  author=author,
                                  text="A",
                                  created_at=datetime.datetime.now())

        max_id = Tweet.get_max_id()
        self.assertEqual(1, max_id)

    def test_get_since_id_must_return_latest_id_of_hashtag(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())

        h1 = Hashtag.objects.create(name="#Test1")
        h2 = Hashtag.objects.create(name="#Test2")
        h3 = Hashtag.objects.create(name="#Test3")

        t1 = Tweet.objects.create(id=1,
                                  author=author,
                                  text="A",
                                  created_at=datetime.datetime.now())
        t2 = Tweet.objects.create(id=2,
                                  author=author,
                                  text="A",
                                  created_at=datetime.datetime.now())
        t3 = Tweet.objects.create(id=10,
                                  author=author,
                                  text="A",
                                  created_at=datetime.datetime.now())

        t1.hashtags.add(h1)
        t2.hashtags.add(h2)
        t2.hashtags.add(h3)
        t3.hashtags.add(h3)

        since_id1 = Tweet.get_since_id(h1.name)
        since_id2 = Tweet.get_since_id(h2.name)
        since_id3 = Tweet.get_since_id(h3.name)
        self.assertEqual(1, since_id1)
        self.assertEqual(2, since_id2)
        self.assertEqual(10, since_id3)

    def test_get_max_id_must_return_earliest_id_of_hashtag(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())

        h1 = Hashtag.objects.create(name="#Test1")
        h2 = Hashtag.objects.create(name="#Test2")
        h3 = Hashtag.objects.create(name="#Test3")

        t1 = Tweet.objects.create(id=1,
                                  author=author,
                                  text="A",
                                  created_at=datetime.datetime.now())
        t2 = Tweet.objects.create(id=2,
                                  author=author,
                                  text="A",
                                  created_at=datetime.datetime.now())
        t3 = Tweet.objects.create(id=10,
                                  author=author,
                                  text="A",
                                  created_at=datetime.datetime.now())

        t1.hashtags.add(h1)
        t2.hashtags.add(h2)
        t2.hashtags.add(h3)
        t3.hashtags.add(h3)

        max_id1 = Tweet.get_max_id(h1.name)
        max_id2 = Tweet.get_max_id(h2.name)
        max_id3 = Tweet.get_max_id(h3.name)
        self.assertEqual(1,  max_id1)
        self.assertEqual(2,  max_id2)
        self.assertEqual(2, max_id3)

    def test_get_since_id_with_invalid_hashtag_must_return_none(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())

        t1 = Tweet.objects.create(id=1,
                                  author=author,
                                  text="A",
                                  created_at=datetime.datetime.now())

        since_id = Tweet.get_since_id("#Test3")
        self.assertIsNone(since_id)

    def test_get_max_id_with_invalid_hashtag_must_return_none(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())

        t1 = Tweet.objects.create(id=1,
                                  author=author,
                                  text="A",
                                  created_at=datetime.datetime.now())

        max_id = Tweet.get_max_id("#Test3")
        self.assertIsNone(max_id)

    def test_get_since_id_when_tweets_are_empty_must_return_none(self):
        since_id = Tweet.get_since_id()
        self.assertIsNone(since_id)
        since_id = Tweet.get_since_id("#Test3")
        self.assertIsNone(since_id)

    def test_get_max_id_when_tweets_are_empty_must_return_none(self):
        max_id = Tweet.get_max_id()
        self.assertIsNone(max_id)
        max_id = Tweet.get_max_id("#Test3")
        self.assertIsNone(max_id)
