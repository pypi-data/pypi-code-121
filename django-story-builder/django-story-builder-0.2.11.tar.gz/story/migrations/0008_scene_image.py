# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0007_story_starting_scene'),
    ]

    operations = [
        migrations.AddField(
            model_name='scene',
            name='image',
            field=models.ImageField(null=True, upload_to=b'scene/%Y/%m/', blank=True),
        ),
    ]
