from django.views.debug import ExceptionReporter


class SentinelExceptionReporter(ExceptionReporter):
    def get_traceback_data(self):
        data = super(SentinelExceptionReporter, self).get_traceback_data()
        print(data)
        return data
