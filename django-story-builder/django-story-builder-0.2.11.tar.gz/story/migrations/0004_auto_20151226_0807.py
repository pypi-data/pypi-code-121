# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0003_auto_20151226_0805'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scene',
            name='story',
            field=models.ForeignKey(to='story.Story', default=1, on_delete=models.CASCADE),
            preserve_default=False,
        ),
    ]
