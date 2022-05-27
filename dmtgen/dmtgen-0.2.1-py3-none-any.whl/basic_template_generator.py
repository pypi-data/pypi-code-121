"""Basic generator, one template, one output file"""

from pathlib import Path
from typing import Dict
from jinja2.environment import Template
from dmt.package_generator import PackageGenerator
from dmt.common.package import Package
from .template_generator import TemplateBasedGenerator


class BasicTemplateGenerator(TemplateBasedGenerator):
    """Basic generator, one template, one output file"""

    def generate(self,package_generator: PackageGenerator, template : Template, outputfile: Path, config: Dict):
        """Basic generator, one template, one output file"""

        package = package_generator.root_package
        self.__generate_package(package, template, outputfile)

    def __generate_package(self, package: Package,template, outputfile):
        model = {}
        package_name = package.name
        model["package_name"] = package_name
        model["version"] = 0.0
        model["package_class"] = self.first_to_upper(package_name) + "PackageDescription"
        model["lib"] = package_name+"-gen"
        model["description"] = package_name + " - Generated types"
        etypes = []

        for blueprint in package.blueprints:
            etype = {}
            name = blueprint.name
            etype["name"] = self.first_to_upper(name)
            etype["file_basename"] = name.lower()
            etypes.append(etype)

        model["types"] = etypes

        with open(outputfile, 'w') as file:
            file.write(template.render(model))

    @staticmethod
    def first_to_upper(string):
        """ Make sure the first letter is uppercase """
        return string[:1].upper() + string[1:]
