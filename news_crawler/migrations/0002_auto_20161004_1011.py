# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_crawler', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='submision',
            old_name='submision_title',
            new_name='title',
        ),
    ]
