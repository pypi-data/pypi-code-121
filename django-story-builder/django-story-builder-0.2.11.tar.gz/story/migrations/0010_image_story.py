# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0009_auto_20160227_2125'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='story',
            field=models.ForeignKey(default=2, to='story.Story', on_delete=models.CASCADE),
            preserve_default=False,
        ),
    ]
