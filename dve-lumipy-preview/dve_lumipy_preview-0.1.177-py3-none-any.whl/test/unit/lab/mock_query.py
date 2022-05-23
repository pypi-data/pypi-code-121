import time
import pandas as pd
import uuid


class MockQuery:

    def __init__(self, x):
        self.x = x
        self.call_count = 0

    def go_async(self):
        self.call_count += 1
        return MockQueryJob(self)

    def result(self, quiet=False):
        rows = [{'A': i, 'B': i**2, 'C': i**0.5} for i in range(self.x)]
        if self.x < 1:
            raise ValueError("This is a test error")

        return pd.DataFrame(rows)

    def get_sql(self):
        return f"select * from mock.provider limit {self.x}"

    @staticmethod
    def build(x):
        return MockQuery(x)


class MockQueryJob:

    def __init__(self, mock_query: MockQuery):
        self.mock_query = mock_query
        self.ex_id = str(uuid.uuid4())

    def interactive_monitor(self, quiet=False, wait=0.1, should_stop=None):
        time.sleep(1)

    def get_result(self, quiet=False):
        return self.mock_query.result()
