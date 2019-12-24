import datetime
import random

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

# Create your tests here.
from ..models import Tweet, User, Hashtag, COLORS_PALETTE
from ..queries import TweetQueries, HashtagQueries, UserQueries

class ViewsTests(TestCase):
    pass