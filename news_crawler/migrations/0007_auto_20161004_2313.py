# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_crawler', '0006_auto_20161004_1301'),
    ]

    operations = [
        migrations.AddField(
            model_name='submision',
            name='comments_url',
            field=models.URLField(verbose_name='Comments URL', null=True, help_text='Comments URL of the submision'),
        ),
        migrations.AddField(
            model_name='submision',
            name='submitter_url',
            field=models.URLField(verbose_name='Submitter URL', null=True, help_text='Submiter URL of the submision'),
        ),
    ]
