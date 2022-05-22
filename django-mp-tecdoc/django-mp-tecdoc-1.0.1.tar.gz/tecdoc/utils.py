
import re

from django.db.models.functions import Lower

from tecdoc.models import *
from tecdoc.constants import ADDITIONAL_CODES_MAX_LENGTH, CYRILLIC_MAP


def clean_code(text):

    result = re.sub(r'[\W_]+', '', text).lower()

    for k, v in CYRILLIC_MAP.items():
        result = result.replace(k, v)

    return result


def get_supplier(name):
    return Supplier.objects.filter(matchcode=name.upper()).first()


def get_crosses_text(supplier, code, initial=None, clean=False):

    text = initial or ''

    if not supplier or not code:
        return text

    new_codes = Cross.objects.filter(
        article_number=code.upper(),
        supplier=supplier
    ).values_list('oen_br', flat=True)

    new_codes = set(new_codes)

    new_codes |= set(text.replace('\r', '').split('\n'))

    new_codes = filter(bool, new_codes)

    if clean:
        new_codes = map(clean_code, new_codes)

    return '\n'.join(new_codes)


def clean_additional_codes(supplier_name, code, initial=None):

    supplier = get_supplier(supplier_name)

    return get_crosses_text(
        supplier,
        code,
        initial,
        clean=True
    )[:ADDITIONAL_CODES_MAX_LENGTH]
