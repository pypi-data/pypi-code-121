from servicefoundry.internal.template.sf_definition import SFDefinition

from ..template.sf_template import SfTemplate


def parse(file):
    sf_definition = SFDefinition.create(file)
    template = SfTemplate.get_template(sf_definition.template)
    out = template.generate_service_def(sf_definition)
    return out
