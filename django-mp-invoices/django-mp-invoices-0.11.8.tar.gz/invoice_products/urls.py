
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

from invoice_products import views


app_name = 'invoice-products'


urlpatterns = [

    path('', views.get_products, name='list'),

    path('add-product/', views.add_product, name='add'),

    path('bar-code-to-id/', views.get_id_from_bar_code,
         name='bar-code-to-id'),

    path('print-name/<int:product_id>/', views.print_product_name,
         name='print-name'),

    path('print-bar-code/<int:product_id>/', views.print_product_bar_code,
         name='print-bar-code'),

    path('history/<int:product_id>/', views.get_product_history,
         name='history')

]


app_urls = i18n_patterns(
    path('products/', include((urlpatterns, app_name)))
)
