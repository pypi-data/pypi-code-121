import re

filename_pattern = re.compile(r'(\/.*?\.[\w:]+)')
url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
email_pattern = re.compile(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$')
file_extension_pattern = re.compile(r'\.(?P<ext>[a-zA-Z0-9]+$)')


def is_url(string):
    return url_pattern.match(string) is not None


def is_email(string):
    return email_pattern.match(string) is not None


def is_filename(string):
    return filename_pattern.match(string) is not None


def find_all_filename(string):
    return re.findall(filename_pattern, string)


def get_file_extension(string):
    return re.search(file_extension_pattern, string).group('ext')
