
from django.urls import path, include

from customers import views


app_name = 'customers'


urlpatterns = [

    path('add/', views.add_customer, name='add'),

    path('<int:customer_id>/details/', views.get_customer_detail,
         name='detail'),

    path('export/', views.export_customers, name='export')
]


app_urls = [
    path('customers/', include((urlpatterns, app_name)))
]
