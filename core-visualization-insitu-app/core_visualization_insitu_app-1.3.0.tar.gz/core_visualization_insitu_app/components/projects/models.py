"""
InSituProject models
"""

from django_mongoengine import fields, Document
from mongoengine import errors as mongoengine_errors

CQL_NAMESPACE = "http://siam.nist.gov/Database-Navigation-Ontology#"


class InSituProject(Document):
    """Data Structure to handle the selected projects"""

    name = fields.StringField(blank=True)
    is_selected = fields.BooleanField(default=False)

    @staticmethod
    def create_project(project):
        """Create project with the given argument as project name and return the project

        Args:
            project:
        Returns:

        """
        return InSituProject.objects.create(name=project)

    @staticmethod
    def get_project_by_name(project_name):
        """Return the project with the given name

        Args:
            project_name:

        Returns:

        """
        return InSituProject.objects.get(name=project_name)

    @staticmethod
    def toggle_project_selection(project_name):
        """Toggle the boolean that indicates if a project is selected or not.
        Return the project with the given project name

        Args:
            project_name:
        Returns:

        """
        for project in InSituProject.objects.all():
            if project.name == project_name:
                InSituProject.objects.filter(name=project.name).update(is_selected=True)
            else:
                InSituProject.objects.filter(name=project.name).update(
                    is_selected=False
                )

        return InSituProject.objects.get(name=project_name)

    @staticmethod
    def get_selected_project_name():
        """Return the list of all the projects names whose 'is_selected' is True

        Returns:

        """
        try:
            return InSituProject.objects.get(is_selected=True).name
        except mongoengine_errors.DoesNotExist as e:
            return None

    @staticmethod
    def delete_all_projects():
        """Delete all projects

        Returns:

        """
        InSituProject.objects.all().delete()
