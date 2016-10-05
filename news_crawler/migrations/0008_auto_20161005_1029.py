# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_crawler', '0007_auto_20161004_2313'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('text', models.TextField(help_text='Text of the comment', max_length=1024, verbose_name='Comment')),
                ('punctiation', models.IntegerField(help_text='Points of the comments', verbose_name='Points')),
                ('creation_date', models.DateTimeField(help_text='Creation date of the comment', verbose_name='Creation date')),
                ('author', models.ForeignKey(verbose_name='Reddit user', related_name='comments', help_text='Reddit user that made the comment', to='news_crawler.RedditUser')),
                ('submission', models.ForeignKey(verbose_name='Submission', related_name='comments', help_text='Submission commented', to='news_crawler.Submision')),
            ],
        ),
        migrations.RemoveField(
            model_name='comments',
            name='author',
        ),
        migrations.RemoveField(
            model_name='comments',
            name='submission',
        ),
        migrations.DeleteModel(
            name='Comments',
        ),
    ]
