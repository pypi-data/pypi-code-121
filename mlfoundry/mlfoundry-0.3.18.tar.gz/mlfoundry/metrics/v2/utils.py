import typing


def get_class_names(predictions, actuals) -> typing.List:
    class_names = set()
    if predictions is not None:
        class_names.update(predictions)
    if actuals is not None:
        class_names.update(actuals)
    class_names = sorted(class_names)
    return class_names
