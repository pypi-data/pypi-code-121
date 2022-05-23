# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0006_auto_20151230_1717'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='starting_scene',
            field=models.ForeignKey(related_name='starting', blank=True, to='story.Scene', null=True, on_delete=models.CASCADE),
        ),
    ]
