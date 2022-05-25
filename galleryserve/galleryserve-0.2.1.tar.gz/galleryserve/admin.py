from django.contrib import admin

from galleryserve import models
from django.conf import settings

class ItemInline(admin.StackedInline):
    model = models.Item
    extra = 1
    try:
        exclude = settings.GALLERYSERVE_EXCLUDE_FIELDS
    except:
        fieldsets = (
            (None, {'fields': (('image', 'alt', 'sort'),
            ('url', 'video_url'), ('title', 'credit'), 'content')}),
        )

class GalleryAdmin(admin.ModelAdmin):
    inlines = [
        ItemInline,
    ]
    list_display = ('title',)
    search_fields = ['title',]
    fieldsets = (
        (None, {'fields': (('title'), 'height', 'width', 'random', 'resize',
                'quality')}),
    )

admin.site.register(models.Gallery, GalleryAdmin)

