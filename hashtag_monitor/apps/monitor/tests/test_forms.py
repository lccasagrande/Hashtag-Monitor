import datetime
import random

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

# Create your tests here.
from ..models import Tweet, User, Hashtag, COLORS_PALETTE
from ..forms import HashtagForm


class HashtagFormTests(TestCase):
    def test_hashtag_is_case_insensitive(self):
        Hashtag.objects.create(name="#Test")
        h = HashtagForm(data={"name": "#TeSt"})
        self.assertFalse(h.is_valid())

    def test_duplicate_hashtag(self):
        Hashtag.objects.create(name="#Test")
        h = HashtagForm(data={"name": "#Test"})
        self.assertFalse(h.is_valid())

    def test_invalid_hashtag_name(self):
        h = HashtagForm(data={"name": "Test"})
        self.assertFalse(h.is_valid())

    def test_hashtag_name_is_not_string(self):
        h = HashtagForm(data={"name": 12})
        self.assertFalse(h.is_valid())

    def test_hashtag_too_long(self):
        h = HashtagForm(data={"name": "#" + "".join('1' for _ in range(500))})
        self.assertFalse(h.is_valid())

    def test_incomplete_hashtag(self):
        h = HashtagForm(data={"name": "#"})
        self.assertFalse(h.is_valid())

    def test_empty_hashtag(self):
        h = HashtagForm(data={"name": ""})
        self.assertFalse(h.is_valid())

    def test_form_is_valid(self):
        h = HashtagForm(data={"name": "#Test"})
        self.assertTrue(h.is_valid())

