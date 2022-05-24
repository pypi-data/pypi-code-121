class TestCycle:
    test_name: str = ''
    testrun_status: str = ''
    testrun_environment: str = ''
    testrun_comment: str = ''
    testrun_duration: str = ''
    testrun_date: str = ''

    def __init__(self, **kwargs):
        for (key, value) in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self):
        return {
            'name': self.test_name,
            'testrun_status': self.testrun_status,
            'testrun_environment': self.testrun_environment,
            'testrun_comment': self.testrun_comment,
            'testrun_duration': self.testrun_duration,
            'testrun_date': self.testrun_date
        }
