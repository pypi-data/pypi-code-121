import json
import os
import subprocess
from decimal import Decimal
from re import IGNORECASE, match, search
from shutil import rmtree as delete_dir
from zipfile import ZipFile as unzip

import unidecode

from arm64_tester.exception import *


class Tester:
    """Evaluator class that grades student's submissions based on test input/output comparison and optional code scoring"""

    def __init__(self, subroutines, test_suite, cmd_line_args=None, grading_folder=None,
                 feedback_folder=None, float_threshold=None, timeout=None, save_to_file=True):
        self.temp_grading_folder = grading_folder or cmd_line_args['gfd']
        self.feedback_folder = feedback_folder or cmd_line_args['ffd']
        self.subroutines = subroutines
        self.float_threshold = float_threshold or cmd_line_args['fpre']
        self.timeout = timeout or cmd_line_args['tout']
        self.save_to_file = save_to_file

        self.template_files = [sr.build_c_file()
                               for sr in self.subroutines.values()]

        self.test_outputs = [list(map(lambda test: test['outputs'], test_suite[name]))
                             for name in self.subroutines.keys()]
        self.test_inputs = [list(map(lambda test: test['inputs'], test_suite[name]))
                            for name in self.subroutines.keys()]
        self.test_weights = [list(map(lambda test: test['weight'], test_suite[name]))
                             for name in self.subroutines.keys()]

        if os.path.exists(self.feedback_folder):
            delete_dir(self.feedback_folder)

        if self.save_to_file:
            os.mkdir(self.feedback_folder)

    def extract_submission_files(self, student_submission):
        """Extracts all relevant subroutine files from a submission in order to be graded"""
        with unzip(student_submission, 'r') as zip_file:
            # Get a list of all subroutine file names from the zip
            files = filter(lambda x: x is not None, map(lambda y: match(
                r'(?:\w+/)*([\w\-]+\.s)', y), zip_file.namelist()))
            for file in files:
                with open('{}/{}'.format(self.temp_grading_folder, file.group(1).lower()), mode='wb') as f:
                    f.write(zip_file.read(file.group(0)))

    def get_extra_assembly_to_include(self, subroutine):
        """Obtains a list of subroutines that are used in the given one so that they can be correctly included at compilation time"""
        try:
            with open('{}/{}.s'.format(self.temp_grading_folder, subroutine.lower()), mode='rb') as f:
                calls = list(filter(lambda x: x is not None, map(lambda y: search(
                    rb'bl\s+([\w\-\_]+)', y.strip(), flags=IGNORECASE), f.readlines())))

                calls = set(map(lambda x: x.group(
                    1).lower().decode('utf-8'), calls))

                return [sr for sr in calls if os.path.exists('{}/{}.s'.format(self.temp_grading_folder, sr))]
        except FileNotFoundError:
            return []

    def cleanup_files(self, files):
        for path in files:
            file = open(path, 'r+', encoding='ISO-8859-1')
            new_content = file.read().replace('system', 'blacklisted_word')
            file.seek(0)
            file.write(new_content)
            file.truncate()
            file.close()

    def compile_and_run(self, subroutine, template_file, inp, output_file):
        """Compiles and runs, with the generated C template files, the student's submission files.
        Returns a boolean tuple with information of a successful (or not) compilation and a successful (or not) test run"""

        sr = self.subroutines[subroutine]
        sr_non_int_outputs = sr.get_nr_outputs()

        # Rearrange parameter-input pair order for format due to possible parameters that are output and, therefore, declared first
        sorted_param_list = list(zip(sr.parameters, inp))
        sorted_param_list = sorted_param_list[-sr_non_int_outputs:] + \
            sorted_param_list[:-sr_non_int_outputs]

        # Build C file from template
        open('{}.c'.format(output_file), 'w').write(
            template_file.format(*[param.get_literal_representantion(inp_literal) for param, inp_literal in sorted_param_list]))

        compilation_files = list(
            map(lambda x: "{}/{}.s".format(self.temp_grading_folder, x.lower()),
                [subroutine, *self.get_extra_assembly_to_include(subroutine)])
        )

        try:
            self.cleanup_files(compilation_files)  # temporary fix
        except Exception as e:
            pass

        # Compile student code alongside generated C file
        compilation_process = subprocess.Popen('aarch64-linux-gnu-gcc -o {} {}.c {} -static'.format(
            output_file,
            output_file,
            ' '.join(compilation_files)
        ).split(' '), stderr=subprocess.PIPE)
        compilation_process.wait()
        (_, stderr) = compilation_process.communicate()

        # Throw compilation error
        if compilation_process.returncode != 0:  # If it doesn't even compile, not worth checking any further
            raise CompileError(stderr)

        # Execute and redirect output to temporary .txt file
        real_output_file = '{}.txt'.format(output_file)
        execution_process = subprocess.Popen('timeout {} qemu-aarch64-static {}'.format(self.timeout, output_file), stdout=open(
            real_output_file, mode='w', encoding='utf-8'), stderr=subprocess.PIPE, shell=True)
        execution_process.wait()
        (_, stderr) = execution_process.communicate()

        if execution_process.returncode != 0:
            if execution_process.returncode == 124:  # Return code when timeout had to kill the process
                raise RuntimeError(
                    'Failed to run: process took longer than {}s limit'.format(self.timeout))
            else:  # Other reason, but not running properly
                first_index = str(stderr).find('"') + 1
                last_index = str(stderr).rfind('"')

                message = str(stderr)[
                    first_index:last_index].strip()

                raise RuntimeError(
                    'Failed to run: {}\n'.format(message))

    def compare_test_call_output(self, subroutine, output_file, expected_outputs, given_inputs):
        """Compares expected to real outputs, calculating student's score on it"""
        # Read real outputs
        real_outputs = list(map(lambda x: x.decode(
            'utf-8', 'backslashreplace').strip(), open('{}.txt'.format(output_file), 'rb').readlines()))

        # Should return outputs and result (expected if necessary)

        converted_output = self.subroutines[subroutine].convert_outputs(
            real_outputs)

        # Actual comparison
        if not self.subroutines[subroutine].compare_outputs(expected_outputs, real_outputs, self.float_threshold):
            return (False, {
                'output': list(map(lambda x: repr(x).replace("'", ""), real_outputs)),
                'expected': expected_outputs,
                'passed': False
            })

        return (True, {
            'output': list(map(lambda x: repr(x).replace("'", ""), real_outputs)),
            'passed': True
        })

    def grade_submission(self, student_submission):
        """Grades a student's submission by comparing each real output to expected output, writing feedback in failing cases if applicable and final grade to grades csv"""
        # Reset temporary grading folder if for some reason it already exists
        if os.path.exists(self.temp_grading_folder):
            delete_dir(self.temp_grading_folder)
        os.mkdir(self.temp_grading_folder)

        # Extract all assembly files to grading directory
        self.extract_submission_files(student_submission)

        filename = match(
            r'(?:.+\/)*(.*)?.*\.zip', student_submission, flags=IGNORECASE).group(1)

        if self.save_to_file:
            feedback_file = open(
                '{}/{}.json'.format(self.feedback_folder, filename), 'w')

        subroutine_list = []

        for subroutine, template_file, inputs, outputs, weights in zip(self.subroutines.keys(), self.template_files, self.test_inputs, self.test_outputs, self.test_weights):
            # Subroutine output file template
            output_file = '{}/{}'.format(self.temp_grading_folder,
                                         subroutine.lower())

            passed = 0

            # Creating subroutine object
            subroutine_object = {
                'name': subroutine
            }

            compiled = True
            compile_output = None

            all_tests_passed = True

            tests_list = []

            score = 0

            for inp, out, weight in zip(inputs, outputs, weights):
                # Try to compile and run submission for a specific input case
                # If it fails, grade with zero and move to next subroutine

                test_object = {}

                test_object['weight'] = weight

                try:
                    self.compile_and_run(
                        subroutine, template_file, inp, output_file)
                except CompileError as compile_error:
                    compile_output = str(compile_error)
                    compiled = False
                    break

                except RuntimeError as runtime_error:
                    all_tests_passed = False

                    test_object['run'] = False
                    test_object['error'] = str(runtime_error)
                    test_object['input'] = inp

                    tests_list.append(test_object)
                    continue

                test_object['run'] = True

                (test_passed, test_compare_object) = self.compare_test_call_output(
                    subroutine, output_file, out, inp)

                if test_passed:
                    passed = passed + 1

                    score = score + int(Decimal(weight) * 1000000)
                else:
                    all_tests_passed = False

                test_object['input'] = inp
                test_object.update(test_compare_object)
                tests_list.append(test_object)

            subroutine_object['compiled'] = compiled

            if not compiled:
                subroutine_object['compile_output'] = compile_output

            subroutine_object['ok'] = compiled and all_tests_passed
            subroutine_object['passed_count'] = passed
            subroutine_object['test_count'] = len(outputs)
            subroutine_object['score'] = float(Decimal(score) / 1000000)
            subroutine_object['tests'] = tests_list

            subroutine_list.append(subroutine_object)

        if self.save_to_file:
            json.dump({'submission_name': filename,
                       'subroutines': subroutine_list}, feedback_file, indent=4)
        # Remove temporary auxiliary folder and write final scores
        # delete_dir(self.temp_grading_folder)

        return subroutine_list
