""" REST views for the Query Ontology API
"""
from django.http import Http404
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from core_explore_tree_app.commons.enums import QueryOntologyStatus
from core_explore_tree_app.components.query_ontology import api as query_ontology_api
from core_explore_tree_app.rest.query_ontology.serializers import (
    QueryOntologySerializer,
)
from core_main_app.commons import exceptions
from core_main_app.access_control.exceptions import AccessControlError
from core_main_app.utils.decorators import api_staff_member_required
from core_main_app.utils.file import get_file_http_response


class QueryOntologyList(APIView):
    """List all Query Ontology, or create a new one"""

    def get(self, request):
        """Get all Query Ontology

        Args:

            request: HTTP request

        Returns:

            - code: 200
              content: List of Query Ontology
            - code: 500
              content: Internal server error
        """
        try:
            # Get object
            query_ontology_list = query_ontology_api.get_all()

            # Serialize object
            query_ontology_serializer = QueryOntologySerializer(
                query_ontology_list, many=True
            )

            # Return response
            return Response(query_ontology_serializer.data, status=status.HTTP_200_OK)
        except Exception as api_exception:
            content = {"message": str(api_exception)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @method_decorator(api_staff_member_required())
    def post(self, request):
        """Create a Query Ontology

        Parameters:

            {
                "title": "title",
                "content": "owl_content",
                "template": "template_id"
            }

        Args:

            request: HTTP request

        Returns:

            - code: 201
              content: Created Query Ontology
            - code: 400
              content: Validation error
            - code: 404
              content: Template was not found
            - code: 500
              content: Internal server error
        """
        try:
            # Build serializer
            query_ontology_serializer = QueryOntologySerializer(data=request.data)

            # Validate query ontology
            query_ontology_serializer.is_valid(True)

            # Save query ontology
            query_ontology_serializer.save()

            # Return the serialized query ontology
            return Response(
                query_ontology_serializer.data, status=status.HTTP_201_CREATED
            )
        except ValidationError as validation_exception:
            content = {"message": validation_exception.detail}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except exceptions.DoesNotExist:
            content = {"message": "Query Ontology not found."}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except Exception as api_exception:
            content = {"message": str(api_exception)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QueryOntologyDownload(APIView):
    """Download content from Query Ontology"""

    def get_object(self, request, pk):
        """Get Query ontology from db

        Args:

            request: HTTP request
            pk: ObjectId

        Returns:

            Query ontology
        """
        try:
            return query_ontology_api.get_by_id(pk)
        except exceptions.DoesNotExist:
            raise Http404

    @method_decorator(api_staff_member_required())
    def get(self, request, pk):
        """Download Query Ontology

        Args:

            request: HTTP request
            pk: ObjectId

        Returns:

            - code: 200
              content: OWL file
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            # Get object
            query_ontology_object = self.get_object(request, pk)
            return get_file_http_response(
                query_ontology_object.content,
                query_ontology_object.title,
                "text/xml",
                "owl",
            )
        except Http404:
            content = {"message": "Query Ontology not found."}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except Exception as api_exception:
            content = {"message": str(api_exception)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QueryOntologyActivate(APIView):
    """Activate a Query Ontology"""

    def get_object(self, request, pk):
        """Get Query ontology from db

        Args:

            request: HTTP request
            pk: ObjectId

        Returns:

            Query ontology
        """
        try:
            return query_ontology_api.get_by_id(pk)
        except exceptions.DoesNotExist:
            raise Http404

    @method_decorator(api_staff_member_required())
    def patch(self, request, pk):
        """Activate the given Query Ontology

        Args:

            request: HTTP request
            pk: ObjectId

        Returns:

            - code: 200
              content: {}
            - code: 403
              content: Access control error
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            # Get object
            query_ontology_object = self.get_object(request, pk)
            # Activate the given Query Ontology
            query_ontology_api.edit_status(
                query_ontology_object, QueryOntologyStatus.active.value
            )
            return Response({}, status=status.HTTP_200_OK)
        except AccessControlError as ace:
            content = {"message": str(ace)}
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        except Http404:
            content = {"message": "Query Ontology not found."}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except Exception as api_exception:
            content = {"message": str(api_exception)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
