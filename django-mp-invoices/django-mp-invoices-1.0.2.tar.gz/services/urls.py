
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

from services import views


app_name = 'services'


urlpatterns = [

    path('report/', views.get_report, name='report'),

    path('items/', views.get_service_items, name='items'),

    path('add-to-sale/<int:sale_id>/', views.add_service, name='add'),

    path('<int:service_id>/', views.ServiceAPI.as_view(), name='service'),

    path('print-services/<int:sale_id>/', views.print_services,
         name='print-services'),

    path('print-service-items/', views.print_service_items,
         name='print-service-items'),

    path('add-service-item/', views.add_service_item, name='add-service-item')

]


app_urls = i18n_patterns(
    path('services/', include((urlpatterns, app_name)))
)
