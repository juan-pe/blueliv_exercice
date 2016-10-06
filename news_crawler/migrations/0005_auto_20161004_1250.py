# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_crawler', '0004_auto_20161004_1245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submision',
            name='discusion_url',
            field=models.URLField(verbose_name='Discusion URL', help_text='Discusion URL of the submision', null=True),
        ),
        migrations.AlterField(
            model_name='submision',
            name='external_url',
            field=models.URLField(verbose_name='External URL', help_text='External URL of the submision', null=True),
        ),
    ]
