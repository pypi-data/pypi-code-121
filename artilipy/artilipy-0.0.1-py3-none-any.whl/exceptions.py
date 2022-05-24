class dictQueryIncomplete(Exception):
    def __init__(self):
        super().__init__("Dictionary query is missing `query` parameter")

class dictNotFound(Exception):
    def __init__(self):
        super().__init__("Dictionary search query has returned nothing")

class dictLangParameterIncorrect(Exception):
    def __init__(self):
        super().__init__("Language parameter accepts only 'eng' or 'ru'. If you wish to participate in "
                         "expanding localisation settings, you can apply for a position on our team: "
                         "https://forms.gle/EKicJADB2L1nxG829")

class langIsNotCached(Exception):
    def __init__(self):
        super().__init__("Cache doesn't contain specified language")

class errorResponse(Exception):
    def __init__(self, error_message):
        super().__init__(f"API returned error response: {error_message}")

class langNotSpecified(Exception):
    def __init__(self, error_message):
        super().__init__(f"Specify 'lang' parameter: 'ru' or 'eng'")

class incorrectParams(Exception):
    def __init__(self, error_message):
        super().__init__(f"One or more parameters are not specified correctly. "
                         f"This error has most likely appeared because of passing "
                         f"not string to 'lang' parameter")
