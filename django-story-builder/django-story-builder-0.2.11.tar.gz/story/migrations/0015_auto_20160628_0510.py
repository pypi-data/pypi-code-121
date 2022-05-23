# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0014_auto_20160604_2311'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='content',
            options={'ordering': ('ordering', 'id'), 'verbose_name_plural': 'Content'},
        ),
        migrations.AlterModelOptions(
            name='story',
            options={'ordering': ('ordering', 'name'), 'verbose_name_plural': 'Stories'},
        ),
        migrations.AddField(
            model_name='story',
            name='ordering',
            field=models.SmallIntegerField(default=1),
        ),
    ]
