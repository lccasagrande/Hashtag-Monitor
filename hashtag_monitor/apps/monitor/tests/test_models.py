import datetime
import random
import pytz

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

# Create your tests here.
from ..models import Tweet, User, Hashtag, COLORS_PALETTE


class HashtagTests(TestCase):
    def test_get_or_create_must_get_hashtag(self):
        h1 = Hashtag.objects.create(name="#Test")
        h2 = Hashtag.get_or_create("#Test")
        self.assertEqual(h1, h2)

    def test_get_or_create_must_create_new_hashtag(self):
        h1 = Hashtag.objects.create(name="#Test")
        h2 = Hashtag.get_or_create("#Test2")
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
        query = Hashtag.get_tweets_count_per_hashtag()
        self.assertEqual(2, query[h1.name]['count'])
        self.assertEqual(1, query[h2.name]['count'])
        self.assertEqual(0, query[h3.name]['count'])

    def test_get_hashtags_sorted(self):
        h1 = Hashtag.objects.create(name="#C")
        h2 = Hashtag.objects.create(name="#B")
        h3 = Hashtag.objects.create(name="#A")
        hashtags_sorted = Hashtag.get_hashtags_sorted()
        self.assertEqual(h3, hashtags_sorted[2])
        self.assertEqual(h2, hashtags_sorted[1])
        self.assertEqual(h1, hashtags_sorted[0])

    def test_delete_if_exists(self):
        h1 = Hashtag.objects.create(name="#Test")
        deleted = Hashtag.delete_if_exists('#Test')
        self.assertEqual(0, Hashtag.objects.count())
        self.assertTrue(deleted)

    def test_delete_if_exists_should_not_throw_exception(self):
        deleted = Hashtag.delete_if_exists('#Test')
        self.assertFalse(deleted)

    def test_hashtag_is_case_insensitive(self):
        h = Hashtag.objects.create(name="#Test")
        with self.assertRaises(ValidationError) as cm:
            Hashtag.objects.create(name="#TeSt")

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('name', cm.exception.message_dict)
        self.assertIn('A hashtag is not case sensitive', msgs[0])

    def test_max_number_of_hashtags(self):
        max_nb = 10
        for i in range(max_nb):
            Hashtag.objects.create(name=f"#Test{i}")
        with self.assertRaises(ValidationError) as cm:
            Hashtag.objects.create(name=f"#Test{max_nb}")

        msgs = list(cm.exception.message_dict.values())
        self.assertIn('name', cm.exception.message_dict)
        self.assertIn(f"The maximum number of hashtags is {max_nb}.", msgs[0])

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
    def test_create_from_json(self):
        d = pytz.utc.localize(datetime.datetime.utcnow())
        j = {
            'id': 1,
            'name': "test",
                    'screen_name': "stest",
                    'created_at': d.strftime("%a %b %d %H:%M:%S %z %Y")
        }
        User.update_or_create_from_json(j)

    def test_update_from_json(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())

        d = pytz.utc.localize(datetime.datetime.utcnow())
        j = {
            'id': 1,
            'name': "test",
            'screen_name': "stest",
            'created_at': d.strftime("%a %b %d %H:%M:%S %z %Y")
        }
        User.update_or_create_from_json(j)
        a = User.objects.get(pk=1)
        self.assertEqual(a.name, "test")
        self.assertEqual(a.screen_name, "stest")

    def test_remove_trash_must_delete_users_without_tweets(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        User.remove_trash()
        self.assertEqual(0, User.objects.all().count())

    def test_remove_trash_must_not_delete_users_with_tweets(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        tweet1 = Tweet.objects.create(id=1,
                                      author=author,
                                      text="A",
                                      created_at=datetime.datetime.now())
        User.remove_trash()
        self.assertEqual(1, User.objects.all().count())

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

    def test_update_or_create_should_update_when_user_exist(self):
        date = datetime.datetime.now()
        old_usr = User.objects.create(
            id=1, name="T", screen_name="T", created_at=date)
        usr = User(id=1, name="A", screen_name="B",
                   created_at=date, friends_count=10)
        User.update_or_create(usr)
        updated_user = User.objects.get(pk=1)
        self.assertEqual(1, User.objects.count())
        self.assertEqual(usr.name, updated_user.name)
        self.assertEqual(usr.screen_name, updated_user.screen_name)
        self.assertEqual(usr.friends_count, updated_user.friends_count)

    def test_update_or_create_should_create_when_user_not_exist(self):
        a1 = User.objects.create(
            id=1, name="T", screen_name="T", created_at=datetime.datetime.now())
        new_a = User(id=2, name="A", screen_name="B",
                     created_at=datetime.datetime.now(), friends_count=10)

        User.update_or_create(new_a)
        self.assertEqual(2, User.objects.count())


class TweetTests(TestCase):
    def create_from_json(self):
        h = Hashtag.objects.create("#Test")
        d = pytz.utc.localize(datetime.datetime.utcnow())
        j = {
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
        Tweet.create_from_json(h.name, j)
        tweet = Tweet.objects.get(pk=1)
        self.assertEqual(tweet.text, "Test")

    def create_from_json_must_update_author(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())

        h = Hashtag.objects.create("#Test")
        d = pytz.utc.localize(datetime.datetime.utcnow())
        j = {
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
        Tweet.create_from_json(h.name, j)
        usr = User.objects.get(pk=1)
        self.assertEqual(usr.name, "test")
        self.assertEqual(usr.sname, "stest")

    def test_remove_trash_must_delete_tweets_without_hashtags(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        parent = Tweet.objects.create(id=1,
                                      author=author,
                                      retweet_count=20,
                                      text="A",
                                      created_at=datetime.datetime.now())
        Tweet.remove_trash()
        self.assertEqual(0, Tweet.objects.all().count())

    def test_remove_trash_must_not_delete_tweets_with_hashtag(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        parent = Tweet.objects.create(id=1,
                                      author=author,
                                      text="A",
                                      created_at=datetime.datetime.now())
        h1 = Hashtag.objects.create(name="#Test")
        parent.hashtags.add(h1)
        Tweet.remove_trash()
        self.assertEqual(1, Tweet.objects.all().count())

    def test_remove_trash_must_not_delete_tweets_retweeted(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        parent = Tweet.objects.create(id=1,
                                      author=author,
                                      text="A",
                                      created_at=datetime.datetime.now())
        tweet = Tweet.objects.create(id=2,
                                     author=author,
                                     retweeted=parent,
                                     text="A",
                                     created_at=datetime.datetime.now())
        Tweet.remove_trash()
        self.assertEqual(1, User.objects.all().count())
        self.assertEqual(1, Tweet.objects.all().count())

    def test_remove_trash_must_not_delete_tweets_quoted(self):
        author = User.objects.create(id=1,
                                     name="Opa",
                                     screen_name="Test",
                                     created_at=datetime.datetime.now())
        parent = Tweet.objects.create(id=1,
                                      author=author,
                                      text="A",
                                      created_at=datetime.datetime.now())
        tweet = Tweet.objects.create(id=2,
                                     author=author,
                                     quoted_tweet=parent,
                                     text="A",
                                     created_at=datetime.datetime.now())
        Tweet.remove_trash()
        self.assertEqual(1, User.objects.all().count())
        self.assertEqual(1, Tweet.objects.all().count())

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
        query = Tweet.get_tweets_per_lang()

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

        query = Tweet.get_tweets_per_lang(hashtag_name=h1.name)

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

        query = Tweet.get_tweets_per_lang(top=1)

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

        query = Tweet.get_tweets_per_lang(top=1, hashtag_name=h1.name)

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

        query = Tweet.get_hashtag_tweets_per_day()
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

        query = Tweet.get_hashtag_tweets_per_day(num_days=2)
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
        summary = Tweet.get_summary()
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
        summary = Tweet.get_summary(h1.name)
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
        tweets = Tweet.get_latest_tweets(count=100)
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
        tweets = Tweet.get_latest_tweets(count=2)
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
        tweets = Tweet.get_latest_tweets(
            count=100, hashtag_name=h2.name)
        self.assertEqual(1, len(tweets))
