DEFAULT_EPSILON_DOCS = {
    "ENGLISH": """
    :return: Default epsilon value as string
    """,
    "RUSSIAN": """
    :return: Значение по умолчанию в виде строки
    """
}

GET_EPSILON_DOCS = {
    "ENGLISH": """
    By using type of passed kind returns the current epsilon value in this type
    Example:
        | from decimal import Decimal
        |
        | from numeric_methods import settings
        |
        |
        | print(settings.get_epsilon(Decimal)

    :param kind: One of basic types see NUMBER type union
    :return: Current value of epsilon in indicated kind
    """,
    "RUSSIAN": """
    Используя тип передаваемого вида, возвращает текущее значение эпсилон в этом типе
    Пример:
        | from decimal import Decimal
        |
        | from numeric_methods import settings
        |
        |
        | print(settings.get_epsilon(Decimal)

    :param kind: Один из базовых типов, смотри объединение типов NUMBER
    :return: Текущее значение эпсилон в указанном типе
    """
}

GET_LANGUAGE_DOCS = {
    "ENGLISH": """
    Returns the current language of package
    Example:
        | from numeric_methods import settings
        |
        |
        | print(settings.get_language())  # ENGLISH

    :return: The string of full language name
    """,
    "RUSSIAN": """
    Возвращает название текущего языка пакета
    Пример:
        | from numeric_methods import settings
        |
        |
        | print(settings.get_language())  # ENGLISH

    :return: Строка полного названия языка
    """
}

RESTORE_EPSILON_DOCS = {
    "ENGLISH": """
    Restores default value of epsilon. Default value can be accessed through `default_epsilon` function
    """,
    "RUSSIAN": """
    Восстанавливает значение эпсилон по умолчанию. Это значение может быть доступно в `default_epsilon`
    """
}

SET_EPSILON_DOCS = {
    "ENGLISH": """
    Sets a new value for mathematics epsilon value. This value is used for value comparing in project.
    Changing this value may increase precision of evaluation in whole project. This value is not
    an epsilon of method functions - they have special epsilon parameters. Don't change it if you
    not need it
    Example:
        | from numeric_methods import mathematics
        | from numeric_methods import settings
        |
        |
        | print(mathematics.compare(0.0001, "==", 0.001))  # False
        | if settings.set_epsilon("0.001"):
        |     # Value 0.001 was sat only for example you can set any value you need
        |     print(mathematics.compare(0.0001, "==", 0.001))  # True

    :param value: String value of integer, probably in exponential notation
    :return: True if value was sat otherwise False
    """,
    "RUSSIAN": """
    Устанавливает новое значение эпсилон математического модуля. Это значени используется для сравнения
    значений в проекте. Изменение данного значение может повысить точность вычислений во всем проекте.
    Это значение не является эпсилоном функций - те имеют собственные параметры эпсилон. Не изменяйте
    значение, если это не требуется 
    Пример:
        | from numeric_methods import mathematics
        | from numeric_methods import settings
        |
        |
        | print(mathematics.compare(0.0001, "==", 0.001))  # False
        | if settings.set_epsilon("0.001"):
        |     # Значение 0.001 было установлено только в качестве примера, вы можете установить любое
        |     print(mathematics.compare(0.0001, "==", 0.001))  # True

    :param value: String value of integer, probably in exponential notation
    :return: True if value was sat otherwise False
    """
}

SET_LANGUAGE_DOCS = {
    "ENGLISH": """
    Sets up language for whole package. That can be very useful for users who don't know english (default language)
    Example:
        | from numeric_methods import settings
        |
        |
        | settings.set_language("ru")
        | print(settings.get_language())  # RUSSIAN

    :param name: Name of supporting language: ENGLISH or RUSSIAN (en or ru)
    :return: True if the language was applied to package otherwise False
    """,
    "RUSSIAN": """
    Устанавливает язык для всего пакета. Довольно полезно для пользователей, не знакомых с английским
    (языком по умолчанию)

    Пример:
        | from numeric_methods import settings
        |
        |
        | settings.set_language("ru")
        | print(settings.get_language())  # RUSSIAN

    :param name: Название поддерживаемого языка: АНГЛИЙСКИЙ или РУССКИЙ (анг или рус)
    :return: True если указанный язык применен к пакету, иначе False
    """
}
