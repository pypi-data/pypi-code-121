from argparse import (
    Namespace,
)

import docker

from botoolkit.bo_git.mixins import (
    WebBBAppBranchArgumentMixin,
)
from botoolkit.bo_git.settings import (
    TOOL_NAME as BOGIT_TOOL_NAME,
)
from botoolkit.bo_registry.mixins import (
    RegistryURLArgumentsMixin,
)
from botoolkit.bo_registry.settings import (
    TOOL_NAME as BOREGISTRY_TOOL_NAME,
)
from botoolkit.bo_toolkit.mixins import (
    BOToolkitPrivateKeyArgumentMixin,
    DockerArgumentsMixin,
)
from botoolkit.bo_toolkit.settings import (
    TOOL_NAME as BOTOOLKIT_TOOL_NAME,
)
from botoolkit.bo_web_bb.mixins import (
    WebBBDockerMixin,
)
from botoolkit.bo_web_bb.services import (
    BaseWebBBAppServiceManager,
)
from botoolkit.bo_web_bb.settings import (
    BASE_WEB_BB_APP_IMAGE_DIR_PATH,
    TOOL_NAME as BOWEBBB_TOOL_NAME,
)
from botoolkit.core.commands import (
    BOConfiguredToolCommand,
    BOConfiguredToolConfigureCommand,
)
from botoolkit.core.consts import (
    ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS,
)


class ConfigureBOWebBBCommand(
    WebBBDockerMixin,
    BOConfiguredToolConfigureCommand,
):
    """
    Команда конфигурирования инструмента bowebbb
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.description = 'Configure bowebb for working with web_bb project.'

    def get_tool_name(self):
        return BOWEBBB_TOOL_NAME

    def get_allowed_empty_config_parameters(self):
        return ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.append(BOTOOLKIT_TOOL_NAME)

        return required_config_tool_names


class BuildBaseWebBBApplicationImageCommand(
    BOToolkitPrivateKeyArgumentMixin,
    RegistryURLArgumentsMixin,
    WebBBAppBranchArgumentMixin,
    DockerArgumentsMixin,
    WebBBDockerMixin,
    BOConfiguredToolCommand,
):
    """
    Команда для сборки базового образа приложения web_bb_app
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.description = 'Building base web_bb_app image by client settings.'

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.extend(
            (
                BOREGISTRY_TOOL_NAME,
                BOGIT_TOOL_NAME,
                BOWEBBB_TOOL_NAME,
                BOTOOLKIT_TOOL_NAME,
            )
        )

        return required_config_tool_names

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        super().take_action(
            parsed_args=parsed_args,
        )

        docker_client = docker.from_env()

        image_repository = self._parsed_args.web_bb_docker_base_image_name

        manager = BaseWebBBAppServiceManager(
            docker_client=docker_client,
            network=self._parsed_args.docker_network,
        )

        manager.build(
            web_bb_app_branch=self._parsed_args.web_bb_app_branch,
            build_dir_path=BASE_WEB_BB_APP_IMAGE_DIR_PATH,
            toolkit_general_rsa_private_key=(
                self._parsed_args.toolkit_general_rsa_private_key
            ),
            image_repository=image_repository,
            image_tag=self._parsed_args.web_bb_app_branch,
            registry_url=self._parsed_args.registry_url,
            force_push=True,
        )
