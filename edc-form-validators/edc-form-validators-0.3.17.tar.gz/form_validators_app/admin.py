from django.contrib import admin
from django.contrib.admin.decorators import register

from .forms import TestModelForm
from .models import TestModel


@register(TestModel)
class TestModelAdmin(admin.ModelAdmin):

    form = TestModelForm
