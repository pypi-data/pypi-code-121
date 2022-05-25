import unittest
from connector import Execute

exec = Execute(hostname='localhost', command="echo test command").local_execution()

class TestExecution(unittest.TestCase):
    def test_echo_command(self):
        self.assertEqual(exec.output.strip(), 'test command')

    def test_return_code_are_0(self):
        self.assertEqual(exec.return_code, 0)

    def test_return_status_as_true(self):
        self.assertTrue(exec.status)

if __name__ == "__main__":
    TestExecution.main()
    print("All tests passed OK.")