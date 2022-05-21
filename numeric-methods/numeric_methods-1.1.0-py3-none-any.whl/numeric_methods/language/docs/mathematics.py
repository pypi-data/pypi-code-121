COMPARE_DOCS = {
    "ENGLISH": """
    Makes compare operation of the indicated kind and lhs, rhs values of the same type.
    This function is using mathematics epsilon that can be sat from settings.
    Example:
        | from numeric_methods import mathematics
        | from numeric_methods import settings
        |
        |
        | if mathematics.compare(0.0001, "==", 0.00001):
        |     print("That can't be possible")
        |
        | settings.set_epsilon("0.0001")
        |
        | if mathematics.compare(0.0001, "==", 0.00001):
        |     print("That will be printed")

    :param lhs: Left-hand-side value
    :param kind: String of compare type: <, >, <=, >= or ==
    :param rhs: Right-hand-side value
    :return: Result of compare operation of indicated type
    """,
    "RUSSIAN": """
    Делает проверку указанного вида левого и правого значений одного типа.
    Эта функция использует эпсилон математического модуля, который может быть
    установлен в настройках.
    Пример:
        | from numeric_methods import mathematics
        | from numeric_methods import settings
        |
        |
        | if mathematics.compare(0.0001, "==", 0.00001):
        |     print("Это не произойдет")
        |
        | settings.set_epsilon("0.0001")
        |
        | if mathematics.compare(0.0001, "==", 0.00001):
        |     print("Это будет напечатано")

    :param lhs: Значение слева
    :param kind: Строка сравнения: <, >, <=, >= or ==
    :param rhs: Значение справа
    :return: Результат операции сравнения указанного типа
    """
}

CONVERT_DOCS = {
    "ENGLISH": """
    This function convert value from its type to indicated if type
    is participant of NUMBER. This function needed because not all
    types can be converted directly.
    Example:
        | from decimal import Decimal
        | from fractions import Fraction
        |
        | from numeric_methods import mathematics
        |
        |
        | # value of this type cannot be converted into Decimal directly
        | # print(Decimal(Fraction(1, 2)))  # <-- raises an exception
        | print(mathematics.convert(Fraction(1, 2), Decimal))

    :param value: Value which will be converted
    :param into: Destination convert type
    :return: Converted number in indicated type
    """,
    "RUSSIAN": """
    Эта функция конвертирует значение данного типа в указанный тип
    из перечисления NUMBER. Данная функция необходима, потому что
    не все преобразования могут быть совершены напрямую.
    Пример:
        | from decimal import Decimal
        | from fractions import Fraction
        |
        | from numeric_methods import mathematics
        |
        |
        | # Значение данного типа не может быть преобразовано в Decimal напрямую
        | # print(Decimal(Fraction(1, 2)))  # <-- вызывает исключение
        | print(mathematics.convert(Fraction(1, 2), Decimal))

    :param value: Значение, которое будет конвертировано
    :param into: Конечный тип
    :return: Конвертированное число в указанном типе
    """
}

WIDEST_TYPE_DOCS = {
    "ENGLISH": """
    This function accept instances of NUMBER and returns most widest type of them:
        float > Decimal > Fraction
    These types are ordered by precision safety
    Example:
        | from fractions import Fraction
        |
        | from numeric_methods import mathematics
        |
        |
        | print(mathematics.widest_type(0.0, 2.0, Fraction(3, 1), Fraction(-1, 1)))  # <class 'fractions.Fraction'>

    :param instances: Values of allowed NUMBER types
    :return: The most widest type
    """,
    "RUSSIAN": """
    Эта функция принимает экземпляры NUMBER и возвращает наиболее широкий из нихЖ
        float > Decimal > Fraction
    Эти типы отсортированы в порядке наибольшего сохранения точности
    Пример:
        | from fractions import Fraction
        |
        | from numeric_methods import mathematics
        |
        |
        | print(mathematics.widest_type(0.0, 2.0, Fraction(3, 1), Fraction(-1, 1)))  # <class 'fractions.Fraction'>

    :param instances: Экземпляры разрешенных типов из NUMBER
    :return: Наиболее широкий тип
    """
}