from datetime import datetime
from re import IGNORECASE, match

from yaml import YAMLError, safe_load

from arm64_tester.exception import ToolFileError
from arm64_tester.subroutines import ArraySubroutine as Array
from arm64_tester.subroutines import MixedSubroutine as Mixed
from arm64_tester.subroutines import NumericSubroutine as Numeric
from arm64_tester.subroutines import VoidSubroutine as Void
from arm64_tester.tester import Tester


class Test:

    def __init__(self, submission_file, subroutine_file, tests_file,
                 timeout=1.0, float_threshold=1e-6, save_to_file=False):
        self.submission_file = submission_file
        self.subroutine_file = subroutine_file
        self.tests_file = tests_file
        self.timeout = timeout
        self.float_threshold = float_threshold
        self.save_to_file = save_to_file

        self.__read_files()
        self.__build_test_cases()

    def __read_files(self):
        try:
            self.subroutines = safe_load(open(self.subroutine_file))
            self.test_suite = safe_load(open(self.tests_file))
        except IOError as err:
            raise ToolFileError(
                'Could not open: {}, please specify a valid file'.format(str(err)))
        except YAMLError as err:
            raise ToolFileError(
                'Error parsing YAML files: ({}), please correct syntax'.format(str(err)))

    def __build_subroutine(self, name, definition):
        map_to_truth_value = ['array' in ret or ret ==
                              'string' for ret in definition['return']]
        if not len(map_to_truth_value):  # No returns - void subroutine
            return Void(name, definition['params'])
        elif all(map_to_truth_value):  # Only arrays and/or strings as return values
            return Array(name, definition['params'], definition['return'])
        elif not any(map_to_truth_value):  # Numeric output
            return Numeric(name, definition['params'], definition['return'][0])
        else:  # Mixed return
            return Mixed(name, definition['params'], definition['return'][0], definition['return'][1:])

    def __build_test_cases(self):
        self.subroutine_objects = {name: self.__build_subroutine(
            name, definition) for name, definition in self.subroutines.items()}

    def run(self):
        folder_prefix = str(datetime.now().microsecond)

        grading_folder = f'tmp_{folder_prefix}_grading'
        feedback_folder = f'tmp_{folder_prefix}_feedback'

        tester = Tester(self.subroutine_objects, self.test_suite, grading_folder=grading_folder,
                        feedback_folder=feedback_folder, float_threshold=self.float_threshold,
                        timeout=self.timeout, save_to_file=self.save_to_file)

        submission = tester.grade_submission(self.submission_file)

        filename = match(
            r'(?:.+\/)*(.*)?.*\.zip', self.submission_file, flags=IGNORECASE).group(1)

        """ subroutines_result = [{
            'name': subroutine['name'],
            'score': subroutine['score']
        } for subroutine in submission] """

        return {
            'submission_name': filename,
            'subroutines': submission,
        }
