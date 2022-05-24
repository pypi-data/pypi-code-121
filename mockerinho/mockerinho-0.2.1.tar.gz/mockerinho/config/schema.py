from schema import Schema, And, Optional

from . import validators


config_file_schema = Schema({
    'request': Schema({
        'path': And(str, validators.is_request_path_valid),
        'method': And(str, validators.is_request_method_valid),
        Optional('headers'): [Schema({
            'name': And(str, validators.is_header_name_valid),
            'value': And(str, validators.is_header_value_valid),
            'value_matcher': And(str, validators.is_header_value_matcher_valid)
        })],
        Optional('query'): Optional([Schema({
            'name': And(str, validators.is_query_name_valid),
            'value': And(str, validators.is_query_value_valid),
            'value_matcher': And(str, validators.is_query_value_matcher_valid)
        })]),
        Optional('body'): Schema({
            'value': str,
            'value_matcher': And(str, validators.is_request_body_value_matcher_valid)
        })
    }),
    'response': Schema({
        Optional('body'): str,
        Optional('headers'): [Schema({
            'name': And(str, validators.is_header_name_valid),
            'value': And(str, validators.is_header_value_valid)
        })],
        'status': And(int, validators.is_status_code_valid)
    })
})
