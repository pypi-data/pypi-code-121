
from django.apps import apps
from django import template


register = template.Library()


@register.simple_tag
def get_latest_reviews():
    Review = apps.get_model('reviews', 'Review')
    return Review.objects.filter(is_active=True).order_by('-id')[:5]
