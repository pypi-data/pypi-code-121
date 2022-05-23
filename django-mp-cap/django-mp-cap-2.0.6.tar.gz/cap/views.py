
from django.contrib import admin
from django.shortcuts import render as django_render
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def render(request, template_name, context=None, status=None):

    ctx = admin.site.each_context(request)
    ctx.update(context or {})

    return django_render(request, template_name, ctx, status=status)
