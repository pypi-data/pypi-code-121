
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

from product_barcode import views


app_name = 'barcode'


urlpatterns = [

    path('print/', views.print_codes, name='print'),

    path('img/<str:code>/', views.get_code, name='get'),

    path('generate/', views.generate_codes, name='generate-bar-codes'),

]

app_urls = i18n_patterns(
    path('barcode/', include((urlpatterns, app_name)))
)
