class BOBARSDockGeneralArgumentsMixin:
    """
    Добавляет параметры
        --dock_barsdock_dir_path
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'dock',
                    'option': 'barsdock_dir_path',
                    'help': 'Абсолютный путь до директории barsdock.',
                },
            )
        )
