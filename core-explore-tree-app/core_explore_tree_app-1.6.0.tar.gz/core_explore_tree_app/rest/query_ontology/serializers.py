""" Serializers used throughout the query ontology Rest API
"""
from builtins import object
from rest_framework_mongoengine.serializers import DocumentSerializer

from core_explore_tree_app.components.query_ontology import api as query_ontology_api
from core_explore_tree_app.components.query_ontology.models import QueryOntology


class QueryOntologySerializer(DocumentSerializer):
    """Query Ontology serializer"""

    class Meta(object):
        """Meta"""

        model = QueryOntology
        fields = [
            "id",
            "title",
            "content",
            "template",
            "status",
            "last_modification_date",
        ]
        read_only_fields = (
            "id",
            "status",
            "last_modification_date",
        )

    def create(self, validated_data):
        """Create and return a new `Query Ontology` instance, given the validated data."""
        # Create QueryOntology
        instance = QueryOntology(
            title=validated_data["title"],
            content=validated_data["content"],
            template=validated_data["template"],
        )
        # Save the QueryOntology
        return query_ontology_api.upsert(instance)
