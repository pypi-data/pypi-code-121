from django.urls import path

from netbox.views.generic import ObjectChangeLogView
from . import models, views

urlpatterns = (
    path('app-systems/', views.AppSystemListView.as_view(), name="appsystem_list"),
    path('app-systems/add', views.AppSystemEditView.as_view(), name="appsystem_add"),
    path('app-systems/<int:pk>/',
         views.AppSystemView.as_view(), name="appsystem"),
    path('app-systems/<int:pk>/edit',
         views.AppSystemEditView.as_view(), name="appsystem_edit"),
    path('app-systems/<int:pk>/delete',
         views.AppSystemDeleteView.as_view(), name="appsystem_delete"),
    path('app-systems/<int:pk>/changelog', ObjectChangeLogView.as_view(),
         name="appsystem_changelog", kwargs={'model': models.AppSystem}),

    # app system assignment
    path('app-system-assignment/add/', views.AppSystemAssignmentEditView.as_view(),
         name='appsystemassignment_add'),
    path('app-system-assignment/<int:pk>/edit/', views.AppSystemAssignmentEditView.as_view(),
         name='appsystemassignment_edit'),
    path('app-system-assignment/<int:pk>/delete/', views.AppSystemAssignmentDeleteView.as_view(),
         name='appsystemassignment_delete'),
)


# path('app-system/', views.AppSystem.as_view(), name="appsystem_"),
