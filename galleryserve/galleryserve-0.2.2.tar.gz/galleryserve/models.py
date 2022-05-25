from django.db import models
import PIL
from PIL import ImageOps

class Gallery(models.Model):
    title = models.CharField(max_length=200)
    height = models.IntegerField(blank=True, default=600,
        help_text="Height images should be resized to in pixels")
    width = models.IntegerField(blank=True, default=800,
        help_text="Width images should be resized to in pixels")
    random = models.BooleanField(default=False,
        help_text="If selected, the sort numbers will be ignored and your "
        "gallery objects will be generated in random order.")
    resize = models.BooleanField(default=True,
        help_text="If selected, the dimensions specified above will be used"
        " to scale and crop the uploaded image")
    quality = models.IntegerField('Image Quality', default=85,
        help_text="An integer between 0-100. 100 will result in the largest "
        "file size.")
    class Meta:
        ordering = ('title',)
        verbose_name_plural = 'galleries'

    def __unicode__(self):
        return '{}'.format(self.title)


class Item(models.Model):
    image = models.ImageField(blank=True, upload_to='galleryserve/images')
    gallery = models.ForeignKey(
        Gallery,
        related_name='items',
        on_delete=models.CASCADE,
    )
    alt = models.CharField(max_length=100, blank=True,
        help_text="This will be used for the image alt attribute")
    title = models.CharField(max_length=100, blank=True,
        help_text="This will be used for the image or content title attribute")
    credit = models.CharField(max_length=200, blank=True,
        help_text="Use this field to credit the image or content creator")
    video_url = models.URLField('video url', blank=True,
        help_text="Enter the url of the video to be embedded")
    url = models.CharField('target url', blank=True, max_length=200,
        help_text="URL to which the image will be linked.")
    content = models.TextField(blank=True, help_text="Use this field to "
        "add html content associated with the item")
    sort = models.IntegerField(default=0,
        help_text="Items will be displayed in their sort order")

    class Meta:
        ordering = ('sort',)

    def __unicode__(self):
        return '{}'.format(self.alt)

    def save(self):
        super(Item, self).save()
        if self.image:
            filename = self.image.path
            image = PIL.Image.open(filename)
            if self.gallery.resize:
                try:
                    width = self.gallery.width
                except:
                    width = 800
                try:
                    height = self.gallery.height
                except:
                    height = 600
                size=(width, height)
                image = ImageOps.fit(image, size, PIL.Image.ANTIALIAS)
            image.save(filename, quality=self.gallery.quality)

