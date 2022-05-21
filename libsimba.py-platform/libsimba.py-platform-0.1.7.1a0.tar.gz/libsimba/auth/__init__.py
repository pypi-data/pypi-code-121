class AuthProvider:
    @staticmethod
    def main():
        return NotImplementedError

    @staticmethod
    def login():
        return NotImplementedError

    @staticmethod
    def _is_authenticated():
        return NotImplementedError
