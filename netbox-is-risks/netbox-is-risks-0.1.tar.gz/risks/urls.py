from django.urls import path
from . import models, views
from netbox.views.generic import ObjectChangeLogView

urlpatterns = (
    # risks
    path('risks/', views.RiskListView.as_view(), name='risk_list'),
    path('risks/add/', views.RiskEditView.as_view(), name='risk_add'),
    path('risks/<int:pk>/', views.RiskView.as_view(), name='risk'),
    path('risks/<int:pk>/edit/', views.RiskEditView.as_view(),
         name='risk_edit'),
    path('risks/<int:pk>/delete/', views.RiskDeleteView.as_view(),
         name='risk_delete'),
    path('risks/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='risk_changelog', kwargs={
         'model': models.Risk
         }),
    #  risk relation
    path('riskrelation/', views.RiskRelationListView.as_view(),
         name='riskrelation_list'),
    path('riskrelation/add/', views.RiskRelationEditView.as_view(),
         name='riskrelation_add'),
    path('riskrelation/<int:pk>/',
         views.RiskRelationView.as_view(), name='riskrelation'),
    path('riskrelation/<int:pk>/edit/',
         views.RiskRelationEditView.as_view(), name='riskrelation_edit'),
    path('riskrelation/<int:pk>/delete/',
         views.RiskRelationDeleteView.as_view(), name='riskrelation_delete'),
    path('riskrelation/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='riskrelation_changelog', kwargs={
         'model': models.RiskRelation
         }),
    # risk assignment
    path('riskassignment/add/', views.RiskAssignmentEditView.as_view(),
         name='riskassignment_add'),
    path('riskassignment/<int:pk>/edit/', views.RiskAssignmentEditView.as_view(),
         name='riskassignment_edit'),
    path('riskassignment/<int:pk>/delete/', views.RiskAssignmentDeleteView.as_view(),
         name='riskassignment_delete'),
)
