# Generated by Django 3.0 on 2019-12-22 16:03

from django.db import migrations, models
import hashtag_monitor.apps.monitor.models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0010_tweet_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hashtag',
            name='name',
            field=models.CharField(max_length=500, primary_key=True, serialize=False, validators=[hashtag_monitor.apps.monitor.models.validate_is_hashtag, hashtag_monitor.apps.monitor.models.validate_nb_hashtag, hashtag_monitor.apps.monitor.models.validate_is_not_duplicate], verbose_name='Hashtag name'),
        ),
    ]