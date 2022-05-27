""" Url router for the REST API
"""
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from core_explore_tree_app.rest.query_ontology import views as query_ontology_views

urlpatterns = [
    url(
        r"^query-ontology/$",
        query_ontology_views.QueryOntologyList.as_view(),
        name="core_explore_tree_rest_query_ontology_list",
    ),
    url(
        r"^query-ontology/download/(?P<pk>\w+)/$",
        query_ontology_views.QueryOntologyDownload.as_view(),
        name="core_explore_tree_rest_query_ontology_download",
    ),
    url(
        r"^query-ontology/activate/(?P<pk>\w+)/$",
        query_ontology_views.QueryOntologyActivate.as_view(),
        name="core_explore_tree_rest_query_ontology_activate",
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)
