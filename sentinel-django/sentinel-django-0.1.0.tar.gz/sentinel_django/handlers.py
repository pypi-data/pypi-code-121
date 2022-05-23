from django.views.debug import ExceptionReporter


class SentinelExceptionHandler(ExceptionReporter):
    def get_traceback_data(self):
        data = super(SentinelExceptionHandler, self).get_traceback_data()
        print(data)
        return data
