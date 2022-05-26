from .get_id import get_applicant_id


def format_result(applicant_id, weight_id, result, interval, start, end):
    return {
        'id': get_applicant_id(interval, start, end),
        'applicant_id': applicant_id,
        'weight_id': weight_id,
        'score': result['wallet'],
        'results': result,
    }
