""" Navigation model
"""
from django_mongoengine import Document, fields
from mongoengine import errors as mongoengine_errors
from mongoengine.errors import NotUniqueError

from core_main_app.commons import exceptions


class Navigation(Document):
    """Data structure to handle the navigation tree"""

    name = fields.StringField(blank=True)
    parent = fields.StringField(blank=True)
    children = fields.ListField(blank=True)
    options = fields.DictField(blank=True)

    def save_object(self):
        """Custom save

        Returns:

        """
        try:
            return self.save()
        except NotUniqueError:
            raise exceptions.ModelError(
                "Unable to save the navigation object: not unique."
            )
        except Exception as ex:
            raise exceptions.ModelError(str(ex))

    @staticmethod
    def get_all():
        """Get all Navigation.

        Returns:
            Navigation(obj): Navigation object list

        """
        return Navigation.objects.all()

    @staticmethod
    def get_by_id(navigation_id):
        """Return the object with the given id.

        Args:
            navigation_id:

        Returns:
            Navigation(obj): Navigation object

        """
        try:
            return Navigation.objects.get(pk=str(navigation_id))
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(str(e))
        except Exception as ex:
            raise exceptions.ModelError(str(ex))

    @staticmethod
    def get_by_name(navigation_name):
        """Return the object with the given name.

        Args:
            navigation_name:

        Returns:
            Navigation(obj): Navigation object list

        """
        return Navigation.objects(name=str(navigation_name)).all()

    @staticmethod
    def delete_objects():
        """Custom delete all Navigation objects.

        Returns:
            Delete all Instances.

        """
        return Navigation.objects().delete()
