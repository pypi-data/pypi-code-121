# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Scene',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='content',
            name='scene',
            field=models.ForeignKey(to='story.Scene', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='choice',
            name='next_scene',
            field=models.ForeignKey(related_name='links_to', to='story.Scene', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='choice',
            name='scene',
            field=models.ForeignKey(related_name='links_from', to='story.Scene', on_delete=models.CASCADE),
        ),
    ]
