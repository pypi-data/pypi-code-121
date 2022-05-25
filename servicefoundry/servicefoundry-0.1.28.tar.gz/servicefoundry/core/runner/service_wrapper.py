import os

from mako.template import Template

from servicefoundry.core.notebook.notebook_util import get_default_callback
from servicefoundry.core.runner.interceptor import Interceptor
from servicefoundry.internal.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.internal.const import BUILD_DIR
from servicefoundry.internal.package.python_requirements import PythonRequirements
from servicefoundry.internal.template.dummy_input_hook import DummyInputHook
from servicefoundry.internal.template.sf_template import SfTemplate
from servicefoundry.internal.template.template_workflow import TemplateWorkflow

TEMPLATE = "fastapi-inference"


def requirements_file_interceptor(interceptor: Interceptor):
    def _requirements_file_interceptor(source_lines):
        requirements = PythonRequirements(source_lines)
        requirements.update_requirements_txt(interceptor.get_dependencies())
        return requirements.get_requirements_txt()

    return _requirements_file_interceptor


def main_file_interceptor(interceptor: Interceptor):
    def _main_file_interceptor(source):
        template = Template(source)
        return template.render(
            functions=interceptor.get_functions(), module_name=interceptor.module_name
        )

    return _main_file_interceptor


class ServiceWrapper:
    def __init__(self, parameters, interceptor: Interceptor):
        self.project_folder = f"{BUILD_DIR}/service"
        tfs_client = ServiceFoundryServiceClient.get_client()
        sf_template = SfTemplate.get_template(f"truefoundry.com/v1/{TEMPLATE}")
        self.template_workflow = TemplateWorkflow(
            sf_template, DummyInputHook(tfs_client, parameters)
        )
        self.template_workflow.process_parameter(parameters=parameters)
        self.template_workflow.add_file_interceptor(
            "requirements.txt", requirements_file_interceptor(interceptor)
        )
        self.template_workflow.add_file_interceptor(
            "main.py", main_file_interceptor(interceptor)
        )

    def extra_files(self):
        return self.template_workflow.template.list_dir_and_files()

    def write(self, overwrite=False, verbose=True):
        self.template_workflow.write(
            out_folder="",
            overwrite=overwrite,
            verbose=verbose,
            callback=get_default_callback(),
        )

    def project_dir(self):
        return os.getcwd()
