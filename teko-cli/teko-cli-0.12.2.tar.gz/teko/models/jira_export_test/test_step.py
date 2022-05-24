class TestStep:
    __test__ = False

    def __init__(self, description, expected_result, test_data):
        self.description = description
        self.expected_result = expected_result
        self.test_data = test_data

    def to_dict(self):
        return {
            'description': self.description,
            'expectedResult': self.expected_result,
            'testData': self.test_data
        }
