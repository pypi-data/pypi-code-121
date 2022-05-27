"""
InSituBuild models
"""

from django_mongoengine import fields, Document
from mongoengine import errors as mongoengine_errors

from core_main_app.commons import exceptions


class InSituBuild(Document):
    """Data Structure to handle the selected InSituBuild"""

    name = fields.StringField(blank=True)
    is_selected = fields.BooleanField(default=False)

    @staticmethod
    def get_all_builds_names():
        """Return the list of all the builds names

        Returns:

        """
        return InSituBuild.objects.all().values_list("name")

    @staticmethod
    def create_build(build):
        """Create and return a build object

        Args:
            build:

        Returns:

        """
        return InSituBuild.objects.create(name=build)

    @staticmethod
    def get_build_by_name(build_name):
        """Return the build object with the given argument

        Args:
            build_name:

        Returns:

        """
        return InSituBuild.objects.get(name=build_name)

    @staticmethod
    def get_selected_build_name():
        """Return the only one selected build object name

        Returns:

        """
        selected_build = InSituBuild.get_selected_build()
        if selected_build is not None:
            return selected_build.name
        return None

    @staticmethod
    def toggle_build_selection(build_name):
        """Toggle the boolean that indicates if a build is selected or not.
        Return the build with the given build name

        Args:
            build_name:

        Returns:

        """
        for build in InSituBuild.objects.all():
            if build.name == build_name:
                InSituBuild.objects.filter(name=build.name).update(is_selected=True)
            else:
                InSituBuild.objects.filter(name=build.name).update(is_selected=False)

        return InSituBuild.objects.get(name=build_name)

    @staticmethod
    def delete_all_builds():
        """Delete all build objects

        Returns:

        """
        InSituBuild.objects.all().delete()

    @staticmethod
    def get_selected_build():
        """Return the selected build

        Returns:

        """
        try:
            return InSituBuild.objects.get(is_selected=True)
        except mongoengine_errors.DoesNotExist as e:
            return None
        except Exception as ex:
            raise exceptions.ModelError(str(ex))
