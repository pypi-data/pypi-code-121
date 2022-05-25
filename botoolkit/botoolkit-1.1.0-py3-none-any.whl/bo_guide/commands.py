from argparse import (
    Namespace,
)
from difflib import (
    Differ,
)
from distutils.util import (
    strtobool,
)
from pathlib import (
    Path,
)

from botoolkit.bo_conf.settings import (
    TOOL_NAME as BOCONF_TOOL_NAME,
)
from botoolkit.bo_git.helpers import (
    clone_or_pull_repository,
)
from botoolkit.bo_guide.mixins import (
    GuideArgumentsMixin,
    GuideBarsGitRepositoryArgumentsMixin,
    GuideBarsGooglePythonEnFilePathArgumentsMixin,
    GuideGoogleGitRepositoryArgumentsMixin,
    GuideGooglePythonEnFilePathArgumentsMixin,
    GuideNotificationTelegramArgumentsMixin,
)
from botoolkit.bo_guide.settings import (
    TOOL_NAME as BOGUIDE_TOOL_NAME,
)
from botoolkit.bo_telegram.helpers import (
    TelegramMessageSender,
)
from botoolkit.bo_telegram.settings import (
    TOOL_NAME as BOTELEGRAM_TOOL_NAME,
)
from botoolkit.bo_toolkit.settings import (
    TOOL_NAME as BOTOOLKIT_TOOL_NAME,
)
from botoolkit.core.commands import (
    BOConfiguredToolCommand,
    BOConfiguredToolConfigureCommand,
)
from botoolkit.core.consts import (
    ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS,
)
from botoolkit.core.loggers import (
    logger,
)


class BOGuideConfigureCommand(
    GuideArgumentsMixin,
    BOConfiguredToolConfigureCommand,
):
    """
    Команда конфигурирования инструмента boguide
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

        self.description = (
            'Configure boguide for manage of guides.'
        )

    def get_tool_name(self):
        return BOGUIDE_TOOL_NAME

    def get_allowed_empty_config_parameters(self):
        return ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.append(BOTOOLKIT_TOOL_NAME)

        return required_config_tool_names

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        super().take_action(
            parsed_args=parsed_args,
        )

        google_guide_git_repository_dir_path = Path(
            self._config.get(
                section='guide',
                option='google_git_repository_dir_path',
            ).value
        )
        google_guide_git_repository_url = self._config.get(
            section='guide',
            option='google_git_repository_url',
        ).value
        clone_or_pull_repository(
            path=google_guide_git_repository_dir_path,
            url=google_guide_git_repository_url,
            branch='gh-pages',
        )

        bars_guide_git_repository_dir_path = Path(
            self._config.get(
                section='guide',
                option='bars_git_repository_dir_path',
            ).value
        )
        bars_guide_git_repository_url = self._config.get(
            section='guide',
            option='bars_git_repository_url',
        ).value
        clone_or_pull_repository(
            path=bars_guide_git_repository_dir_path,
            url=bars_guide_git_repository_url,
        )


class BOGuidePythonCheckUpdatesCommand(
    GuideGoogleGitRepositoryArgumentsMixin,
    GuideGooglePythonEnFilePathArgumentsMixin,
    GuideBarsGitRepositoryArgumentsMixin,
    GuideBarsGooglePythonEnFilePathArgumentsMixin,
    GuideNotificationTelegramArgumentsMixin,
    BOConfiguredToolCommand,
):
    """
    Команда для проверки наличия изменений в Google Python Styleguide и
    оповещения разработчиков об их наличии
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

        self.description = (
            'Checking Google Python Styleguide updates.'
        )

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.extend(
            (
                BOCONF_TOOL_NAME,
                BOGUIDE_TOOL_NAME,
                BOTELEGRAM_TOOL_NAME,
            )
        )

        return required_config_tool_names

    def get_parser(
        self,
        prog_name,
    ):
        parser = super().get_parser(
            prog_name=prog_name,
        )

        parser.add_argument(
            '--notify',
            dest='notify',
            action='store',
            default=False,
            type=lambda x: bool(strtobool(x)),
            help=(
                'Notify developers about updates in Google Python Styleguide '
                'via Telegram channel.'
            ),
        )

        parser.add_argument(
            '--print_diff',
            dest='print_diff',
            action='store',
            default=False,
            type=lambda x: bool(strtobool(x)),
            help=(
                'Print difference.'
            ),
        )

        return parser

    def _update_repositories(
        self,
        parsed_args: Namespace,
    ):
        clone_or_pull_repository(
            path=Path(parsed_args.guide_google_git_repository_dir_path),
            url=parsed_args.guide_google_git_repository_url,
            branch='gh-pages',
        )

        clone_or_pull_repository(
            path=Path(parsed_args.guide_bars_git_repository_dir_path),
            url=parsed_args.guide_bars_git_repository_url,
        )

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        super().take_action(
            parsed_args=parsed_args,
        )

        self._update_repositories(
            parsed_args=parsed_args,
        )

        google_python_en_file_path = (
            Path(parsed_args.guide_google_git_repository_dir_path) /
            parsed_args.guide_google_python_en_file_path
        )
        with open(str(google_python_en_file_path)) as google_python_en_file:
            google_python_en_file_lines = google_python_en_file.readlines()

        bars_google_python_en_file_path = (
            Path(parsed_args.guide_bars_git_repository_dir_path) /
            parsed_args.guide_bars_google_python_en_file_path
        )
        with open(str(bars_google_python_en_file_path)) as bars_google_python_en_file:  # noqa
            bars_google_python_en_file_lines = bars_google_python_en_file.readlines()  # noqa

        if bars_google_python_en_file_lines != google_python_en_file_lines:
            logger.write(
                'difference found.\n'
            )

            if parsed_args.print_diff:
                differ = Differ()
                diff = list(
                    differ.compare(
                        a=bars_google_python_en_file_lines,
                        b=google_python_en_file_lines,
                    )
                )

                logger.write('\n'.join(diff))

            if parsed_args.notify:
                sender = TelegramMessageSender(
                    bot_api_token=self._botelegram_config['telegram']['bot_api_token'].value,  # noqa
                    chat_ids=(
                        parsed_args.guide_notification_telegram_chat_id,
                    )
                )

                sender.send(
                    message=(
                        'Были выявлены изменения в оригинальном Google Python '
                        'Styleguide! Необходимо произвести актуализацию '
                        'перевода.'
                    ),
                )
        else:
            logger.write('difference not found.')
