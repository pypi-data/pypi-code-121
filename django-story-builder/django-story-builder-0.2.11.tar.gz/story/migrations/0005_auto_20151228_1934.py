# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('story', '0004_auto_20151226_0807'),
    ]

    operations = [
        migrations.CreateModel(
            name='Consequence',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('module', models.CharField(max_length=255)),
                ('choice', models.ForeignKey(to='story.Choice', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='ConsequenceAttribute',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('tag', models.CharField(max_length=50)),
                ('value', models.SmallIntegerField(default=1)),
                ('choice', models.ForeignKey(to='story.Choice', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='RequiredTag',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('tag', models.CharField(max_length=50)),
                ('comparison', models.CharField(choices=[('>', '>'), ('<', '<'), ('=', '=')], max_length=10, default='>')),
                ('value', models.SmallIntegerField(default=1)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AddField(
            model_name='content',
            name='group',
            field=models.CharField(max_length=50, default='default'),
        ),
        migrations.AddField(
            model_name='content',
            name='ordering',
            field=models.SmallIntegerField(default=0),
        ),
    ]
