from vripper.parser import get_parser_object


class VImage:
    def __init__(self, index_in_post, url, thumb_url=None):
        self.filename = str(index_in_post).zfill(4) + ".jpg"
        self.main_url = url
        self.thumb_url = thumb_url
        self.local_path = None  # Will update after a successful download.
        self.is_available = True  # Will change to False as needed.
        self.parser_object = get_parser_object(self.main_url.lower())

    def get_underlying_url(self, timeout):
        if self.parser_object is None:
            return self.main_url
        return self.parser_object.parser_function(self.main_url, timeout)
