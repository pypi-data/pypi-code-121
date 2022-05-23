__all__ = 'CompileError'


class CompileError(Exception):

    def __init__(self, message):
        first_index = str(message).find('"') + 1
        last_index = str(message).rfind('"')

        self.message = str(message)[
            first_index:last_index].strip()
        super().__init__(self.message)
