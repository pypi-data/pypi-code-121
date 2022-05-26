from servicefoundry.core.deploy import _deploy, _deploy_local
from servicefoundry.core.notebook.notebook_util import get_default_callback
from servicefoundry.internal.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.internal.const import BUILD_DIR, SFY_DIR
from servicefoundry.internal.io.dummy_input_hook import DummyInputHook
from servicefoundry.internal.io.input_hook import InputHook
from servicefoundry.internal.package.package import Package
from servicefoundry.internal.packaged_component import PackagedComponent
from servicefoundry.internal.template.sf_definition import SFDefinition
from servicefoundry.internal.template.template_workflow import TemplateWorkflow


def _get_callback(callback):
    if not callback:
        return get_default_callback()
    else:
        return callback


class Component:
    def __init__(self, parameters, template, input_hook: InputHook = None):
        self.template = template
        self.project_folder = f"{SFY_DIR}/service"
        tfs_client = ServiceFoundryServiceClient.get_client()
        if not input_hook:
            input_hook = DummyInputHook(tfs_client)
        self.template_workflow = TemplateWorkflow(
            f"truefoundry.com/v1/{template}", input_hook
        )
        self.parameters = self.template_workflow.process_parameter(
            parameter_values=parameters
        )
        self.callback = get_default_callback()

    def extra_files(self):
        return self.template_workflow.template.list_dir_and_files()

    def _pack(self, overwrite=False):
        generated_def = self.template_workflow.template.generate_service_def(
            SFDefinition(self.template, self.parameters, None)
        )
        _package = Package(generated_def, BUILD_DIR)
        _package.clean(callback=self.callback)
        _package.pre_package(callback=self.callback)
        self.write(out_folder=BUILD_DIR, overwrite=overwrite)
        _package.package(callback=self.callback)
        packaged_component = PackagedComponent(
            build_dir=_package.build_dir, service_def=_package.generated_service_def
        )
        return packaged_component

    def deploy(self, overwrite=False, callback=None):
        packaged_component = self._pack(overwrite=overwrite)
        return _deploy(packaged_component, callback=_get_callback(callback))

    def deploy_local(self, overwrite=False, callback=None):
        packaged_component = self._pack(overwrite=overwrite)
        return _deploy_local(packaged_component, callback=_get_callback(callback))

    def write(self, out_folder="", overwrite=False):
        self.template_workflow.write(
            out_folder=out_folder,
            overwrite=overwrite,
            callback=self.callback,
        )


SERVICE_DEFAULT_TEMPLATE = "fastapi-inference"


class Service(Component):
    def __init__(
        self,
        parameters,
        template=SERVICE_DEFAULT_TEMPLATE,
        input_hook: InputHook = None,
    ):
        super().__init__(parameters, template, input_hook)


WEBAPP_DEFAULT_TEMPLATE = "streamlit-inference"


class Webapp(Component):
    def __init__(
        self, parameters, template=WEBAPP_DEFAULT_TEMPLATE, input_hook: InputHook = None
    ):
        super().__init__(parameters, template, input_hook)
