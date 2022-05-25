# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('galleryserve', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gallery',
            name='random',
            field=models.BooleanField(default=False, help_text=b'If selected, the sort numbers will be ignored and your gallery objects will be generated in random order.'),
        ),
    ]
