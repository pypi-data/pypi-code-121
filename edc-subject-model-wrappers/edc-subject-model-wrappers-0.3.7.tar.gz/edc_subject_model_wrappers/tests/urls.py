from django.contrib import admin
from django.urls import path
from edc_appointment.admin_site import edc_appointment_admin

from .admin import edc_subject_model_wrappers_admin

app_name = "edc_subject_model_wrappers"

urlpatterns = [
    path("admin/", edc_appointment_admin.urls),
    path("admin/", edc_subject_model_wrappers_admin.urls),
    path("admin/", admin.site.urls),
]
