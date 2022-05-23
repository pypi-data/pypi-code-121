# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0005_auto_20151228_1934'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='content',
            options={'verbose_name_plural': 'Content', 'ordering': ('ordering',)},
        ),
        migrations.AlterModelOptions(
            name='story',
            options={'verbose_name_plural': 'Stories'},
        ),
        migrations.AddField(
            model_name='content',
            name='image',
            field=models.ImageField(upload_to='content/%Y/%m/', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='requiredtag',
            name='comparison',
            field=models.CharField(default='>=', choices=[('>', '>'), ('<', '<'), ('=', '=')], max_length=10),
        ),
    ]
