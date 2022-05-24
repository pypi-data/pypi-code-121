
from django.contrib import admin

from reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_filter = ['is_active']

    list_display = ['name', 'date_created', 'user', 'rating', 'is_active', 'answer']

    list_editable = ['is_active']

    search_fields = ['id', 'name', 'text']

    fields = (
        ('is_active', 'user', ),
        ('name', 'rating', ),
        ('photo', ),
        'text',
        'answer'
    )
