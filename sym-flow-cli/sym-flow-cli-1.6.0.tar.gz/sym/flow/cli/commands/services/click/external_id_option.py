import click


class ExternalIdOption(click.Option):
    """Custom click.Option whose prompt dynamically changes depending on the "service_type" value inputted"""

    def __init__(self, *args, **kwargs):
        super(ExternalIdOption, self).__init__(*args, **kwargs)

    def prompt_for_value(self, ctx):
        """Dynamically change external_id prompt text based on service_type"""
        # ServiceTypes Enums are defined in all caps
        self.prompt = ctx.params["service_type"].external_id_name

        return super().prompt_for_value(ctx)
