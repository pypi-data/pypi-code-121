from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from wagtail.admin.modal_workflow import render_modal_workflow
from wagtail.core.models import Page

def chooser_page_data(request, page_id):
    '''Returns modal_workflow data version of page data.'''
    page = get_object_or_404(Page, id=page_id)

    return JsonResponse({
            'step': 'page_chosen',
            'result': {
                'id': page.id,
                'title': page.title,
                'edit_link': reverse('wagtailadmin_pages:edit', args=[page.id]),
            }
        }
    )
