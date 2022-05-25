"""
InSituData models
"""

from django_mongoengine import fields, Document


class InSituData(Document):
    """Data Structure to handle the insitu_data related to the selection"""

    project = fields.StringField(blank=False)
    build = fields.StringField(blank=False)
    part = fields.StringField(blank=False)
    data_name = fields.StringField(blank=False)
    tab = fields.IntField(blank=False)
    images = fields.ListField(blank=True)
    active_image = fields.StringField(blank=True)
    layer_number = fields.IntField(blank=True)
    layer_numbers = fields.ListField(blank=True)

    @staticmethod
    def get_all_data():
        """Return the list of all the insitu_data

        Returns:

        """
        return InSituData.objects.all()

    @staticmethod
    def reset_default_data(project, build, part):
        """Return the insitu_data objects with the according arguments

        Args:
            project:
            build:
            part:

        Returns:

        """

        insitu_objects = InSituData.objects.filter(
            project=project, build=build, part=part
        )
        for insitu_object in insitu_objects:
            if insitu_object.layer_number != 0:
                insitu_object.layer_number = insitu_object.layer_numbers[0]
                insitu_object.active_image = insitu_object.images[0]
                insitu_object.save()

        return insitu_objects

    @staticmethod
    def get_data(project, build, part):
        """Get all insitu_data objects having the same project, build and part.
        Should be 7 of them (3 tabs for data_name builds command and 2 tabs for data_name melt pool and layer wise)

         Args:
             project:
             build:
             part:

         Returns:

        """

        return InSituData.objects.filter(project=project, build=build, part=part)

    @staticmethod
    def get_data_by_tab_name(project, build, part, data_name, tab):
        """Return a single insitu_data object

        Args:
            project:
            build:
            part:
            data_name:
            tab:

        Returns:

        """
        return InSituData.objects.get(
            project=project, build=build, part=part, data_name=data_name, tab=tab
        )

    @staticmethod
    def change_active_image(project, build, part, data_name, tab, active_image):
        """Change the active image from a single insitu_data object and return this image

        Args:
            project:
            build:
            part:
            data_name:
            tab:
            active_image:

        Returns:

        """
        InSituData.objects.filter(
            project=project, build=build, part=part, data_name=data_name, tab=tab
        ).update(active_image=active_image)
        return InSituData.objects.get(
            project=project, build=build, part=part, data_name=data_name, tab=tab
        ).active_image

    @staticmethod
    def create_data(
        project, build, part, data_name, tab, images=None, layer_numbers=None
    ):
        """Create an insitu data object

        Args:
            project:
            build:
            part:
            data_name:
            tab:
            images:
            layer_numbers:

        Returns:

        """
        if (images is not None) and (layer_numbers is not None):
            if len(images) > 0 and len(layer_numbers) > 0:
                return InSituData.objects.create(
                    project=project,
                    build=build,
                    part=part,
                    data_name=data_name,
                    tab=tab,
                    images=images,
                    layer_number=layer_numbers[0],
                    layer_numbers=layer_numbers,
                    active_image=images[0],
                )

        return InSituData.objects.create(
            project=project,
            build=build,
            part=part,
            data_name=data_name,
            tab=tab,
            images=images,
            layer_number=0,
            layer_numbers=[0],
            active_image="/static/core_visualization_insitu_app/user/img/no_data_layer.jpg",
        )

    @staticmethod
    def delete_all_data():
        """Delete all insitu_data objects

        Returns:

        """
        InSituData.objects.all().delete()

    @staticmethod
    def update_data(project, build, part, data_name, tab, layer_number, active_image):
        """Update the layer number and active image of insitu data object

        Args:
            project:
            build:
            part:
            data_name:
            tab:
            layer_number:
            active_image:

        Returns:

        """
        InSituData.objects.filter(
            project=project, build=build, part=part, data_name=data_name, tab=tab
        ).update(layer_number=layer_number, active_image=active_image)
        return InSituData.objects.get(
            project=project, build=build, part=part, data_name=data_name, tab=tab
        )

    @staticmethod
    def get_data_by_name_all_tabs(project, build, part, data_name):
        """Return all tabs from a single data name (ie build command, melt pool or layer wise)

        Args:
            project:
            build:
            part:
            data_name:

        Returns:

        """
        return InSituData.objects.filter(
            project=project, build=build, part=part, data_name=data_name
        )
