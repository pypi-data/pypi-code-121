import hashlib
import json


def hash_record(record, desired_fields):
    """
    Create a consistent hash from an input record using only fields from the desired field list

    Uses json.dumps, since sorted won't sort nested fields, if any exist in the input record
    """
    record_hash = hashlib.md5()
    filtered_record = filter_record_by_mask(record, desired_fields)
    record_string = json.dumps(filtered_record, sort_keys=True)
    record_hash.update(record_string.encode())
    return record_hash


def filter_record_by_mask(input_record, mask):
    output_record = {}
    for field, value in mask.items():
        if isinstance(value, dict):
            output_record[field] = filter_record_by_mask(input_record[field], value)
        elif value:
            output_record[field] = input_record[field]
    return output_record
