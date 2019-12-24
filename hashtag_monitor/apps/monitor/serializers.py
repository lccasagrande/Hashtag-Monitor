from rest_framework import serializers

from . import models


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Hashtag
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = '__all__'


class DefaultTweetSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d/%m/%Y  %H:%M")
    author = UserSerializer()
    hashtags = HashtagSerializer(many=True)

    class Meta:
        model = models.Tweet
        fields = '__all__'
        depth = 1


class TweetSerializer(DefaultTweetSerializer):
    quoted_tweet = DefaultTweetSerializer()
    retweeted = DefaultTweetSerializer()
