# -*- coding: utf-8 -*-


from django.db import migrations, models
import galleryserve.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('height', models.IntegerField(default=600, help_text=b'Height images should be resized to in pixels', blank=True)),
                ('width', models.IntegerField(default=800, help_text=b'Width images should be resized to in pixels', blank=True)),
                ('resize', models.BooleanField(default=True, help_text=b'If selected, the dimensions specified above will be used to scale and crop the uploaded image')),
                ('quality', models.IntegerField(default=85, help_text=b'An integer between 0-100. 100 will result in the largest file size.', verbose_name='Image Quality')),
            ],
            options={
                'ordering': ('title',),
                'verbose_name_plural': 'galleries',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=b'galleryserve/images', blank=True)),
                ('alt', models.CharField(help_text=b'This will be used for the image alt attribute', max_length=100, blank=True)),
                ('title', models.CharField(help_text=b'This will be used for the image or content title attribute', max_length=100, blank=True)),
                ('credit', models.CharField(help_text=b'Use this field to credit the image or content creator', max_length=200, blank=True)),
                ('video_url', models.URLField(help_text=b'Enter the url of the video to be embedded', verbose_name=b'video url', blank=True)),
                ('url', models.CharField(help_text=b'URL to which the image will be linked.', max_length=200, verbose_name=b'target url', blank=True)),
                ('content', models.TextField(help_text=b'Use this field to add html content associated with the item', blank=True)),
                ('sort', models.IntegerField(default=0, help_text=b'Items will be displayed in their sort order')),
                ('gallery', models.ForeignKey(related_name='items', to='galleryserve.Gallery', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('sort',),
            },
        ),
    ]
