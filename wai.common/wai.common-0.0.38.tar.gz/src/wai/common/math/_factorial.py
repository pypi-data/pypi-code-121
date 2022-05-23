def factorial(
        of: int,
        down_to: int = 0
) -> int:
    """
    Returns the multiplication of all positive integers from ``of`` down
    to (but not including) ``down_to``.

    :param of:
                The greatest positive integer to include in the product.
    :param down_to:
                The greatest positive integer, less than ``of``, to exclude
                from the product.
    :return:
                The factorial of ``of`` down to ``down_to``. If ``of`` equals
                ``down_to``, the result is ``of``.
    """
    if down_to < 0:
        raise ArithmeticError(f"'down_to' cannot be less than 0, got {down_to}")
    if of < down_to:
        raise ArithmeticError(f"'of' must be at least 'down_to', got 'of = {of}, 'down_to' = {down_to}")

    result = 1
    while of > down_to:
        result *= of
        of -= 1

    return result
