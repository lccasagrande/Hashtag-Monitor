# Generated by Django 3.0 on 2019-12-23 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0016_auto_20191223_1941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_image',
            field=models.URLField(blank=True, default=None, null=True, verbose_name='Profile image url'),
        ),
    ]
