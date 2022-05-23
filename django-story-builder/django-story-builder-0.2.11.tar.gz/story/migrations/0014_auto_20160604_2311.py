# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0013_auto_20160528_0528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requiredtag',
            name='value',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='story',
            name='short_description',
            field=models.CharField(max_length=80, null=True, blank=True),
        ),
    ]
