from sym.flow.cli.commands.services.click.inquirer_choice import InquirerChoiceOption
from sym.flow.cli.commands.services.click.service_type_choice import ServiceTypeChoice
from sym.flow.cli.models.service_type import ServiceType


class ServiceTypeOption(InquirerChoiceOption):
    """Custom click.Option that uses inquirer to prompt users for service types.
    Choices can be set with the `service_type_choices` kwarg, otherwise it defaults to all public ServiceTypes.
    """

    def __init__(self, *args, **kwargs):
        kwargs["inquirer_choices"] = kwargs.get("inquirer_choices", ServiceType.public())
        super().__init__(*args, **kwargs)
        self.type = ServiceTypeChoice(choices=kwargs["inquirer_choices"])
