# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='choice',
            name='next_scene',
            field=models.ForeignKey(blank=True, to='story.Scene', null=True, related_name='links_to', on_delete=models.CASCADE),
        ),
    ]
