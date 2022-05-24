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
    ignore_empty,
):
    return {
        "name": [ignore_empty, unicode_safe],
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
    unicode_safe,
    flakes_flake_id_exists,
):
    return {
        "id": [not_missing, unicode_safe],
        "data": [not_missing, convert_to_json_if_string, dict_only],
        "parent_id": [ignore_missing, flakes_flake_id_exists],
        "extras": [ignore_missing, convert_to_json_if_string, dict_only],
        "__extras": [ignore],
    }


@validator_args
def flake_override(not_empty, unicode_safe):
    schema = flake_update()
    schema.pop("id")
    schema["name"] = [not_empty, unicode_safe]
    return schema


@validator_args
def flake_delete(not_missing, unicode_safe):
    return {
        "id": [not_missing, unicode_safe],
    }


@validator_args
def flake_show(not_missing, boolean_validator, unicode_safe):
    return {
        "id": [not_missing, unicode_safe],
        "expand": [boolean_validator],
    }


@validator_args
def flake_list(
    boolean_validator, ignore_missing, unicode_safe, json_list_or_string
):
    return {
        "expand": [boolean_validator],
        "extra_path": [ignore_missing, json_list_or_string],
        "extra_value": [ignore_missing, unicode_safe],
    }


@validator_args
def flake_lookup(boolean_validator, not_empty, unicode_safe):
    return {
        "name": [not_empty, unicode_safe],
        "expand": [boolean_validator],
    }


@validator_args
def flake_validate(boolean_validator, not_missing, unicode_safe):
    return {
        "id": [not_missing, unicode_safe],
        "expand": [boolean_validator],
        "schema": [not_missing],
    }


@validator_args
def data_validate(convert_to_json_if_string, dict_only, not_missing):
    return {
        "data": [not_missing, convert_to_json_if_string, dict_only],
        "schema": [not_missing],
    }


@validator_args
def data_example(not_missing, convert_to_json_if_string, dict_only, default):
    return {
        "factory": [not_missing],
        "data": [default("{}"), convert_to_json_if_string, dict_only],
    }


@validator_args
def flake_materialize(
    boolean_validator, not_missing, flakes_into_api_action, unicode_safe
):
    return {
        "id": [not_missing, unicode_safe],
        "expand": [boolean_validator],
        "remove": [boolean_validator],
        "action": [not_missing, flakes_into_api_action],
    }


@validator_args
def flake_combine(
    default,
    not_missing,
    json_list_or_string,
    convert_to_json_if_string,
    dict_only,
):
    return {
        "id": [not_missing, json_list_or_string],
        "expand": [default("{}"), convert_to_json_if_string, dict_only],
    }


@validator_args
def flake_merge(boolean_validator, ignore_missing):
    schema = flake_combine()
    schema["remove"] = [boolean_validator]
    schema["destination"] = [ignore_missing]
    return schema
