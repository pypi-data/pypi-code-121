# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0010_image_story'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='audio',
            field=models.FileField(blank=True, upload_to='content/%Y/%m/', null=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(blank=True, upload_to='content/%Y/%m/', null=True),
        ),
    ]
