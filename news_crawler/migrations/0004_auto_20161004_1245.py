# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_crawler', '0003_auto_20161004_1142'),
    ]

    operations = [
        migrations.AddField(
            model_name='reddituser',
            name='comment_karma',
            field=models.IntegerField(verbose_name='Comment karma', help_text='Avarage comment karma of the user', null=True),
        ),
        migrations.AddField(
            model_name='reddituser',
            name='post_karma',
            field=models.IntegerField(verbose_name='Post karma', help_text='Avarage post karma of the user', null=True),
        ),
    ]
