from botoolkit.bo_git.helpers import (
    ls_remote,
)
from botoolkit.bo_guide.consts import (
    BARS_GUIDE_GIT_REPOSITORY_DIR_PATH,
    GOOGLE_GUIDE_GIT_REPOSITORY_DIR_PATH,
)
from botoolkit.core.strings import (
    WRONG_ARGUMENT_VALUE,
)


class GuideGoogleGitRepositoryArgumentsMixin:
    """
    Добавляет параметры
        --guide_google_git_repository_url
        --guide_google_git_repository_dir_path
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'guide',
                    'option': 'google_git_repository_url',
                    'help': 'URL репозитория с гайдами Google.',
                },
                {
                    'section': 'guide',
                    'option': 'google_git_repository_dir_path',
                    'help': (
                        'Абсолютный путь до директории для клонирования репозитория (со склонированным репозиторием) с '
                        'гайдами Google.'
                    ),
                },
            )
        )

    def _validate_guide_google_git_repository_url(self):
        """
        Валидация значения параметра guide_google_git_repository_url
        """
        if self._parsed_args.guide_google_git_repository_url:
            references = ls_remote(
                url=self._parsed_args.guide_google_git_repository_url,
            )

            if not references['HEAD']:
                raise RuntimeError(
                    WRONG_ARGUMENT_VALUE.format(
                        argument_name='guide_google_git_repository_url',
                    )
                )

    def _fill_guide_google_git_repository_dir_path(
        self,
        value: str,
    ):
        """
        Заполнение значения параметра guide_google_git_repository_dir_path
        """
        if not value:
            value = str(GOOGLE_GUIDE_GIT_REPOSITORY_DIR_PATH)

        self._config.set(
            section='guide',
            option='google_git_repository_dir_path',
            value=value,
        )


class GuideGooglePythonEnFilePathArgumentsMixin:
    """
    Добавляет параметры
        --guide_google_python_en_file_path
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'guide',
                    'option': 'google_python_en_file_path',
                    'help': 'Относительный путь до оригинального гайда для Python от Google.'
                },
            )
        )
        

class GuideBarsGitRepositoryArgumentsMixin:
    """
    Добавляет параметры
        --guide_bars_git_repository_url
        --guide_bars_git_repository_dir_path
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'guide',
                    'option': 'bars_git_repository_url',
                    'help': 'URL репозитория с гайдами БАРС Груп',
                },
                {
                    'section': 'guide',
                    'option': 'bars_git_repository_dir_path',
                    'help': (
                        'Абсолютный путь до директории для клонирования репозитория (со склонированным репозиторием) с '
                        'гайдами БАРС Груп.'
                    ),
                },
            )
        )

    def _validate_guide_bars_git_repository_url(self):
        """
        Валидация значения параметра guide_bars_git_repository_url
        """
        if self._parsed_args.guide_bars_git_repository_url:
            references = ls_remote(
                url=self._parsed_args.guide_bars_git_repository_url,
            )

            if not references['HEAD']:
                raise RuntimeError(
                    WRONG_ARGUMENT_VALUE.format(
                        argument_name='guide_bars_git_repository_url',
                    )
                )

    def _fill_guide_bars_git_repository_dir_path(
        self,
        value: str,
    ):
        """
        Заполнение значения параметра guide_bars_git_repository_dir_path
        """
        if not value:
            value = str(BARS_GUIDE_GIT_REPOSITORY_DIR_PATH)

        self._config.set(
            section='guide',
            option='bars_git_repository_dir_path',
            value=value,
        )


class GuideBarsGooglePythonEnFilePathArgumentsMixin:
    """
    Добавляет параметры
        --guide_bars_google_python_en_file_path
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'guide',
                    'option': 'bars_google_python_en_file_path',
                    'help': 'Относительный путь до копии Python гайда от Google в репозитории с гайдами БАРС Груп.',
                },
            )
        )


class GuideNotificationTelegramArgumentsMixin:
    """
    Добавляет параметры
        --guide_notification_telegram_chat_id
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'guide',
                    'option': 'notification_telegram_chat_id',
                    'help': (
                        'Telegram Chat ID для отправки оповещений.'
                    ),
                },
            )
        )


class GuideArgumentsMixin(
    GuideGoogleGitRepositoryArgumentsMixin,
    GuideGooglePythonEnFilePathArgumentsMixin,
    GuideBarsGitRepositoryArgumentsMixin,
    GuideBarsGooglePythonEnFilePathArgumentsMixin,
    GuideNotificationTelegramArgumentsMixin,
):
    """
    Добавляет параметры
        --guide_google_git_repository_url
        --guide_google_git_repository_dir_path
        --guide_google_python_en_file_path
        --guide_bars_git_repository_url
        --guide_bars_git_repository_dir_path
        --guide_bars_google_python_en_file_path
        --guide_notification_telegram_chat_id
    """