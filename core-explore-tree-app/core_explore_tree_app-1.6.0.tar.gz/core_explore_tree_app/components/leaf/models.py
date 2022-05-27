""" Leaf model
"""
from django_mongoengine import Document, fields
from mongoengine import errors as mongoengine_errors
from mongoengine.errors import NotUniqueError

from core_main_app.commons import exceptions


class Leaf(Document):
    """Leaf object that represent a final node from the navigation tree"""

    current_node_id = fields.StringField(blank=False)
    # list of id of the documents under the current leaf
    docs_list = fields.ListField(blank=False)

    @staticmethod
    def get_all():
        """Get all Leaves objects.

        Returns:

        """
        return Leaf.objects().all()

    @staticmethod
    def get_by_id(leaf_id):
        """Return the object with the given id.

        Args:
            leaf_id:

        Returns:
            Leaf Object

        """
        try:
            return Leaf.objects.get(pk=str(leaf_id))
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(str(e))
        except Exception as ex:
            raise exceptions.ModelError(str(ex))

    @staticmethod
    def get_by_current_node_id(current_node_id):
        """Return the object with the given id.

        Args:
            current_node_id:

        Returns:
            Leaf Objects

        """
        try:
            return Leaf.objects.get(current_node_id=str(current_node_id))
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(str(e))
        except Exception as ex:
            raise exceptions.ModelError(str(ex))

    def save_object(self):
        """Custom save.

        Returns:
            Saved Instance.

        """
        try:
            return self.save()
        except mongoengine_errors.NotUniqueError as e:
            raise exceptions.NotUniqueError(str(e))
        except Exception as ex:
            raise exceptions.ModelError(str(ex))

    @staticmethod
    def delete_objects():
        """Custom delete all Leaf objects.

        Returns:
            Delete all Instances.

        """
        return Leaf.objects().delete()
