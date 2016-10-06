# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_crawler', '0005_auto_20161004_1250'),
    ]

    operations = [
        migrations.RenameField(
            model_name='submision',
            old_name='punctiation',
            new_name='punctuation',
        ),
    ]
