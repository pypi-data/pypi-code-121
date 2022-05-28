def _section_result_to_json(result):
    _name, (_ok, _runs, _info) = result
    return dict(
        name=_name,
        ok=_ok,
        commands=[item.json for item in _runs],
        information=_info,
    )


def result_to_json(success: bool, result):
    """
    from result to json data
    :param success: success or not
    :param result: full result
    :return: full json
    """
    return dict(
        ok=not not success,
        sections=[_section_result_to_json(item) for item in result],
    )
