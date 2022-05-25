class Handler:

    @staticmethod
    def error_information(db, exectype, value, tb):
        print(
            'database Connection',
            db)
        print(
            'My Error Information')
        print(
            'Type:', type(exectype).__name__)
        print(
            'Value:', value)
        print(
            'Traceback:', tb.format_exc().split('\n'))