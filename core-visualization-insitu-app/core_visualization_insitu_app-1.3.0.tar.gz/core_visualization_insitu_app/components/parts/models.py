"""
InsituPart models
"""

from django_mongoengine import fields, Document
from mongoengine import errors as mongoengine_errors

from core_main_app.commons import exceptions


class InSituPart(Document):
    """Data Structure to handle the selected InSituPart"""

    name = fields.StringField(blank=True)
    part_id = fields.StringField(blank=True)
    is_selected = fields.BooleanField(default=False)

    @staticmethod
    def get_all_parts_names():
        """Return the list of all the parts names

        Returns:

        """
        return InSituPart.objects.all().values_list("name")

    @staticmethod
    def create_part(part_name, part_id):
        """Create and return a part object

        Args:
            part_name:
            part_id:

        Returns:

        """
        return InSituPart.objects.create(name=part_name, part_id=part_id)

    @staticmethod
    def get_part_by_name(part_name):
        """Return the part object with the given argument

        Args:
            part_name:

        Returns:

        """
        return InSituPart.objects.get(name=part_name)

    @staticmethod
    def get_selected_part_name():
        """Return the only one selected part object name

        Returns:

        """
        selected_part = InSituPart.get_selected_part()
        if selected_part is not None:
            return selected_part.name
        return None

    @staticmethod
    def get_selected_part_id():
        """Return the only one selected part object id

        Returns:

        """
        selected_part = InSituPart.get_selected_part()
        if selected_part is not None:
            return selected_part.part_id
        return None

    @staticmethod
    def toggle_part_selection(part_name):
        """Toggle the boolean that indicates if a part is selected or not.
        Return the part with the given part name

        Args:
            part_name:

        Returns:

        """
        for part in InSituPart.objects.all():
            if part.name == part_name:
                InSituPart.objects.filter(name=part.name).update(is_selected=True)
            else:
                InSituPart.objects.filter(name=part.name).update(is_selected=False)

        return InSituPart.objects.get(name=part_name)

    @staticmethod
    def delete_all_parts():
        """Delete all part objects

        Returns:

        """
        InSituPart.objects.all().delete()

    @staticmethod
    def get_selected_part():
        """Return the selected part

        Returns:

        """
        try:
            return InSituPart.objects.get(is_selected=True)
        except mongoengine_errors.DoesNotExist as e:
            return None
        except Exception as ex:
            raise exceptions.ModelError(str(ex))
