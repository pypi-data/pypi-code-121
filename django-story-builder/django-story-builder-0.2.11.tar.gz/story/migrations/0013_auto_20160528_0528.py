# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0012_auto_20160526_0244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='starting_scene',
            field=models.ForeignKey(related_name='starting', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='story.Scene', null=True),
        ),
    ]
