FALSE_METHOD_DOCS = {
    "ENGLISH": """
    This method is implementing the false position method of root searching.

    Algorithm:
        x_(i + 1) = x_(i) - (end - x_(i)) * function(x_(i)) / (function(end) - function(x_(i)))
        return step, x_(i + 1)
        while not |x_(i + 1) - x_(i)| < epsilon:
            x_(i) = x_(i + 1)
            x_(i + 1) = x_(i) - (end - x_(i)) * function(x_(i)) / (function(end) - function(x_(i)))
            return step, x_(i + 1)
        return x_(i + 1)
        STOP

    Condition of using:
        [Automatic] Must be truth or ArithmeticError will raise: function(a) * function''(a) => 0 or function(b) * function''(b) => 0 

    Example:
        | from numeric_methods.one_variable import false_method
        |
        |
        | for line in false_method(lambda x: x**3 + 2*x - 11, lambda x: 6*x, 1, 2, 0.001):
        |     print(line)
    
    :param function: Lambda or defined function which must support type of number and be continuity
    :param double_differential: Double differential of function that must be continuity    
    :param a: Begin of the slice where root is
    :param b: End of the slice where root is
    :param epsilon: Required precision of the `function(x) = 0` root
    :return: Root of the `function(x) = 0` with indicated precision
    """,
    "RUSSIAN": """
    Данный метод реализует нахождение корня методом ложного положения.
    
    Алгоритм:
        x_(i + 1) = x_(i) - (end - x_(i)) * function(x_(i)) / (function(end) - function(x_(i)))
        return step, x_(i + 1)
        while not |x_(i + 1) - x_(i)| < epsilon:
            x_(i) = x_(i + 1)
            x_(i + 1) = x_(i) - (end - x_(i)) * function(x_(i)) / (function(end) - function(x_(i)))
            return step, x_(i + 1)
        return x_(i + 1)
        STOP
    
    Условия использования:
        [Автоматически] Должно быть истинной или будет вызвана ArithmeticError: function(a) * function''(a) => 0 или function(b) * function''(b) => 0

    Пример:
        | from numeric_methods.one_variable import false_method
        |
        |
        | for line in false_method(lambda x: x**3 + 2*x - 11, lambda x: 6*x, 1, 2, 0.001):
        |     print(line)

    :param function: Лямбда-функция или заранее определенная функция, которая должна поддерживать данный тип числа и быть непрерывной
    :param double_differential: Двойной дифференциал функции, который должен быть непрерывным
    :param a: Начало отрезка, в котором находится корень
    :param b: Конец отрезка, в котором находится корень
    :param epsilon: Требуемая точность корня уравнения `function(x) = 0`
    :return: Корень уравнения `function(x) = 0` с указанной точностью
    """
}

HALF_METHOD_DOCS = {
    "ENGLISH": """
    This method is implementing the half division's method of root searching.

    Algorithm:
        repeat while x_(i - 1)  -  x_(i) >= epsilon
            x = (a + b) / 2
            y = function(x)
            return step, a, b, x, y
            # -- [a] -- x -- [b] -->
            if function(a) * function(x) < 0 then
                # -- [a] -- [x] -- b -->
                a = a and b = x
            else if function(x) * function(b) < 0 then
                a = x and b = b
                # -- a -- [x] -- [b] -->
            else if function(x) == 0 then
                return x
                STOP
            else
                ERROR

    Conditions of using:
        [Automatic] Must be truth or ArithmeticError will raise: function(a_0) * function(b_0) < 0
        [Manually] Must be truth or some kind of exception will raise: function is continuous in [a_0, b_0]
    
    Example:
        | from numeric_methods.one_variable import half_method
        |
        |
        | # x ** 5 = 2
        | for line in half_method(lambda x: x ** 5 - 2, 1, 2, 0.001):
        |     print(line)

    :param function: Lambda or defined function which must support type of number and be continuity
    :param a: Begin of the slice where root is
    :param b: End of the slice where root is
    :param epsilon: Required precision of the `function(x) = 0` root
    :return: Root of the `function(x) = 0` with indicated precision
    """,
    "RUSSIAN": """
    Данный метод реализует нахождение корня методом половинного деления.
    
    Алгоритм:
        repeat while x_(i - 1)  -  x_(i) >= epsilon
            x = (a + b) / 2
            y = function(x)
            return step, a, b, x, y
            # -- [a] -- x -- [b] -->
            if function(a) * function(x) < 0 then
                # -- [a] -- [x] -- b -->
                a = a and b = x
            else if function(x) * function(b) < 0 then
                a = x and b = b
                # -- a -- [x] -- [b] -->
            else if function(x) == 0 then
                return x
                STOP
            else
                ERROR

    Условия использования:
        [Автоматически] Должно быть истинной или будет вызвана ArithmeticError: function(a_0) * function(b_0) < 0
        [Вручную] Должно быть истинно или будет вызвано исключение какого-то вида: функция непрерывна на [a_0, b_0]

    Пример:
        | from numeric_methods.one_variable import half_method
        |
        |
        | # x ** 5 = 2
        | for line in half_method(lambda x: x ** 5 - 2, 1, 2, 0.001):
        |     print(line)

    :param function: Лямбда-функция или заранее определенная функция, которая должна поддерживать данный тип числа и быть непрерывной
    :param a: Начало отрезка, в котором находится корень
    :param b: Конец отрезка, в котором находится корень
    :param epsilon: Требуемая точность корня уравнения `function(x) = 0`
    :return: Корень уравнения `function(x) = 0` с указанной точностью
    """
}

ITER_METHOD_DOCS = {
    "ENGLISH": """
    This method is implementing the simple iterations' method of root searching.

    Algorithm:
        x_(i + 1) = function(x_(i))
        return step, x_(i + 1)
        repeat while |x_(i + 1) - x_(i)| >= (1 - c_criterion) / c_criterion * epsilon
            x_(i) = x_(i + 1)
            x_(i + 1) = function(x_(i))
            return step, x_(i + 1)
        return x_(i + 1)
        STOP

    Conditions of using:
        [Manually] Must be truth or ArithmeticError will raise or algorithm will execute forever: |function'(x_(i))| < 1

    Example:
        | from math import sin
        |
        | from numeric_methods.one_variable import iter_method
        |
        |
        | # sin(x) / x = x
        | for line in iter_method(lambda x: sin(x) / x, 1, 0.001):
        |     print(line)

    :param function: Lambda or defined function which must support type of number, be continuity and represents left part of equation `function(x) = x`
    :param x: Start value of x (x_0)
    :param epsilon: Required precision of the `function(x) = x` root
    :param c_criterion: Convergence criterion
    :return: Root of the `function(x) = 0` with indicated precision
    """,
    "RUSSIAN": """
    Данный метод реализует нахождение корня методом простых итераций.

    Алгоритм:
        x_(i + 1) = function(x_(i))
        return step, x_(i + 1)
        repeat while |x_(i + 1) - x_(i)| >= (1 - c_criterion) / c_criterion * epsilon
            x_(i) = x_(i + 1)
            x_(i + 1) = function(x_(i))
            return step, x_(i + 1)
        return x_(i + 1)
        STOP

    Условия использования:
        [Вручную] Должно быть истинной или будет вызвана ArithmeticError или алгоритм будет исполнятся вечно: |function'(x_(i))| < 1

    Пример:
        | from math import sin
        |
        | from numeric_methods.one_variable import iter_method
        |
        |
        | # sin(x) / x = x
        | for line in iter_method(lambda x: sin(x) / x, 1, 0.001):
        |     print(line)

    :param function: Лямбда-функция или заранее определенная функция, которая должна поддерживать данный тип числа, быть непрерывной и представлять левую часть уравнения `function(x) = x`
    :param x: Начальное значение x (x_0)
    :param epsilon: Требуемая точность корня уравнения `function(x) = x`
    :param c_criterion: Критерий сходимости
    :return: Корень уравнения `function(x) = x` с указанной точностью
    """,
}

SECANT_METHOD_DOCS = {
    "ENGLISH": """
    This method is implementing the secant method of root searching.

    Algorithm:
        x_(i + 1) = x_(i) - (x_(i) - x_(i - 1)) * function(x_(i)) / (function(x_(i)) - function(x_(i - 1)))
        return step, next_x
        while not |x_(i + 1) - x_(i)| < epsilon:
            x_(i - 1) = x_(i)
            x_(i) = x_(i + 1)
            x_(i + 1) = x_(i) - (x_(i) - x_(i - 1)) * function(x_(i)) / (function(x_(i)) - function(x_(i - 1)))
            return step, x_(i + 1)
        return x_(i + 1)
        STOP

    Example:
        | from math exp
        |
        | from numeric_methods.one_variable import secant_method
        |
        |
        | for line in secant_method(lambda x: 4*(1 - x**2) - exp(x), 1, 0.5, 0.001):
        |     print(line)

    :param function: Lambda or defined function which must support type of number and be continuity
    :param x_prev: Previous value of x (x_0)
    :param x: Start value of x (x_1)
    :param epsilon: Required precision of the `function(x) = x` root
    :return: Root of the `function(x) = 0` with indicated precision
    """,
    "RUSSIAN": """
    Данный метод реализует нахождение корня методом секущих.

    Алгоритм:
        x_(i + 1) = x_(i) - (x_(i) - x_(i - 1)) * function(x_(i)) / (function(x_(i)) - function(x_(i - 1)))
        return step, next_x
        while not |x_(i + 1) - x_(i)| < epsilon:
            x_(i - 1) = x_(i)
            x_(i) = x_(i + 1)
            x_(i + 1) = x_(i) - (x_(i) - x_(i - 1)) * function(x_(i)) / (function(x_(i)) - function(x_(i - 1)))
            return step, x_(i + 1)
        return x_(i + 1)
        STOP

    Пример:
        | from math exp
        |
        | from numeric_methods.one_variable import secant_method
        |
        |
        | for line in secant_method(lambda x: 4*(1 - x**2) - exp(x), 1, 0.5, 0.001):
        |     print(line)

    :param function: Лямбда-функция или заранее определенная функция, которая должна поддерживать данный тип числа и быть непрерывной
    :param x_prev: Предыдущее значение x (x_0)
    :param x: Начальное значение x (x_1)
    :param epsilon: Требуемая точность корня уравнения `function(x) = x`
    :return: Корень уравнения `function(x) = x` с указанной точностью
    """
}

TANGENT_METHOD_DOCS = {
    "ENGLISH": """
    This method is implementing the tangent lines' method (Newton's method) of root searching.

    Algorithm:
        x_(i + 1) = x_(i) - function(x_(i)) / differential(x_(i))
        return step, x_(i + 1)
        while not |x_(i + 1) - x_(i)| < epsilon:
            x_(i) = x_(i + 1)
            x_(i + 1) = x_(i) - function(x_(i)) / differential(x_(i))
            return step, x_(i + 1)
        return x_(i + 1)
        STOP

    Conditions of using:
        [Automatic] Must be truth or ValueError will raise: x or double_differential must be specified
        [Automatic] Must be truth or ArithmeticError will raise: function(a) * function(b) < 0
        [Manually] Must be truth or ArithmeticError will raise or algorithm will execute forever: function is double differentiable continuously in [a_0, b_0]

    Example:
        | from numeric_methods.one_variable import tangent_method
        |
        |
        | # x ** 3 = 7
        | for line in tangent_method(lambda x: x**3 - 7, lambda x: 3*x**2, 1, 2, 0.001, double_differential=lambda x: 6*x):
        |     print(line)

    :param function: Lambda or defined function which must support type of number and be continuity
    :param differential: Differential of function that must be continuity
    :param a: Begin of the slice where root is
    :param b: End of the slice where root is
    :param epsilon: Required precision of the `function(x) = 0` root
    :param x: Start value of x (x_0)
    :param double_differential: Double differential of function that must be continuity
    :return: Root of the `function(x) = 0` with indicated precision
    """,
    "RUSSIAN": """
    Данный метод реализует нахождение корня методом касательных (методом Ньютона).

    Алгоритм:
        x_(i + 1) = x_(i) - function(x_(i)) / differential(x_(i))
        return step, x_(i + 1)
        while not |x_(i + 1) - x_(i)| < epsilon:
            x_(i) = x_(i + 1)
            x_(i + 1) = x_(i) - function(x_(i)) / differential(x_(i))
            return step, x_(i + 1)
        return x_(i + 1)
        STOP

    Условия использования:
        [Автоматически] Должно быть истинной или будет вызвана ValueError: x или double_differential должно быть указано
        [Автоматически] Должно быть истинной или будет вызвана ArithmeticError: function(a) * function(b) < 0
        [Вручную] Должно быть истинной или будет вызвана ArithmeticError или алгоритм будет исполнятся вечно: функция должна быть дважды непрерывно дифференцируема на [a, b]

    Пример:
        | from numeric_methods.one_variable import tangent_method
        |
        |
        | # x ** 3 = 7
        | for line in tangent_method(lambda x: x**3 - 7, lambda x: 3*x**2, 1, 2, 0.001, double_differential=lambda x: 6*x):
        |     print(line)

    :param function: Лямбда-функция или заранее определенная функция, которая должна поддерживать данный тип числа и быть непрерывной
    :param differential: Дифференциал функции, который должен быть непрерывным
    :param a: Начало отрезка, в котором находится корень
    :param b: Конец отрезка, в котором находится корень
    :param epsilon: Требуемая точность корня уравнения `function(x) = 0`
    :param x: Начальное значение x (x_0)
    :param double_differential: Двойной дифференциал функции, который должен быть непрерывным
    :return: Корень уравнения `function(x) = 0` с указанной точностью
    """
}
