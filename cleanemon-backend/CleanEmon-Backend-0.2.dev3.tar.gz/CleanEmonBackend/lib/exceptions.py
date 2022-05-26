class BadDateError(ValueError):
    def __init__(self, bad_date: str):
        self.bad_date = bad_date


class BadDateRangeError(ValueError):
    def __init__(self, bad_from_date: str, bad_to_date):
        self.bad_from_date = bad_from_date
        self.bad_to_date = bad_to_date
