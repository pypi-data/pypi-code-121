
from django.shortcuts import render
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def find_article(request):

    code = request.GET.get('code', '')

    articles = []

    return render(request, 'tecdoc/search.html', {
        'articles': articles,
        'code': code,
        **admin.site.each_context(request)
    })
