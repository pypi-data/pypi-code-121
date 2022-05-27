
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

from invoices import views


app_name = 'invoices'


urlpatterns = [

    path('<str:invoice_type>/create/',
         views.create_invoice,
         name='create'),

    path('<str:invoice_type>/<int:invoice_id>/',
         views.update_invoice,
         name='update'),

    path('<str:invoice_type>/<int:invoice_id>/manage/',
         views.manage_invoice,
         name='manage'),

    path('<str:invoice_type>/<int:invoice_id>/print/',
         views.print_invoice,
         name='print'),

    path('<str:invoice_type>/report/',
         views.get_report,
         name='report'),

    path('<str:invoice_type>/<int:invoice_id>/add-item/',
         views.add_item,
         name='add-item'),

    path('<str:invoice_type>/<int:invoice_id>/items/<int:item_id>/',
         views.ItemAPI.as_view(),
         name='item')

]


app_urls = i18n_patterns(
    path('documents/', include((urlpatterns, app_name)))
)
