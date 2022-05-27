""" DataCached model
"""
from django_mongoengine import fields, Document
from mongoengine import errors as mongoengine_errors
from mongoengine.errors import NotUniqueError

from core_main_app.commons import exceptions


class DataCached(Document):
    """DataCached object that has been cached by the system"""

    cached_documents_dict = fields.ListField(blank=False)
    cached_documents_objects = fields.ListField(blank=True)
    current_node = fields.StringField(blank=False)

    @staticmethod
    def get_all():
        """Get all DataCached objects.

        Returns:

        """
        return DataCached.objects().all()

    @staticmethod
    def get_by_id(data_cached_id):
        """Return the object with the given id.

        Args:
            data_cached_id:

        Returns:
            DataCached Object

        """
        try:
            return DataCached.objects.get(pk=str(data_cached_id))
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
        return DataCached.objects().delete()
