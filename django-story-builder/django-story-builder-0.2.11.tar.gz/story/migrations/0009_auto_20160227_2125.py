# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0008_scene_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('image', models.ImageField(null=True, upload_to=b'content/%Y/%m/', blank=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='content',
            name='image',
        ),
        migrations.RemoveField(
            model_name='scene',
            name='image',
        ),
        migrations.AddField(
            model_name='content',
            name='image',
            field=models.ForeignKey(blank=True, to='story.Image', null=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='scene',
            name='image',
            field=models.ForeignKey(blank=True, to='story.Image', null=True, on_delete=models.CASCADE),
        ),
    ]
