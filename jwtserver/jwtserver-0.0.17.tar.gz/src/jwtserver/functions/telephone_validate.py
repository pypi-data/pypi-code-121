import phonenumbers
from fastapi import HTTPException


def telephone_validate(telephone):
    if not phonenumbers.is_valid_number(phonenumbers.parse(telephone, None)):
        raise HTTPException(status_code=400, detail="phonenumbers is not valid")
    return telephone
