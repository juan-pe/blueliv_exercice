# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_crawler', '0002_auto_20161004_1011'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('text', models.TextField(verbose_name='Comment', help_text='Text of the comment', max_length=1024)),
                ('punctiation', models.IntegerField(verbose_name='Points', help_text='Points of the comments')),
                ('creation_date', models.DateTimeField(verbose_name='Creation date', help_text='Creation date of the comment')),
                ('author', models.ForeignKey(verbose_name='Reddit user', help_text='Reddit user that made the comment', to='news_crawler.RedditUser', related_name='comments')),
            ],
        ),
        migrations.AlterField(
            model_name='submision',
            name='submitter',
            field=models.ForeignKey(verbose_name='Reddit user', help_text='Reddit user that made the submission', to='news_crawler.RedditUser', related_name='submissions'),
        ),
        migrations.AddField(
            model_name='comments',
            name='submission',
            field=models.ForeignKey(verbose_name='Submission', help_text='Submission commented', to='news_crawler.Submision', related_name='comments'),
        ),
    ]
