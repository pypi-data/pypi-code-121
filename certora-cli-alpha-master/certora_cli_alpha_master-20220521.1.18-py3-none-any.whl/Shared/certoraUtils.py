import argparse
import csv
import json
import os
import subprocess
from enum import Enum
import pkg_resources
import sys
import platform
import shlex
import shutil
import re
import queue
import math
from typing import Any, Callable, Dict, List, Optional, Set, Union, Generator
from pathlib import Path
from contextlib import contextmanager
from Shared.certoraTester import compareResultsWithExpected, get_errors, has_violations, get_violations
import logging

# logger for issues related to file system interactions
io_logger = logging.getLogger("file")
# logger for issues calling/shelling out to external functions
process_logger = logging.getLogger("rpc")
# messages from the verification results
verification_logger = logging.getLogger("verification")
# errors handling csvs (???)
csv_logger = logging.getLogger("csv")
# logger for issues regarding type checking
typecheck_logger = logging.getLogger("type_check")

LEGAL_CERTORA_KEY_LENGTHS = [32, 40]

# bash colors
BASH_ORANGE_COLOR = "\033[33m"
BASH_END_COLOR = "\033[0m"
BASH_GREEN_COLOR = "\033[32m"
BASH_RED_COLOR = "\033[31m"

VERIFICATION_ERR_MSG_PREFIX = "Prover found violations:"
VERIFICATION_SUCCESS_MSG = "No errors found by Prover!"

DEFAULT_SOLC = "solc"
DEFAULT_CLOUD_ENV = 'production'
DEFAULT_STAGING_ENV = 'master'
OPTION_OUTPUT_VERIFY = "output_verify"
ENVVAR_CERTORA = "CERTORA"
PUBLIC_KEY = "795ebbac71ae5fd6a19e7a214a524b064e33ff05"

CERTORA_CONFIG_DIR = Path(".certora_config")  # folder
CERTORA_BUILD_FILE = Path(".certora_build.json")
CERTORA_VERIFY_FILE = Path(".certora_verify.json")
PACKAGE_FILE = Path("package.json")
RECENT_JOBS_FILE = Path(".certora_recent_jobs.json")

CONTACT_CERTORA_MSG = "Encountered an error running Certora Prover; consider running the script again with " \
                      "--debug to find out why"


class SolcCompilationException(Exception):
    pass


COINBASE_FEATURES_MODE_CONFIG_FLAG = '-coinbaseFeaturesMode'

MIN_JAVA_VERSION = 11  # minimal java version to run the local type checker jar


def __colored_text(txt: str, color: str) -> str:
    return color + txt + BASH_END_COLOR


def orange_text(txt: str) -> str:
    return __colored_text(txt, BASH_ORANGE_COLOR)


def red_text(txt: str) -> str:
    return __colored_text(txt, BASH_RED_COLOR)


def green_text(txt: str) -> str:
    return __colored_text(txt, BASH_GREEN_COLOR)


def print_completion_message(txt: str, flush: bool = False) -> None:
    print(green_text(txt), flush=flush)


def is_ci_or_git_action() -> bool:
    if os.environ.get("GITHUB_ACTIONS", False) or os.environ.get("CI", False):
        return True
    return False


def remove_file(file_path: Union[str, Path]) -> None:  # TODO - accept only Path
    if isinstance(file_path, str):
        try:
            os.remove(file_path)
        except OSError:
            pass
    else:
        try:
            # When we upgrade to Python 3.8, we can use unlink(missing_ok=True) and remove the try/except clauses
            file_path.unlink()
        except FileNotFoundError:
            pass


def get_version() -> str:
    """
    @return: The version of the Certora CLI's python package in format X.Y.Z if found, an error message otherwise
    """
    # Note: the most common reason not to have an installed certora-cli package is in circleci
    try:
        version = pkg_resources.get_distribution("certora-cli").version
        return version
    except pkg_resources.DistributionNotFound:
        return "couldn't find certora-cli distributed package. Try\n pip install certora-cli"


def check_results_from_file(output_path: str, expected_filename: str) -> bool:
    with open(output_path) as output_file:
        actual = json.load(output_file)
        return check_results(actual, expected_filename)


def check_results(actual: Dict[str, Any], expected_filename: str) -> bool:
    actual_results = actual
    based_on_expected = os.path.exists(expected_filename)
    if based_on_expected:  # compare actual results with expected
        with open(expected_filename) as expectedFile:
            expected = json.load(expectedFile)
            if "rules" in actual_results and "rules" in expected:
                is_equal = compareResultsWithExpected("test", actual_results["rules"], expected["rules"], {}, {})
            elif "rules" not in actual_results and "rules" not in expected:
                is_equal = True
            else:
                is_equal = False

        if is_equal:
            print_completion_message(f"{VERIFICATION_SUCCESS_MSG} (based on {expected_filename})")
            return True
        # not is_equal:
        error_str = get_errors()
        if error_str:
            verification_logger.error(f"{VERIFICATION_ERR_MSG_PREFIX} {error_str}")
        if has_violations():
            verification_logger.error(VERIFICATION_ERR_MSG_PREFIX)
            get_violations()
        return False

    # if expected results are not defined
    # traverse results and look for violation
    errors = []
    result = True

    if "rules" not in actual_results:
        errors.append("No rules in results")
        result = False
    elif len(actual_results["rules"]) == 0:
        errors.append("No rule results found. Please make sure you wrote the rule and method names correctly.")
        result = False
    else:
        for rule in actual_results["rules"].keys():
            rule_result = actual_results["rules"][rule]
            if isinstance(rule_result, str) and rule_result != 'SUCCESS':
                errors.append("[rule] " + rule)
                result = False
            elif isinstance(rule_result, dict):
                # nested rule - ruleName: {result1: [functions list], result2: [functions list] }
                nesting = rule_result
                violating_functions = ""
                for method in nesting.keys():
                    if method != 'SUCCESS' and len(nesting[method]) > 0:
                        violating_functions += '\n  [func] ' + '\n  [func] '.join(nesting[method])
                        result = False
                if violating_functions:
                    errors.append("[rule] " + rule + ":" + violating_functions)

    if not result:
        verification_logger.error(VERIFICATION_ERR_MSG_PREFIX)
        verification_logger.error('\n'.join(errors))
        return False

    print_completion_message(VERIFICATION_SUCCESS_MSG)
    return True


def is_windows() -> bool:
    return platform.system() == 'Windows'


def replace_file_name(old_file: str, new_file_name: str) -> str:
    """
    :param old_file: the full original path
    :param new_file_name: the new base name of the file
    :return: file_with_path with the base name of the file replaced with new_file_name,
             preserving the file extension and the base path
    """
    old_file_path = Path(old_file)
    return str(old_file_path.parent / f'{new_file_name}')


def safe_create_dir(path: Path, revert: bool = True) -> None:
    if path.is_dir():
        io_logger.debug(f"directory {path} already exists")
        return
    try:
        path.mkdir()
    except OSError as e:
        msg = f"Failed to create directory {path.resolve()}"
        if revert:
            io_logger.error(msg, exc_info=e)
            raise e
        else:
            io_logger.debug(msg, exc_info=e)


def as_posix(path: str) -> str:
    """
    Converts path from windows to unix
    :param path: Path to translate
    :return: A unix path
    """
    return path.replace("\\", "/")


def abs_posix_path(path: Union[str, Path]) -> str:
    """
    Returns the absolute path, unix style
    :param path: Path to change
    :return: A posix style absolute path string
    """
    return as_posix(str(abs_posix_path_obj(path)))


def abs_posix_path_obj(path: Union[str, Path]) -> Path:
    """
    Returns the absolute path, unix style
    :param path: Path to change
    :return: A posix style absolute Path
    """
    sanitized_path = as_posix(str(path))  # Windows works with / as file separator, so we always convert
    abs_path = Path(sanitized_path).expanduser().resolve()
    return abs_path


def abs_posix_path_relative_to_root_file(rel_path: Path, root_file: Path) -> Path:
    """
     Returns the absolute path, unix style
     :param rel_path: Relative path to change.
     :param root_file: rel_path is assumed to be relative to the directory of the file root_file.
     :return: A posix style absolute path
    """
    root_dir = root_file.parent
    file_path = root_dir / rel_path
    return Path(abs_posix_path(file_path))


def convert_path_for_solc_import(path: Union[Path, str]) -> str:
    """
    Converts a path to a solc-compatible import.
    Solc paths only accept / as a file separator, and do not accept drives in path
    :param path: A path to convert
    :return: the converted path
    """
    unix_file_sep_path = abs_posix_path(path)
    driveless_path = re.sub("^[a-zA-Z]:", "", unix_file_sep_path)
    return driveless_path


def remove_and_recreate_dir(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    safe_create_dir(path)


def prepare_call_args(cmd: str) -> List[str]:
    split = shlex.split(cmd)
    if split[0].endswith('.py'):
        # sys.executable returns a full path to the current running python, so it's good for running our own scripts
        certora_root = get_certora_root_directory()
        args = [sys.executable] + [as_posix(os.path.join(certora_root, split[0]))] + split[1:]
    else:
        args = split
    return args


def get_certora_root_directory() -> str:
    return os.getenv(ENVVAR_CERTORA, os.getcwd())


def which(filename: str) -> Optional[str]:
    if is_windows() and not filename.endswith(".exe"):
        filename += ".exe"

    # TODO: find a better way to iterate over all directories in $Path
    for dirname in os.environ['PATH'].split(os.pathsep) + [os.getcwd()]:
        candidate = os.path.join(dirname, filename)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return filename

    return None


def read_json_file(file_name: Path) -> Dict[str, Any]:
    with file_name.open() as json_file:
        json_obj = json.load(json_file)
        return json_obj


def write_json_file(data: Union[Dict[str, Any], List[Dict[str, Any]]], file_name: Path) -> None:
    with file_name.open("w+") as json_file:
        json.dump(data, json_file, indent=4)


def output_to_csv(filename: str, fieldnames: List[str], row: Dict[str, Any]) -> bool:
    """
        Creates and appends the row to csv file

        @param filename: csv filename without the extension
        @param fieldnames: headers of the csv file
        @param row: data to append (as a row) to the csv file

        @return: true if completed successfully
    """
    try:
        csv_path = Path(f'{filename}.csv')
        if csv_path.exists():
            with csv_path.open("a") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writerow(row)
        else:
            with csv_path.open('a+') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(row)
        return True
    except ValueError as e:  # when the row contains fields not in fieldnames (file header)
        csv_logger.error("value conversion failed", exc_info=e)
        return False


class NoValEnum(Enum):
    """
    A class for an enum where the numerical value has no meaning.
    """

    def __repr__(self) -> str:
        """
        Do not print the value of this enum, it is meaningless
        """
        return f'<{self.__class__.__name__}.{self.name}>'


class Mode(NoValEnum):
    """
    Mode of operation - the modes are mutually exclusive:

    1. CLI parameters consist of a single .tac file.
        We check the verification condition given by that file.
    2. CLI parameters consist of a single .conf file.
        A .conf file is created on each tool run inside the .certora_config directory. It contains the command line
        options that were used for the run (in a parsed format).
        We take the options given from that file as a basis for this run; additionally given command line options
        override options given in the .conf file.
    3. CLI parameters consist of one or more Solidity (.sol) files and the `--assert` option is set.
        We create and check verification conditions based on the `assert` statements in the given solidity contracts.
    4. CLI parameters consist of one or more Solidity (.sol) files and the `--verify` option is set (the option takes
        an additional .spec/.cvl file).
        We use the given .spec/.cvl file to create and check verification conditions for the given solidity contracts.
    5. CLI parameters consist of a single .json file.
        The .json file must be in the format created e.g. by SmtTimeoutReporting.kt. This mode will take the
        .certoraBuild, .certoraVerify, and .certora_config, contents, as well as the configuration information (command
        line arguments) that are stored inside the json and start a CVT run using those files/parameters.
    6. CLI parameters consist of 0 files but all are provided in --bytecode.
        The bytecode files are in JSON, and adhere to a format given by blockchain scrapers.
        --bytecode_spec must be specified as well if this mode is used.
        The spec will be checked against the first bytecode provided, with the other bytecodes serving as auxiliary.
    """
    TAC = "a single .tac file"
    CONF = "a single .conf file"
    VERIFY = "using --verify"
    ASSERT = "using --assert"
    REPLAY = "a single .json file"
    BYTECODE = "using --bytecode"


def mode_has_spec_file(mode: Mode) -> bool:
    return mode not in [Mode.ASSERT, Mode.TAC]


def is_hex_or_dec(s: str) -> bool:
    """
    @param s: A string
    @return: True if it is a decimal or hexadecimal number
    """
    try:
        int(s, 16)
        return True
    except ValueError:
        return False


def is_hex(number: str) -> bool:
    """
    @param number: A string
    @return: True if the number is a hexadecimal number:
        - Starts with 0
        - Second character is either x or X
        - All other characters are digits 0-9, or letters a-f or A-F
    """
    match = re.search(r'^0[xX][0-9a-fA-F]+$', number)
    return match is not None


def hex_str_to_cvt_compatible(s: str) -> str:
    """
    @param s: A string representing a number in base 16 with '0x' prefix
    @return: A string representing the number in base 16 but without the '0x' prefix
    """
    assert is_hex(s)
    return re.sub(r'^0[xX]', '', s)


def decimal_str_to_cvt_compatible(s: str) -> str:
    """
    @param s: A string representing a number in base 10
    @return: A string representing the hexadecimal representation of the number, without the '0x' prefix
    """
    assert s.isnumeric()
    return re.sub(r'^0[xX]', '', hex(int(s)))


def is_debugging() -> bool:
    return logging.root.getEffectiveLevel() == logging.DEBUG


def split_by_commas_ignore_parenthesis(s: str) -> List[str]:
    """
    Split `s` by top-level commas only. Commas within parentheses are ignored. Handles nested parentheses.

    s = "-b=2, -assumeUnwindCond, -rule=bounded_supply, -m=withdrawCollateral(uint256, (bool, bool)), -regressionTest"

    will return:
    ['-b=2',
    '-assumeUnwindCond',
    '-rule=bounded_supply',
    '-m=withdrawCollateral(uint256, (bool, bool))',
    '-regressionTest']

    @param s a string
    @returns a list of strings
    """

    # Parse the string tracking whether the current character is within parentheses.
    balance = 0
    parts = []
    part = ''

    for c in s:
        part += c
        if c == '(':
            balance += 1
        elif c == ')':
            balance -= 1
            if balance < 0:
                raise argparse.ArgumentTypeError(f"Imbalanced parenthesis in --settings str: {s}")
        elif c == ',' and balance == 0:
            parts.append(part[:-1].strip())
            part = ''

    # Capture last part
    if len(part):
        parts.append(part.strip())

    return parts


def string_distance_function(input_str: str, dictionary_str: str) -> float:
    """
    Calculates a modified levenshtein distance between two strings. The distance function is modified to penalize less
    for more common user mistakes.
    Each subtraction, insertion or replacement of a character adds 1 to the distance of the two strings, unless:
    1. The input string is a prefix of the dictionary string or vice versa - the distance is 0.1 per extra letter.
    2. The replacement is between two equal letter except casing - adds nothing to the distance
    3. The subtraction/addition is of an underscore, adds 0.1 to the distance
    4. Repeated characters cost nothing, e.g. 'balloon', 'baloon' and 'balllllloooonn' have distance 0 from each other

    :param input_str: the string the user gave as input, error-prone
    :param dictionary_str: a legal string we compare the wrong input to
    :return a distance measure between the two string. A low number indicates a high probably the user to give the
            dictionary string as input
    """
    # treat special cases first:

    input_str = input_str.lower()
    dictionary_str = dictionary_str.lower()

    if input_str == dictionary_str:
        return 0
    if dictionary_str.startswith(input_str) or input_str.startswith(dictionary_str):
        diff = abs(len(input_str) - len(dictionary_str))
        return 0.1 * diff

    '''
    We are calculating the Levenshtein distance with a dynamic programming algorithm based on
    https://en.wikipedia.org/wiki/Levenshtein_distance

    Each matrix value distance_matrix[row][col] we calculate represent the distance between the two prefix substrings
    input_str[0..row-1] and dictionary_str[0..col-1]

    NOTE: our implementation differs from the classic implementation in that the cost of deletions/insertions is not
    constant
    '''

    # Initialize matrix of zeros
    rows = len(input_str) + 1
    cols = len(dictionary_str) + 1

    distance_matrix = []
    for row in range(rows):
        column = []
        for j in range(cols):
            column.append(0.0)
        distance_matrix.append(column)

    # Populate matrix of zeros with the indices of each character of both strings
    for i in range(1, rows):
        distance_matrix[i][0] = i
    for k in range(1, cols):
        distance_matrix[0][k] = k

    # Calculate modified Levenshtein distance
    for col in range(1, cols):
        for row in range(1, rows):
            if input_str[row - 1] == dictionary_str[col - 1]:
                # No cost if the characters are the same up to casing in the two strings
                cost: float = 0
            elif input_str[row - 1] == '_' or dictionary_str[col - 1] == '_':
                # common mistake
                cost = 0.1
            else:
                # full cost
                cost = 1
            distance_matrix[row][col] = min(distance_matrix[row - 1][col] + cost,         # Cost of deletions
                                            distance_matrix[row][col - 1] + cost,         # Cost of insertions
                                            distance_matrix[row - 1][col - 1] + cost)     # Cost of substitutions

    return distance_matrix[rows - 1][cols - 1]


def get_closest_strings(input_word: str, word_dictionary: List[str],
                        distance: Callable[[str, str], float] = string_distance_function,
                        max_dist: float = 4, max_dist_ratio: float = 0.5, max_suggestions: int = 2,
                        max_delta: float = 0.2) -> List[str]:
    """
    Gets an input word, which doesn't belong to a dictionary of predefined words, and returns a list of the closest
    words from the dictionary, with respect to a distance function.

    :param input_word: The word we look for closest matches of.
    :param word_dictionary: A collection of words to suggest matches from.
    :param distance: The distance function we use to measure proximity of words.
    :param max_dist: The maximal distance between words, over which no suggestions will be made.
    :param max_dist_ratio: A maximal ratio between the distance and the input word's length. No suggestions will be made
                           over this ratio.
    :param max_suggestions: The maximal number of suggestions to return.
    :param max_delta: We stop giving suggestions if the next best suggestion is worse than the one before it by more
                      than the maximal delta.
    :return: A list of suggested words, ordered from the best match to the worst.
    """
    distance_queue: queue.PriorityQueue = queue.PriorityQueue()  # Ordered in a distance ascending order

    for candidate_word in word_dictionary:
        dist = distance(input_word, candidate_word)
        distance_queue.put((dist, candidate_word))

    all_suggestions: List[str] = []
    last_dist = None

    while not distance_queue.empty() and len(all_suggestions) <= max_suggestions:
        suggested_dist, suggested_rule = distance_queue.get()
        if suggested_dist > max_dist or suggested_dist / len(input_word) > max_dist_ratio:
            break  # The distances are monotonically increasing
        if (last_dist is None) or (suggested_dist - last_dist <= max_delta):
            all_suggestions.append(suggested_rule)
            last_dist = suggested_dist

    return all_suggestions


def get_readable_time(milliseconds: int) -> str:
    # calculate (and subtract) whole hours
    milliseconds_in_hour = 3600000  # 1000 * 60 * 60
    hours = math.floor(milliseconds / milliseconds_in_hour)
    milliseconds -= hours * milliseconds_in_hour

    # calculate (and subtract) whole minutes
    milliseconds_in_minute = 60000  # 1000 * 60
    minutes = math.floor(milliseconds / milliseconds_in_minute)
    milliseconds -= minutes * milliseconds_in_minute

    # seconds
    seconds = math.floor(milliseconds / 1000)

    milliseconds -= seconds * 1000
    duration = ""

    if hours > 0:
        duration += f"{hours}h "
    duration += f"{minutes}m {seconds}s {milliseconds}ms"
    return duration


def flush_stdout() -> None:
    print("", flush=True)


def flatten_nested_list(nested_list: List[list]) -> list:
    """
    @param nested_list: A list of lists: [[a], [b, c], []]
    @return: a flat list, in our example [a, b, c]. If None was entered, returns None
    """
    return [item for sublist in nested_list for item in sublist]


def flatten_set_list(set_list: List[Set[Any]]) -> List[Any]:
    """
    Gets a list of sets, returns a list that contains all members of all sets without duplicates
    :param set_list: A list containing sets of elements
    :return: A list containing all members of all sets. There are no guarantees on the order of elements.
    """
    ret_set = set()
    for _set in set_list:
        for member in _set:
            ret_set.add(member)
    return list(ret_set)


def run_local_spec_check(with_typechecking: bool) -> int:
    """
    Runs the local type checker in one of two modes: (1) syntax only,
        and (2) including full typechecking after building the contracts
    :param with_typechecking: True if we want the full check, false for a quick CVL syntax check
    @return 0 on success or if the type checking was skipped, an error exit code otherwise
    """
    # Check if java exists on the machine
    java = which("java")
    if java is None:
        print(
            f"`java` is not installed. Installing Java version {MIN_JAVA_VERSION} or later will enable faster "
            f"CVL specification syntax checking before uploading to the cloud.")
        return 0  # if user doesn't have java installed, user will have to wait for remote type checking

    try:
        java_version_str = str(subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT))
        major_java_version = re.search(r'version \"(\d+).*', java_version_str).groups()[0]  # type: ignore
        if int(major_java_version) < MIN_JAVA_VERSION:
            print(f"Installed Java version is too old to check CVL specification files locally. Installing Java version"
                  f" {MIN_JAVA_VERSION} or later will enable faster CVL syntax checking before uploading to the cloud.")
            # if user doesn't have a valid version of java installed, user will have to wait for remote CVL syntax
            # checking
            return 0
    except (subprocess.CalledProcessError, AttributeError):
        print("Couldn't find the installed Java version. Skipping local CVL specification checking")
        # if user doesn't have a valid version of java installed, user will have to wait for remote CVL syntax
        # checking
        return 0

    # Find path to typechecker jar
    certora_root_dir = as_posix(get_certora_root_directory())
    local_certora_path = as_posix(os.path.join(certora_root_dir, "certora_jars", "Typechecker.jar"))
    installed_certora_path = \
        as_posix(os.path.join(os.path.split(__file__)[0], "../..", "certora_jars", "Typechecker.jar"))

    path_to_typechecker = local_certora_path if os.path.isfile(local_certora_path) else installed_certora_path
    # if typechecker jar does not exist, we just skip this step
    if not os.path.isfile(path_to_typechecker):
        typecheck_logger.error(f"Could not run type checker locally: file not found {path_to_typechecker}")
        return 0

    # args to typechecker
    if with_typechecking:
        typecheck_cmd = f"java -jar {path_to_typechecker} {CERTORA_BUILD_FILE} {CERTORA_VERIFY_FILE}"
    else:
        typecheck_cmd = f"java -jar {path_to_typechecker} {CERTORA_VERIFY_FILE}"

    # run it - exit with code 1 if failed
    exit_code = run_cmd(typecheck_cmd, False, custom_error_message="Failed to compile spec file",
                        logger_topic="type_check")
    return exit_code


def run_cmd(cmd: str, override_exit_code: bool, custom_error_message: Optional[str] = None,
            logger_topic: Optional[str] = "run") -> int:
    """
    @return: 0 on success, an error exit code otherwise
    """
    logger = logging.getLogger(logger_topic)
    try:
        args = prepare_call_args(cmd)
        run_result = subprocess.run(args, shell=False, universal_newlines=True, stderr=subprocess.PIPE)
        return_code = run_result.returncode
        if return_code:
            default_msg = f"Execution of command \"{' '.join(args)}\" terminated with exitcode {return_code}."
            err_msg_header = custom_error_message if custom_error_message is not None else default_msg
            print(err_msg_header, flush=True)

            # We log all lines in stderr, as they contain useful information we do not want the Python loggers to miss
            log_level = logging.INFO if override_exit_code else logging.CRITICAL
            stderr_lines = run_result.stderr.splitlines()
            for line in stderr_lines:
                logger.log(log_level, line)

            if not override_exit_code:  # else, we return 0
                return 1

        return 0
    except Exception as e:
        logger.error(e)
        return 1


@contextmanager
def change_working_directory(path: Union[str, os.PathLike]) -> Generator[None, None, None]:
    """
    Changes working directory and returns to previous on exit.
    Note: the directory will return to the previous even if an exception is thrown, for example: if path does not exist
    """
    prev_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


class Singleton(type):
    """
    This is intended to be used as a metaclass to enforce only a single instance of a class can be created
    """
    _instances: Dict[Any, Any] = {}  # Mapping from a class type to its instance

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """
        returns the instance of a class if exists, otherwise constructs it
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
