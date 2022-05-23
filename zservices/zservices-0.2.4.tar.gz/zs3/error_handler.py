from requests import Response


ec = {
    # Z Request Invalid Request Error
    'ZR001': 400,

    # Z Request Auth Error
    'ZA001': 401,

    # Z Request Internal Error
    'ZI001': 500,
    'ZI002': 500,
    'ZI003': 500,
    'ZI004': 404,

    # Z Request External Error
    'ZE001': 424,
    'ZE002': 424,
}

em = {
    # Z Request External Error
    'ZE001': 'Z Request External Invalid Response Code',
    'ZE002': 'Z Request External Invalid Response Text',
}


def parse_error(code: str, details, description=None, exc=None) -> dict:
    if isinstance(description, Response):
        description = str(description.content)

    errors = [{
        'code': code,
        'message': em.get(code),
        'details': details,
        'description': description,
        'exc': str(exc)
    }]
    return {'error': errors}
