# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0011_auto_20160509_0258'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='content',
            name='image',
        ),
        migrations.AddField(
            model_name='story',
            name='short_description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='story',
            name='splash',
            field=models.ImageField(null=True, upload_to=b'content/%Y/%m/', blank=True),
        ),
        migrations.AlterField(
            model_name='choice',
            name='text',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='scene',
            name='image',
            field=models.ForeignKey(verbose_name=b'Background Image', blank=True, to='story.Image', null=True, on_delete=models.CASCADE),
        ),
    ]
