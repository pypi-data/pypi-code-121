import hashlib
import re
from functools import partial

from six import BytesIO


def hash_file(file, block_size=65536):
    hash_ = hashlib.md5()
    for buf in iter(partial(file.read, block_size), b''):
        hash_.update(buf)

    return hash_.hexdigest()


def accept_file(self, file_):
    if isinstance(file_, str):
        if '://' in file_:
            # URL supplied
            response = self.requests.get(url=file_, timeout=(30, 60))
            file_io = BytesIO(response.content)
        else:
            file_io = open(file_, 'rb')
    else:
        file_io = file_
        assert hasattr(file_io, 'read'), 'Non file like object was supplied'

    return file_io


def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, "http://www.example.com") is not None  # True


def get_id_list_from_ranges(id_list_str):
    id_list = []
    ranges = id_list_str.split(',')
    for number_range in ranges:
        range_with_dash = number_range.split('-')
        if len(range_with_dash) > 1:
            first_range_number = int(range_with_dash[0])
            second_range_number = int(range_with_dash[1])
            if first_range_number < second_range_number:
                id_list.extend(list(range(first_range_number, second_range_number + 1)))
            else:
                id_list.extend(list(range(second_range_number, first_range_number + 1)))
        else:
            id_list.append(number_range.strip())
    return [int(i) for i in id_list]
