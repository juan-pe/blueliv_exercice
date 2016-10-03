# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RedditUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(help_text='Reddit user name', max_length=255, verbose_name='Reddit user')),
            ],
        ),
        migrations.CreateModel(
            name='Submision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('submision_title', models.CharField(help_text='Title of the submision', max_length=255, verbose_name='Title')),
                ('external_url', models.URLField(help_text='External URL of the submision', verbose_name='External URL')),
                ('discusion_url', models.URLField(help_text='Discusion URL of the submision', verbose_name='Discusion URL')),
                ('punctiation', models.IntegerField(help_text='Points of the submision', verbose_name='Points')),
                ('rank', models.IntegerField(help_text='Rank of the submision', verbose_name='Rank')),
                ('number_of_comments', models.IntegerField(help_text='Number of comments of the submision', verbose_name='Number of comments')),
                ('creation_date', models.DateTimeField(help_text='Creation date of the submision', verbose_name='Creation date')),
                ('submitter', models.ForeignKey(help_text='Reddit user that made the submission', to='news_crawler.RedditUser', verbose_name='Reddit user')),
            ],
        ),
    ]
