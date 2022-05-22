from ckan.logic.schema import validator_args


@validator_args
def flake_create(
    not_missing,
    convert_to_json_if_string,
    dict_only,
    ignore,
    ignore_missing,
    unicode_safe,
    flakes_flake_id_exists,
):
    return {
        "name": [ignore_missing, unicode_safe],
        "data": [not_missing, convert_to_json_if_string, dict_only],
        "parent_id": [ignore_missing, flakes_flake_id_exists],
        "extras": [ignore_missing, convert_to_json_if_string, dict_only],
        "__extras": [ignore],
    }


@validator_args
def flake_update(
    not_missing,
    convert_to_json_if_string,
    dict_only,
    ignore,
    ignore_missing,
):
    return {
        "id": [not_missing],
        "data": [not_missing, convert_to_json_if_string, dict_only],
        "parent_id": [ignore_missing],
        "extras": [ignore_missing, convert_to_json_if_string, dict_only],
        "__extras": [ignore],
    }


@validator_args
def flake_delete(not_missing):
    return {
        "id": [not_missing],
    }


@validator_args
def flake_show(not_missing, boolean_validator):
    return {
        "id": [not_missing],
        "expand": [boolean_validator],
    }


@validator_args
def flake_list(boolean_validator):
    return {
        "expand": [boolean_validator],
    }


@validator_args
def flake_lookup(boolean_validator, not_missing):
    return {
        "name": [not_missing],
        "expand": [boolean_validator],
    }


@validator_args
def flake_validate(boolean_validator, not_missing):
    return {
        "id": [not_missing],
        "expand": [boolean_validator],
        "schema": [not_missing],
    }


@validator_args
def data_validate(convert_to_json_if_string, dict_only, not_missing):
    return {
        "data": [not_missing, convert_to_json_if_string, dict_only],
        "schema": [not_missing],
    }
