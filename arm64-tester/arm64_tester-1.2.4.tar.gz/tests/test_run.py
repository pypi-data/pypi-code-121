from unittest import TestCase

from arm64_tester import Test


class TestRun(TestCase):
    def test_run(self):
        submission_path = "./tests/resources/submission.zip"
        subroutine_path = "./tests/resources/subroutines.yaml"
        tests_path = "./tests/resources/tests.yaml"

        test = Test(submission_path, subroutine_path, tests_path)

        result = test.run()

        print(result)
