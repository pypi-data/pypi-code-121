#!/usr/bin/env python3

import os
import sys
import time
import logging
import argparse
import re
import ast
from typing import Dict, List, Optional, Tuple, Any, Set, NoReturn
import json
import shutil
import itertools
from pathlib import Path
from copy import deepcopy

scripts_dir_path = Path(__file__).parent.resolve()  # containing directory
sys.path.insert(0, str(scripts_dir_path))
from EVMVerifier.certoraDualArg import check_arg_and_setting_consistency
from Shared.certoraUtils import get_certora_root_directory, COINBASE_FEATURES_MODE_CONFIG_FLAG, run_cmd
from Shared.certoraUtils import DEFAULT_SOLC, DEFAULT_CLOUD_ENV, DEFAULT_STAGING_ENV, CONTACT_CERTORA_MSG
from Shared.certoraUtils import as_posix, abs_posix_path_obj, split_by_commas_ignore_parenthesis, run_local_spec_check
from Shared.certoraUtils import check_results_from_file, is_ci_or_git_action
from Shared.certoraUtils import is_windows, get_closest_strings, remove_file
from Shared.certoraUtils import CERTORA_BUILD_FILE, CERTORA_VERIFY_FILE, LEGAL_CERTORA_KEY_LENGTHS, PACKAGE_FILE
from Shared.certoraUtils import CERTORA_CONFIG_DIR, PUBLIC_KEY
from Shared.certoraUtils import Mode, get_version
from Shared.certoraUtils import print_completion_message
from Shared.certoraUtils import flatten_nested_list
from Shared.certoraUtils import mode_has_spec_file, abs_posix_path
from EVMVerifier.certoraConfigIO import read_from_conf, read_from_conf_file, current_conf_to_file
from EVMVerifier.certoraCloudIO import CloudVerification, validate_version
from EVMVerifier.certoraCollectRunMetadata import collect_run_metadata, CERTORA_METADATA_FILE
from Shared.certoraLogging import setup_log_arguments

BUILD_SCRIPT_PATH = Path("EVMVerifier/certoraBuild.py")

# logger for issues regarding the general run flow.
# Also serves as the default logger for errors originating from unexpected places.
run_logger = logging.getLogger("run")

# logger for issues regarding argument parsing and user input validation
arg_logger = logging.getLogger("arguments")


def print_version() -> None:
    print("certora-cli", get_version())


def get_local_run_cmd(args: argparse.Namespace) -> str:
    """
    Assembles a jar command for local run
    @param args: A namespace including all command line input arguments
    @return: A command for running the prover locally
    """
    run_args = []
    if args.mode == Mode.TAC:
        run_args.append(args.files[0])
    if args.cache is not None:
        run_args.extend(['-cache', args.cache])
    if args.tool_output is not None:
        run_args.extend(['-json', args.tool_output])
    if args.settings is not None:
        for setting in args.settings:
            run_args.extend(setting.split('='))
    if args.coinbaseMode:
        run_args.append(COINBASE_FEATURES_MODE_CONFIG_FLAG)

    if args.jar is not None:
        jar_path = args.jar
    else:
        certora_root_dir = as_posix(get_certora_root_directory())
        jar_path = f"{certora_root_dir}/emv.jar"

    if args.java_args is not None:
        return " ".join(["java", args.java_args, "-jar", jar_path] + run_args)
    return " ".join(["java", "-jar", jar_path] + run_args)


def run_certora(args: List[str], is_library: bool = False) -> None:
    """
    The main function that is responsible for the general flow of the script.
    The general flow is:
    1. Parse program arguments
    2. Run the necessary steps (type checking/ build/ cloud verification/ local verification)
    3. Shut down

    IMPORTANT - we assume the scripts always reaches the shut down code. DO NOT SYS.EXIT() IN THE SCRIPT FILES!

    The program terminates with an exit code of 0 in case of success and 1 otherwise
    """

    # If we are not in debug mode, we do not want to print the traceback in case of exceptions.
    if '--debug' not in args:  # We check manually, because we want no traceback in argument parsing exceptions
        sys.tracebacklimit = 0

    parsed_args, conf_dict = get_args(args)  # Parse arguments
    if parsed_args.short_output is False:
        if is_ci_or_git_action():
            parsed_args.short_output = True
    print_completion_message("Collecting contracts and building", True)

    timings = {}
    exit_code = 0  # The exit code of the script. 0 means success, any other number is an error.

    try:
        collect_run_metadata(wd=Path.cwd(), raw_args=sys.argv, conf_dict=conf_dict, args=parsed_args) \
            .dump()

        # When a TAC file is provided, no build arguments will be processed
        if parsed_args.mode not in [Mode.TAC, Mode.REPLAY]:
            run_logger.debug(f"There is no TAC file. Going to script {BUILD_SCRIPT_PATH} to main_with_args()")
            from EVMVerifier.certoraBuild import build
            build_start = time.perf_counter()

            # If we are not in CI, we also check the spec for Syntax errors.
            build_success = build(parsed_args, ignore_spec_syntax_check=is_library)
            if not build_success:
                exit_code = 1
            else:
                build_end = time.perf_counter()
                timings["buildTime"] = round(build_end - build_start, 4)
                print_completion_message("Collected contract bytecode and metadata", True)

        if not parsed_args.build_only and exit_code == 0:  # either we skipped building (TAC MODE) or build succeeded
            if parsed_args.local:
                check_cmd = get_local_run_cmd(parsed_args)

                compare_with_tool_output = parsed_args.tool_output is not None
                if compare_with_tool_output:
                    # Remove actual before starting the current test
                    remove_file(parsed_args.tool_output)

                # In local mode, this is reserved for Certora devs, so let the script print it
                print(f"Verifier run command:\n {check_cmd}", flush=True)
                run_result = run_cmd(check_cmd, compare_with_tool_output, logger_topic="verification")
                if run_result != 0:
                    exit_code = 1
                else:
                    print_completion_message("Finished running verifier:")
                    print(f"\t{check_cmd}")

                    if compare_with_tool_output:
                        print("Comparing tool output to the expected output:")
                        result = check_results_from_file(parsed_args.tool_output, parsed_args.expected_file)
                        if not result:
                            exit_code = 1

            else:  # Remote run
                # In cloud mode, we first run a local type checker

                '''
                Before running the local type checker, we see if the current package version is compatible with
                the latest. We check it before running the local type checker, because local type checking
                errors could be simply a result of syntax introduced in the newest version.
                '''
                validate_version()  # Will raise an exception if the local version is incompatible.

                # Syntax checking and typechecking
                if mode_has_spec_file(parsed_args.mode):
                    if parsed_args.disableLocalTypeChecking:
                        run_logger.warning(
                            "Local checks of CVL specification files disabled. It is recommended to enable "
                            "the checks.")
                    else:
                        typechecking_start = time.perf_counter()
                        spec_check_failed = run_local_spec_check(with_typechecking=True)
                        if spec_check_failed:
                            exit_code = 1
                        else:
                            typechecking_end = time.perf_counter()
                            timings['typecheckingTime'] = round(typechecking_end - typechecking_start, 4)
                            print_completion_message("Local type checking finished successfully", True)

                if not parsed_args.typecheck_only and exit_code == 0:  # Local typechecking either succeeded or skipped
                    parsed_args.key = validate_certora_key()
                    cloud_verifier = CloudVerification(parsed_args, timings)

                    # Wrap strings with space with ' so it can be copied and pasted to shell
                    pretty_args = [f"'{arg}'" if ' ' in arg else arg for arg in args]
                    cl_args = ' '.join(pretty_args)

                    result = cloud_verifier.cli_verify_and_report(cl_args, parsed_args.send_only)
                    if not result:
                        exit_code = 1

    except Exception as e:
        run_logger.fatal(CONTACT_CERTORA_MSG, exc_info=e)
        run_logger.debug("Failure traceback: ", exc_info=e)
        exit_code = 1
    except KeyboardInterrupt:
        print('Interrupted by user', flush=True)

    # If the exit_code is 0, we do not call sys.exit() -> calling sys.exit() also exits any script that wraps this one
    if not is_library and exit_code != 0:
        sys.exit(exit_code)


'''
########################################################################################################################
############################################### Argument types #########################################################
########################################################################################################################
'''


def _raise_argument_type_error(msg: str) -> NoReturn:
    raise argparse.ArgumentTypeError(msg)


def type_non_negative_integer(string: str) -> str:
    """
    :param string: A string
    :return: The same string, if it represents a decimal integer
    :raises argparse.ArgumentTypeError if the string does not represent a non-negative decimal integer
    """
    if not string.isnumeric():
        _raise_argument_type_error(f'expected a non-negative integer, instead given {string}')
    return string


def type_positive_integer(string: str) -> str:
    type_non_negative_integer(string)
    if int(string) == 0:
        _raise_argument_type_error("Expected a positive number, got 0 instead")
    return string


def type_jar(filename: str) -> str:
    file_path = Path(filename)
    if not file_path.is_file():
        raise argparse.ArgumentTypeError(f"file {filename} does not exist.")
    if not os.access(filename, os.X_OK):
        raise argparse.ArgumentTypeError(f"no execute permission for jar file {filename}")

    basename = file_path.name  # extract file name from path.
    # NOTE: expects Linux file paths, all Windows file paths will fail the check below!
    if re.search(r"^[\w.-]+\.jar$", basename):
        # Base file name can contain only alphanumeric characters, underscores, or hyphens
        return filename

    raise argparse.ArgumentTypeError(f"file {filename} is not of type .jar")


def type_optional_readable_file(filename: str) -> str:
    """
    Verifies that if filename exists, it is a valid readable file.
    It is the responsibility of the consumer to check the file exists
    """
    file_path = Path(filename)
    if file_path.is_dir():
        raise argparse.ArgumentTypeError(f"{filename} is a directory and not a file")
    elif file_path.exists() and not os.access(filename, os.R_OK):
        raise argparse.ArgumentTypeError(f"no read permissions for {filename}")
    return filename  # It is okay if the file does not exist


def type_readable_file(filename: str) -> str:
    file_path = Path(filename)
    if not file_path.exists():
        raise argparse.ArgumentTypeError(f"file {filename} not found")
    if file_path.is_dir():
        raise argparse.ArgumentTypeError(f"{filename} is a directory and not a file")
    if not os.access(filename, os.R_OK):
        raise argparse.ArgumentTypeError(f"no read permissions for {filename}")
    return filename


def is_solc_file_valid(orig_filename: Optional[str]) -> str:
    """
    Verifies that a given --solc argument is valid:
        1. The file exists
        2. We have executable permissions for it
    :param orig_filename: Path to a solc executable file. If it is None, a default path is used instead,
                          which is also checked
    :return: Default solc executable if orig_filename was None, orig_filename is returned otherwise
    :raises argparse.ArgumentTypeException if the argument is invalid (including the default if it is used)
    """
    if orig_filename is None:
        filename = DEFAULT_SOLC
        err_prefix = f'No --solc path given, but default solidity executable {DEFAULT_SOLC} had an error. '
    else:
        filename = orig_filename
        err_prefix = ''

    if is_windows() and not filename.endswith(".exe"):
        filename += ".exe"

    common_mistakes_suffixes = ['sol', 'conf', 'tac', 'spec', 'cvl']
    for suffix in common_mistakes_suffixes:
        if filename.endswith(f".{suffix}"):
            raise argparse.ArgumentTypeError(f"wrong solidity executable given: {filename}")

    # TODO: find a better way to iterate over all directories in $PATH
    for dirname in os.environ['PATH'].split(os.pathsep) + [os.getcwd()]:
        dir_path = Path(dirname).expanduser()  # Expand ~ in unix systems
        candidate = dir_path / filename
        if candidate.exists():
            if candidate.is_file():
                if os.access(str(candidate), os.X_OK):
                    sanitized = candidate.as_posix()
                    return sanitized
                else:
                    raise argparse.ArgumentTypeError(
                        err_prefix + f"No execution permissions for Solidity executable {filename}")
            else:
                raise argparse.ArgumentTypeError(err_prefix + f"{filename} is a directory, not a file")

    raise argparse.ArgumentTypeError(err_prefix + f"Solidity executable {filename} not found in path")


def type_solc_map(args: str) -> Dict[str, str]:
    """
    Checks that the argument is of form <contract_1>=<solc_1>,<contract_2>=<solc_2>,..
    and if all solc files are valid: they were found, and we have execution permissions for them.
    We also validate that a contract doesn't have more than a single value (but that value may appear multiple times.

    :param args: argument of --solc_map
    :return: {contract: solc}.
             For example, if --solc_args a=solc4.25 is used, returned value will be:
             {'a': 'solc4.25'}
    :raises argparse.ArgumentTypeError if the format is wrong
    """
    args = args.replace(' ', '')  # remove whitespace

    '''
    Regex explanation:
    ([^=,]+=[^=,]+) describes a single key-value pair in the map. It must contain a single = sign, something before
    and something after.
    We allow more than one, as long as all but the last are followed by a comma hence ([^=,]+=[^=,]+,)*
    We allow nothing else inside the argument, so all is wrapped by ^ and $
    '''
    solc_matches = re.search(r'^([^=,]+=[^=,]+,)*([^=,]+=[^=,]+)$', args)

    if solc_matches is None:
        raise argparse.ArgumentTypeError(f"--solc_map argument {args} is of wrong format. Must be of format:"
                                         f"<contract>=<solc>[,..]")

    solc_map = {}  # type: Dict[str, str]
    solc_versions = set()  # If all --solc_args point to the same solc version, it is better to use --solc, and we warn
    all_warnings = set()

    for match in args.split(','):
        contract, solc_file = match.split('=')
        is_solc_file_valid(solc_file)  # raises an exception if file is bad
        if contract in solc_map:
            if solc_map[contract] == solc_file:
                all_warnings.add(f"solc mapping {contract}={solc_file} appears multiple times and is redundant")
            else:
                raise argparse.ArgumentTypeError(f"contradicting definition in --solc_map for contract {contract}: "
                                                 f"it was given two different Solidity compilers: {solc_map[contract]}"
                                                 f" and {solc_file}")
        else:
            solc_map[contract] = solc_file
            solc_versions.add(solc_file)

    if len(solc_versions) == 1:
        all_warnings.add(f'All contracts will be compiled with the same Solidity compiler in --solc_map. '
                         f'--solc {list(solc_versions)[0]} can be used instead')

    for warning in all_warnings:
        arg_logger.warning(warning)

    arg_logger.debug(f"solc_map = {solc_map}", True)
    return solc_map


def type_optimize_map(args: str) -> Dict[str, str]:
    """
    Checks that the argument is of form <contract_1>=<num_runs_1>,<contract_2>=<num_runs_2>,..
    and if all <num_runs> are valid positive integers.
    We also validate that a contract doesn't have more than a single value (but that value may appear multiple times.

    :param args: argument of --optimize_map
    :return: {contract: num_runs}.
             For example, if --optimize_args a=12 is used, returned value will be:
             {'a': '12'}
    :raises argparse.ArgumentTypeError if the format is wrong
    """
    args = args.replace(' ', '')  # remove whitespace

    '''
    Regex explanation:
    ([^=,]+=[^=,]+) describes a single key-value pair in the map. It must contain a single = sign, something before
    and something after
    We allow more than one, as long as all but the last are followed by a comma hence ([^=,]+=[^=,]+,)*
    We allow nothing else inside the argument, so all is wrapped by ^ and $
    '''
    optimize_matches = re.search(r'^([^=,]+=[^=,]+,)*([^=,]+=[^=,]+)$', args)

    if optimize_matches is None:
        raise argparse.ArgumentTypeError(f"--optimize_map argument {args} is of wrong format. Must be of format:"
                                         f"<contract>=<num_runs>[,..]")

    optimize_map = {}  # type: Dict[str, str]
    all_num_runs = set()  # If all --optimize_args use the same num runs, it is better to use --optimize, and we warn
    all_warnings = set()

    for match in args.split(','):
        contract, num_runs = match.split('=')
        type_positive_integer(num_runs)  # raises an exception if the number is bad
        if contract in optimize_map:
            if optimize_map[contract] == num_runs:
                all_warnings.add(f"optimization mapping {contract}={num_runs} appears multiple times and is redundant")
            else:
                raise argparse.ArgumentTypeError(f"contradicting definition in --optimize_map for contract {contract}: "
                                                 f"it was given two different numbers of runs to optimize for: "
                                                 f"{optimize_map[contract]} and {num_runs}")
        else:
            optimize_map[contract] = num_runs
            all_num_runs.add(num_runs)

    if len(all_num_runs) == 1:
        all_warnings.add(f'All contracts are optimized for the same number of runs in --optimize_map. '
                         f'--optimize {list(all_num_runs)[0]} can be used instead')

    for warning in all_warnings:
        arg_logger.warning(warning)

    arg_logger.debug(f"optimize_map = {optimize_map}", True)
    return optimize_map


def type_dir(dirname: str) -> str:
    dir_path = Path(dirname)
    if not dir_path.exists():
        raise argparse.ArgumentTypeError(f"path {dirname} does not exist")
    if dir_path.is_file():
        raise argparse.ArgumentTypeError(f"{dirname} is a file and not a directory")
    if not os.access(dirname, os.R_OK):
        raise argparse.ArgumentTypeError(f"no read permissions to {dirname}")
    return dir_path.resolve().as_posix()


def type_tool_output_path(filename: str) -> str:
    file_path = Path(filename)
    if file_path.is_dir():
        raise argparse.ArgumentTypeError(f"--toolOutput {filename} is a directory")
    if file_path.is_file():
        arg_logger.warning(f"--toolOutPut {filename} file already exists")
        if not os.access(filename, os.W_OK):
            raise argparse.ArgumentTypeError(f'No permission to rewrite --toolOutPut file {filename}')
    else:
        try:
            with file_path.open('w') as f:
                f.write('try')
            file_path.unlink()
        except (ValueError, IOError, OSError) as e:
            raise argparse.ArgumentTypeError(f"could not create --toolOutput file {filename}. Error: {e}")

    return filename


def type_list(candidate: str) -> List[str]:
    """
    Verifies the argument can be evaluated by python as a list
    """
    v = ast.literal_eval(candidate)
    if type(v) is not list:
        raise argparse.ArgumentTypeError(f"Argument \"{candidate}\" is not a list")
    return v


def type_input_file(file: str) -> str:
    # [file[:contractName] ...] or CONF_FILE.conf or TAC_FILE.tac

    if '.sol' in file:
        ext = 'sol'
    elif '.vy' in file:
        ext = 'vy'
    else:
        ext = None

    if ext is not None:
        '''
        Regex explanation (suppose ext=.sol):
        The file path must ends with suffix .sol: ".+\\.sol"
        A single contract name might appear. It cannot contain dots of colons:  "(:[^.:]+)?"
        '''
        if not re.search(r'^.+\.' + ext + r'(:[^.:]+)?$', file):
            raise argparse.ArgumentTypeError(f"Bad input file format of {file}. Expected <file_path>:<contract>")

        pos_file_path = Path(file).as_posix()

        if ':' in pos_file_path:
            # We split by the last occurrence of sol: in the path, which was guaranteed by te regex
            file_path_suffixless, contract = pos_file_path.rsplit("." + ext + ":", 1)
            if not re.search(r'^\w+$', contract):
                raise argparse.ArgumentTypeError(
                    f"A contract's name {contract} can contain only alphanumeric characters or underscores")
            file_path = file_path_suffixless + "." + ext
        else:
            file_path = file

        type_readable_file(file_path)
        base_name = Path(file_path).stem  # get Path's leaf name and remove the trailing ext
        if not re.search(r'^\w+$', base_name):
            raise argparse.ArgumentTypeError(
                f"file name {file} can contain only alphanumeric characters or underscores")
        return file

    elif file.endswith('.tac') or file.endswith('.conf') or file.endswith('.json'):
        type_readable_file(file)
        return file

    raise argparse.ArgumentTypeError(f"input file {file} is not in one of the supported types (.sol, .vy, .tac, .conf, "
                                     f".json)")


sanity_values = ['none', 'basic', 'advanced']


def type_rule_sanity_flag(sanity_flag: str) -> str:
    if sanity_flag in sanity_values:
        return sanity_flag
    else:
        _raise_argument_type_error(
            f'Illegal value for --rule_sanity, choose one of the following values: {sanity_values}')


def type_json_file(file: str) -> str:
    if not file.endswith('.json'):
        raise argparse.ArgumentTypeError(f"Input file {file} is not of type .json")
    type_readable_file(file)
    with open(file, 'r') as f:
        json.load(f)  # if it fails, it would throw an exception
    return file


def type_verify_arg(candidate: str) -> str:
    if not re.search(r'^\w+:[^:]+\.(spec|cvl)$', candidate):
        # Regex: name has only one ':', has at least one letter before, one letter after and ends in .spec
        raise argparse.ArgumentTypeError(f"argument {candidate} for --verify option is in incorrect form. "
                                         "Must be formatted contractName:specName.spec")
    spec_file = candidate.split(':')[1]
    type_readable_file(spec_file)

    return candidate


def type_link_arg(link: str) -> str:
    if not re.search(r'^\w+:\w+=\w+$', link):
        raise argparse.ArgumentTypeError(f"Link argument {link} must be of the form contractA:slot=contractB or "
                                         f"contractA:slot=<number>")
    return link


def type_struct_link(link: str) -> str:
    search_res = re.search(r'^\w+:([^:=]+)=\w+$', link)
    # We do not require firm form of slot number so we can give more informative warnings

    if search_res is None:
        raise argparse.ArgumentTypeError(f"Struct link argument {link} must be of the form contractA:<field>=contractB")
    if search_res[1].isidentifier():
        return link
    try:
        parsed_int = int(search_res[1], 0)  # an integer or a hexadecimal
        if parsed_int < 0:
            raise argparse.ArgumentTypeError(f"struct link slot number negative at {link}")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Struct link argument {link} must be of the form contractA:number=contractB"
                                         f" or contractA:fieldName=contractB")
    return link


def type_contract(contract: str) -> str:
    if not re.match(r'^\w+$', contract):
        raise argparse.ArgumentTypeError(
            f"Contract name {contract} can include only alphanumeric characters or underscores")
    return contract


def type_package(package: str) -> str:
    if not re.search("^[^=]+=[^=]+$", package):
        raise argparse.ArgumentTypeError("a package must have the form name=path")
    path = package.split('=')[1]
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"Package path {path} does not exist")
    if not os.access(path, os.R_OK):
        raise argparse.ArgumentTypeError(f"No read permissions for for packages directory {path}")
    return package


def type_settings_arg(settings: str) -> str:
    """
    Gets a string representing flags to be passed to another tool via --settings, in the form '-a,-b=2[,..]'
    @raise argparse.ArgumentTypeError
    """
    arg_logger.debug(f"settings pre-parsing= {settings}")
    settings = settings.lstrip()

    '''
    Split by commas UNLESS the commas are inside parenthesis, for example:
    "-b=2, -assumeUnwindCond, -rule=bounded_supply, -m=withdrawCollateral(uint256, uint256), -regressionTest"

    will become:
    ['-b=2',
    '-assumeUnwindCond',
    '-rule=bounded_supply',
    '-m=withdrawCollateral(uint256, uint256)',
    '-regressionTest']
    '''
    flags = split_by_commas_ignore_parenthesis(settings)
    '''
    Regex explanation:
    We want to match a comma.
    ?! is a negative lookahead. We do not match the comma if there is any number of non-parenthesis characters
    ending in a closing parenthesis.
    We also strip all whitespaces following commas, if any.
    '''

    arg_logger.debug("settings after-split= " + str(settings))
    for flag in flags:
        arg_logger.debug(f"checking setting {flag}")

        '''
        Regex explanation:
        The setting must start with a dash.
        The setting name cannot contain dashes or equality signs: "[^-=]+"
        The setting might be set to a single non-empty value: "(=[^=]+)?"
        '''
        if not re.search(r'^-[^-=]+(=[^=]+)?$', flag):
            if flag.startswith("--"):
                raise argparse.ArgumentTypeError(f"illegal argument in --settings: {flag} starts with -- instead of -")
            raise argparse.ArgumentTypeError(f"illegal argument in --settings: {flag}")
    return settings


def type_java_arg(java_args: str) -> str:
    if not re.search(r'^"[^"]+"$', java_args):  # Starts and ends with " but has no " in between them
        raise argparse.ArgumentTypeError(f'java argument must be wrapped in "", instead found {java_args}')
    return java_args


def type_address(candidate: str) -> str:
    if not re.search(r'^[^:]+:[0-9A-Fa-fxX]+$', candidate):
        # Regex: name has a single ':', has at least one character before and one alphanumeric character after
        raise argparse.ArgumentTypeError(f"Argument {candidate} of --address option is in incorrect form. "
                                         "Must be formatted <contractName>:<non-negative number>")
    return candidate


def type_method(candidate: str) -> str:
    """
    Verifies that the given method is valid. We check for the following:
    * The format is fun_name(<primitive_types separated by commas>).
    * There are valid parenthesis
    * There are only legal characters
    * The commas appear inside the parenthesis, and separate words
    * We currently do not support complex types in methods, such as structs. We warn the user accordingly.

    This function does not check whether the primitive types exist. For example, an input foo(bar,simp) will be accepted
    even though there is no primitive type bar. This will be checked later, when we try to match the method signature
    to existing method signatures.
    :param candidate: The method input string
    :return: The same string
    :raises: ArgumentTypeError when the string is illegal (see above)
    """
    tot_opening_parenthesis_count = 0
    curr_opening_parenthesis_count = 0
    curr_str_len = 0  # length of strings that represent primitives or function names
    last_non_whitespace_char = None

    for i, char in enumerate(candidate):
        if char.isspace():
            continue
        if char == '(':
            if last_non_whitespace_char is None:
                raise argparse.ArgumentTypeError(f"malformed --method argument {candidate} - method has no name")
            elif curr_str_len == 0 and curr_opening_parenthesis_count == 0:
                raise argparse.ArgumentTypeError(
                    f"malformed --method argument {candidate} - only one pair of wrapping argument parenthesis allowed")
            tot_opening_parenthesis_count += 1
            curr_opening_parenthesis_count += 1
            curr_str_len = 0
        elif char == ')':
            curr_opening_parenthesis_count -= 1
            if curr_opening_parenthesis_count < 0:
                raise argparse.ArgumentTypeError(
                    f"malformed --method argument - too many closing parenthesis at location {i + 1} of: {candidate}")
            if last_non_whitespace_char == "," and curr_str_len == 0:
                raise argparse.ArgumentTypeError(
                    f"malformed --method argument - empty primitive type after comma at location {i + 1} of: "
                    f"{candidate}")
            if last_non_whitespace_char == "(" and curr_opening_parenthesis_count > 0:
                raise argparse.ArgumentTypeError(
                    f"malformed --method argument - empty struct at location {i - 1} of: {candidate}")
            curr_str_len = 0
        elif char == ',':
            if curr_opening_parenthesis_count == 0:
                raise argparse.ArgumentTypeError(
                    f"malformed --method argument - comma outside parenthesis at location {i + 1} of: {candidate}")
            if curr_str_len == 0 and last_non_whitespace_char != ")":
                # a comma after a struct is legal
                raise argparse.ArgumentTypeError(
                    f"malformed --method argument - empty primitive type before comma at location {i + 1} of: "
                    f"{candidate}")
            curr_str_len = 0
        elif char.isalnum() or char == '_':
            curr_str_len += 1
        elif char == "[":
            if curr_str_len < 1:
                raise argparse.ArgumentTypeError(
                    f"Bracket without a primitive type of --method argument at location {i + 1} of: {candidate}")
            if len(candidate) == i + 1 or candidate[i + 1] != "]":
                raise argparse.ArgumentTypeError(
                    f"Opening bracket not followed by a closing bracket at --method argument at location {i + 1} of: "
                    f"{candidate}")
        elif char == "]":
            if i == 0 or candidate[i - 1] != "[":
                raise argparse.ArgumentTypeError(
                    f"Closing bracket not preceded by an opening bracket at --method argument at location {i + 1} of: "
                    f"{candidate}")
        else:  # we insert spaces after commas to aid in parsing
            raise argparse.ArgumentTypeError(
                f"Unsupported character {char} in --method argument at location {i + 1} of: {candidate}")

        last_non_whitespace_char = char

    if tot_opening_parenthesis_count == 0:
        raise argparse.ArgumentTypeError(f"malformed --method argument {candidate} - no parenthesis")
    elif curr_opening_parenthesis_count > 0:
        raise argparse.ArgumentTypeError(f"malformed --method argument {candidate} - unclosed parenthesis")
    return candidate


'''
########################################################################################################################
############################################# Other functions ##########################################################
########################################################################################################################
'''


def check_files_input(file_list: List[str]) -> None:
    """
    Verifies that correct input was inserted as input to files.
    As argparser verifies the files exist and the correctness of the format, we only check if only a single operation
    mode was used.
    The allowed disjoint cases are:
    1. Use a single .conf file
    2. Use a single .tac file
    3. Use any number of [contract.sol:nickname ...] (at least one is guaranteed by argparser)
    @param file_list: A list of strings representing file paths
    @raise argparse.ArgumentTypeError if more than one of the modes above was used
    """
    num_files = len(file_list)
    if num_files > 1:  # if there is a single file, there cannot be a mix between file types
        for file in file_list:
            if '.tac' in file:
                raise argparse.ArgumentTypeError(f'When using the tool in TAC mode by providing .tac file {file}, '
                                                 f'you can only provide a single file. {num_files} files were given')
            if '.conf' in file:
                raise argparse.ArgumentTypeError(f'When using the tool in CONF mode by providing .conf file {file}, '
                                                 f'you can only provide a single file. {num_files} files were given')


def _get_trivial_contract_name(contract: str) -> str:
    """
    Gets a path to a .sol file and returns its trivial contract name. The trivial contract name is the basename of the
    path of the file, without file type suffix.
    For example: for 'file/Test/opyn/vault.sol', the trivial contract name is 'vault'.
    @param contract: A path to a .sol file
    @return: The trivial contract name of a file
    """
    return abs_posix_path_obj(contract).stem


def warn_verify_file_args(files: List[str]) -> Tuple[Set[str], Set[str], Dict[str, str], Dict[str, str]]:
    """
    Verifies all file inputs are legal. If they are not, throws an exception.
    If there are any redundancies or duplication, warns the user.
    Otherwise, it returns a set of all legal contract names.
    @param files: A list of string of form: [contract.sol[:contract_name] ...]
    @return: (contracts, files, contract_to_file, file_to_contract)
        contracts - a set of contract names
        files - a set of paths to files containing contracts
        contract_to_file - a mapping from contract name -> file containing it
        file_to_contract - a mapping from a file path -> name of the contract within it we verify
                           (we can currently only verify a single contract per file)
    """

    """
    The logic is complex, and better shown by examples.
    Legal use cases:
    1. A.sol B.sol
        ->  contracts=(A, B), files=(A.sol, B.sol), contract_to_file={'A': 'A.sol', 'B': 'B.sol'},
            file_to_contract = {'A.sol': 'A', 'B.sol': 'B'}
    2. A.sol:a B.sol:b C.sol
        ->  contracts=(a, b, C), files=(A.sol, B.sol, C.sol),
            contract_to_file={'a': 'A.sol', 'b': 'B.sol', 'C': 'C.sol'},
            file_to_contract = {'A.sol': 'a', 'B.sol': 'b', 'C.sol': 'C'}
    3. A.sol:B B.sol:c
        ->  contracts=(B, c), files=(A.sol, B.sol),
            contract_to_file={'B': 'A.sol', 'c': 'B.sol'},
            file_to_contract = {'A.sol': 'B', 'B.sol': 'c'}

    Warning cases:
    4. A.sol A.sol
        -> A.sol is redundant
    5. A.sol:a A.sol:a
        -> A.sol:a is redundant
    6. A.sol:A
        -> contract name A is redundant (it's the default name)

    Illegal cases:
    7. A.sol:a A.sol:b
        -> The same file cannot contain two different contracts
    8. A.sol:a B.sol:a
        -> The same contract name cannot be used twice
    9. ../A.sol A.sol
        -> The same contract name cannot be used twice
    10. A.sol:B B.sol
        -> The same contract name cannot be used twice
    11. A.sol:a A.sol
        -> The same file cannot contain two different contracts
    12. A.sol A.sol:a
        -> The same file cannot contain two different contracts

    Warning are printed only if the input is legal
    @raise argparse.ArgumentTypeError in an illegal case (see above)
    """
    if len(files) == 1 and (files[0].endswith(".conf") or files[0].endswith(".tac")):
        return set(), set(), dict(), dict()  # No legal contract names

    declared_contracts = set()
    file_paths = set()
    all_warnings = set()

    contract_to_file: Dict[str, str] = dict()
    file_to_contract: Dict[str, str] = dict()

    for f in files:

        default_contract_name = _get_trivial_contract_name(f)
        posix_path = os.path.relpath(abs_posix_path_obj(f), Path.cwd())
        assert posix_path.count(':') < 2
        if ':' in posix_path:
            filepath_str, contract_name = posix_path.split(":")
            if contract_name == default_contract_name:
                all_warnings.add(f"contract name {contract_name} is the same as the file name and can be omitted "
                                 f"from {filepath_str}:{contract_name}")
        else:
            filepath_str = posix_path
            contract_name = default_contract_name

        if filepath_str in file_to_contract:
            if contract_name != file_to_contract[filepath_str]:
                raise argparse.ArgumentTypeError(f"file {filepath_str} was given two different contract names: "
                                                 f"{file_to_contract[filepath_str]} and {contract_name}")
            else:
                all_warnings.add(f"file argument {f} appears more than once and is redundant")

        if contract_name in contract_to_file and contract_to_file[contract_name] != filepath_str:
            # A.sol:a B.sol:a
            raise argparse.ArgumentTypeError(f"A contract named {contract_name} was declared twice for files "
                                             f"{contract_to_file[contract_name]}, {filepath_str}")

        contract_to_file[contract_name] = filepath_str
        file_to_contract[filepath_str] = contract_name
        declared_contracts.add(contract_name)
        file_paths.add(filepath_str)

    for warning in all_warnings:
        arg_logger.warning(warning)

    return declared_contracts, file_paths, contract_to_file, file_to_contract


def check_conflicting_link_args(args: argparse.Namespace) -> None:
    """
    Detects contradicting definitions of slots in link and throws.
    DOES NOT check for file existence, format legality, or anything else.
    We assume the links contain no duplications.
    @param args: A namespace, where args.link includes a list of strings that are the link arguments
    @raise argparse.ArgumentTypeError if a slot was given two different definitions
    """
    pair_list = itertools.permutations(args.link, 2)
    for pair in pair_list:
        link_a = pair[0]
        link_b = pair[1]
        slot_a = link_a.split('=')[0]
        slot_b = link_b.split('=')[0]
        if slot_a == slot_b:
            raise argparse.ArgumentTypeError(f"slot {slot_a} was defined multiple times: {link_a}, {link_b}")


def format_input(args: argparse.Namespace) -> None:
    """
    Formats the input as it was parsed by argParser. This allows for simpler reading and treatment of args
    * Removes whitespace from input
    * Flattens nested lists
    * Removes duplicate values in lists
    * Sorts values in lists in alphabetical order
    :param args: Namespace containing all command line arguments, generated by get_args()
    """
    flatten_arg_lists(args)
    __cannonize_settings(args)
    sort_deduplicate_list_args(args)


def flatten_arg_lists(args: argparse.Namespace) -> None:
    """
    Flattens lists of lists arguments in a given namespace.
    For example,
    [[a], [b, c], []] -> [a, b, c]

    This is applicable to all options that can be used multiple times, and each time get multiple arguments.
    For example: --assert, --verify and --link
    @param args: Namespace containing all command line arguments, generated by get_args()
    """
    for arg_name in vars(args):
        arg_val = getattr(args, arg_name)
        # We assume all list members are of the same type
        if isinstance(arg_val, list) and len(arg_val) > 0 and isinstance(arg_val[0], list):
            flat_list = flatten_nested_list(arg_val)
            flat_list.sort()
            setattr(args, arg_name, flat_list)


def __remove_parsing_whitespace(arg_list: List[str]) -> None:
    """
    Removes all whitespaces added to args by __alter_args_before_argparse():
    1. A leading space before a dash (if added)
    2. space between commas
    :param arg_list: A list of options as strings.
    """
    for idx, arg in enumerate(arg_list):
        arg_list[idx] = arg.strip().replace(', ', ',')


def __cannonize_settings(args: argparse.Namespace) -> None:
    """
    Converts the args.settings into a standard form.
    The standard form is a single list of strings, each string contains no whitespace and represents a single setting
    (that might have an assignment too).

    @dev - --settings are different from all other list arguments, which are formatted by flatten_list_arg(). This is
           because while settings can be inserted multiple times, each time it gets a single string argument (which
           contains multiple settings, separated by commas).

    @param args: Namespace containing all command line arguments, generated by get_args()
    """
    if not hasattr(args, 'settings') or args.settings is None:
        return

    all_settings = list()

    for setting_list in args.settings:
        # Split by commas UNLESS they are inside parenthesis, like -m 'foo(uint256, uint256)'
        for setting in split_by_commas_ignore_parenthesis(setting_list):

            '''
            Lines below remove whitespaces inside the setting argument.
            An example for when this might occur:
            -m 'foo(uint, uint)'
            will result in settings ['-m', 'foo(uint, uint)']
            We wish to replace it to be ['-m', '-foo(uint,uint)'], without the space after the comma
            '''
            setting_split = setting.strip().split('=')
            for i, setting_word in enumerate(setting_split):
                setting_split[i] = setting_word.replace(' ', '')

            setting = '='.join(setting_split)
            all_settings.append(setting)

    args.settings = all_settings


def __sort_dedup_list_arg(arg_list: List[str], arg_name: str) -> List[str]:
    """
    This function takes a list of strings and formats it in two ways:
    1. Removes all duplicate values. If any duplicate value was removed, gives an appropriate warning to the user.
    2. Sorts the values in the list in alphabetical order
    :param arg_list: A list of strings that represents the value of a named argument.
    :param arg_name: Name of the argument this list is the value of. The name is only used in warning prints when
                     removing duplicate values.
    :return: A list with the same values as the original, without duplicates, sorted in alphabetical order.
    """
    all_members = set()
    all_warnings = set()

    for member in arg_list:
        if member in all_members:
            all_warnings.add(f'value {member} for option {arg_name} appears multiple times')
        else:
            all_members.add(member)

    for warning in sorted(list(all_warnings)):
        arg_logger.warning(warning)

    return sorted(list(all_members))


def sort_deduplicate_list_args(args: argparse.Namespace) -> None:
    """
    This function takes all list arguments in the namespace and formats them in two ways:
    1. Removes all duplicate values. If any duplicate value were removed, gives an appropriate warning to the user.
    2. Sorts the values in the list in alphabetical order
    :param args: The namespace generated by the argParse, contains all the options the user gave as input
    """
    for arg_name in vars(args):
        arg_val = getattr(args, arg_name)
        if isinstance(arg_val, list) and len(arg_val) > 0:
            setattr(args, arg_name, __sort_dedup_list_arg(arg_val, arg_name))


def __suggest_contract_name(err_msg: str, contract_name: str, all_contract_names: Set[str],
                            contract_to_file: Dict[str, str]) -> None:
    err_str = err_msg
    suggestions = get_closest_strings(contract_name, list(all_contract_names), max_suggestions=1)

    if len(suggestions) == 1:
        suggested_contract = suggestions[0]
        err_str = f'{err_str}. Maybe you meant contract {suggested_contract} ' \
                  f'(found in file {contract_to_file[suggested_contract]})?'

    raise argparse.ArgumentTypeError(err_str)


def check_contract_name_arg_inputs(args: argparse.Namespace) -> None:
    """
    This function verifies that all options that expect to get contract names get valid contract names.
    If they do, nothing happens. If there is any error, an exception is thrown.
    @param args: Namespace containing all command line arguments, generated by get_args()
    @raise argparse.ArgumentTypeError if a contract name argument was expected, but not given.
    """
    contract_names, file_paths, contract_to_file, file_to_contract = warn_verify_file_args(args.files)
    args.contracts = contract_names
    args.file_paths = file_paths
    args.file_to_contract = file_to_contract

    # we print the warnings at the end of this function, only if no errors were found. Each warning appears only once
    all_warnings = set()

    # Link arguments can be either: contractName:slot=contractName
    #   or contractName:slot=integer(decimal or hexadecimal)
    if args.link is not None:
        for link in args.link:
            executable = link.split(':')[0]
            executable = _get_trivial_contract_name(executable)
            if executable not in contract_names:
                __suggest_contract_name(f"link {link} doesn't match any contract name", executable, contract_names,
                                        contract_to_file)

            library_or_const = link.split('=')[1]
            try:
                parsed_int = int(library_or_const, 0)  # can be either a decimal or hexadecimal number
                if parsed_int < 0:
                    raise argparse.ArgumentTypeError(f"slot number is negative at {link}")
            except ValueError:
                library_name = _get_trivial_contract_name(library_or_const)
                if library_name not in contract_names:
                    __suggest_contract_name(f"link {link} doesn't match any contract name", library_name,
                                            contract_names, contract_to_file)

        check_conflicting_link_args(args)

    args.verified_contract_files = []
    if args.assert_contracts is not None:
        for assert_arg in args.assert_contracts:
            contract = _get_trivial_contract_name(assert_arg)
            if contract not in contract_names:
                __suggest_contract_name(f"--assert argument {contract} doesn't match any contract name", contract,
                                        contract_names, contract_to_file)
            else:
                args.verified_contract_files.append(contract_to_file[contract])

    args.spec_files = None

    if args.verify is not None:
        spec_files = set()
        for ver_arg in args.verify:
            contract, spec = ver_arg.split(':')
            contract = _get_trivial_contract_name(contract)
            if contract not in contract_names:
                __suggest_contract_name(f"--verify argument {contract} doesn't match any contract name", contract,
                                        contract_names, contract_to_file)
            spec_files.add(spec)
            args.verified_contract_files.append(contract_to_file[contract])
        args.spec_files = sorted(list(spec_files))

    contract_to_address = dict()
    if args.address:
        for address_str in args.address:
            contract = address_str.split(':')[0]
            if contract not in contract_names:
                __suggest_contract_name(f"unrecognized contract in --address argument {address_str}", contract,
                                        contract_names, contract_to_file)
            number = address_str.split(':')[1]
            if contract not in contract_to_address:
                contract_to_address[contract] = number
            elif contract_to_address[contract] != number:
                raise argparse.ArgumentTypeError(f'contract {contract} was given two different addresses: '
                                                 f'{contract_to_address[contract]} and {number}')
            else:
                all_warnings.add(f'address {number} for contract {contract} defined twice')
    args.address = contract_to_address

    if args.struct_link:
        contract_slot_to_contract = dict()
        for link in args.struct_link:
            location = link.split('=')[0]
            destination = link.split('=')[1]
            origin = location.split(":")[0]
            if origin not in contract_names:
                __suggest_contract_name(
                    f"--structLink argument {link} is illegal: {origin} is not a defined contract name", origin,
                    contract_names, contract_to_file)
            if destination not in contract_names:
                __suggest_contract_name(
                    f"--structLink argument {link} is illegal: {destination} is not a defined contract name",
                    destination, contract_names, contract_to_file)

            if location not in contract_slot_to_contract:
                contract_slot_to_contract[location] = destination
            elif contract_slot_to_contract[location] == destination:
                all_warnings.add(f"--structLink argument {link} appeared more than once")
            else:
                raise argparse.ArgumentTypeError(f"{location} has two different definitions in --structLink: "
                                                 f"{contract_slot_to_contract[location]} and {destination}")

    for warning in all_warnings:
        arg_logger.warning(warning)


def check_mode_of_operation(args: argparse.Namespace) -> None:
    """
    Ascertains we have only one mode of operation in use and updates args.mode to store it as an enum.
    The modes are:
    1. There is a single .tac file
    2. There is a single .conf file
    3. There is a single .json file
    4. --assert
    5. --verify
    6. --bytecode - the only case in which files may be empty


    This function ascertains there is no overlap between the modes. The correctness of each mode is checked in other
    functions.
    @param args: A namespace including all CLI arguments provided
    @raise an argparse.ArgumentTypeError when:
        1. .conf|.tac|.json file is used with --assert|--verify flags
        2. when both --assert and --verify flags were given
        3. when the file is not .tac|.conf|.json and neither --assert nor --verify were used
        4. If any file is provided with --bytecode flag
        5. If either --bytecode or --bytecode_spec was used without the other.
    """
    is_verifying = args.verify is not None and len(args.verify) > 0
    is_asserting = args.assert_contracts is not None and len(args.assert_contracts) > 0
    is_bytecode = args.bytecode_jsons is not None and len(args.bytecode_jsons) > 0
    has_bytecode_spec = args.bytecode_spec is not None

    if is_verifying and is_asserting:
        raise argparse.ArgumentTypeError("only one option of --assert and --verify can be used")

    special_file_type = None

    if len(args.files) > 0 and is_bytecode:
        raise argparse.ArgumentTypeError("Cannot use --bytecode with other files")

    if len(args.files) == 0 and not is_bytecode:
        raise argparse.ArgumentTypeError("Should always provide input files, unless --bytecode is used")

    if has_bytecode_spec != is_bytecode:
        raise argparse.ArgumentTypeError("Must use --bytecode together with --bytecode_spec")

    if len(args.files) == 1:
        # We already checked that this is the only case where we might encounter CONF or TAC files
        input_file = args.files[0]
        for suffix in [".tac", ".conf", ".json"]:
            if input_file.endswith(suffix):
                special_file_type = suffix

        if special_file_type is not None:
            if is_verifying:
                raise argparse.ArgumentTypeError(
                    f"Option --verify cannot be used with a {special_file_type} file {input_file}")
            if is_asserting:
                raise argparse.ArgumentTypeError(
                    f"Option --assert cannot be used with a {special_file_type} file {input_file}")

    if special_file_type is None and not is_asserting and not is_verifying and not is_bytecode:
        raise argparse.ArgumentTypeError(
            "You must use either --assert or --verify or --bytecode when running the Certora Prover")

    # If we made it here, exactly a single mode was used. We update the namespace entry mode accordingly:
    if is_verifying:
        args.mode = Mode.VERIFY
    elif is_asserting:
        args.mode = Mode.ASSERT
    elif is_bytecode:
        args.mode = Mode.BYTECODE
    elif special_file_type == '.conf':
        args.mode = Mode.CONF
    elif special_file_type == '.tac':
        args.mode = Mode.TAC
    elif special_file_type == '.json':
        args.mode = Mode.REPLAY
    else:
        raise ValueError(f"File {input_file} has unsupported file type {special_file_type}")


def setup_cache(args: argparse.Namespace) -> None:
    """
    Sets automatic caching up, unless it is disabled (only relevant in VERIFY and ASSERT modes).
    The list of contracts, optimistic loops and loop iterations are determining uniquely a cache key.
    If the user has set their own cache key, we will not generate an automatic cache key, but we will also mark it
    as a user defined cache key.

    This function first makes sure to set user_defined_cache to either True or False,
    and then if necessary, sets up the cache key value.
    """

    # we have a user defined cache key if the user provided a cache key
    args.user_defined_cache = args.cache is not None
    if not args.disable_auto_cache_key_gen and not os.environ.get("CERTORA_DISABLE_AUTO_CACHE") is not None:
        if args.mode == Mode.VERIFY or args.mode == Mode.ASSERT:
            if args.cache is None:
                optimistic_loop = args.optimistic_loop
                loop_iter = args.loop_iter
                files = sorted(args.files)
                args.cache = '-'.join(files) + f"-optimistic{optimistic_loop}-iter{loop_iter}"
                arg_logger.debug(f"setting cache key to {args.cache}")


def check_packages_arguments(args: argparse.Namespace) -> None:
    """
    Performs checks on the --packages_path and --packages options.
    @param args: A namespace including all CLI arguments provided
    @raise an argparse.ArgumentTypeError if:
        1. both options --packages_path and --packages options were used
        2. in --packages the same name was given multiples paths
    """
    if args.packages_path is None:
        args.packages_path = os.getenv("NODE_PATH", f"{Path.cwd() / 'node_modules'}")
        arg_logger.debug(f"args.packages_path is {args.packages_path}")

    if args.packages is not None and len(args.packages) > 0:

        package_name_to_path: Dict[str, str] = dict()
        for package_str in args.packages:
            package = package_str.split("=")[0]
            path = package_str.split("=")[1]
            if package in package_name_to_path:
                raise argparse.ArgumentTypeError(
                    f"package {package} was given two paths: {package_name_to_path[package]}, {path}")
            package_name_to_path[package] = path

        args.packages = sorted(args.packages, key=str.lower)

    else:
        if not PACKAGE_FILE.exists():
            arg_logger.warning(f"Default package file {PACKAGE_FILE} not found")
        elif not os.access(PACKAGE_FILE, os.R_OK):
            arg_logger.warning(f"No read permissions for default package file {PACKAGE_FILE}")
        else:
            try:
                with PACKAGE_FILE.open() as package_json_file:
                    package_json = json.load(package_json_file)
                    deps = set(list(package_json["dependencies"].keys()) if "dependencies" in package_json else
                               list(package_json["devDependencies"].keys()) if "devDependencies" in package_json
                               else list())  # May need both

                    packages_path = args.packages_path
                    packages_to_path_list = [f"{package}={packages_path}/{package}" for package in deps]
                    args.packages = sorted(packages_to_path_list, key=str.lower)

            except EnvironmentError:
                ex_type, ex_value, _ = sys.exc_info()
                arg_logger.warning(f"Failed in processing {PACKAGE_FILE}: {ex_type}, {ex_value}")


def validate_certora_key() -> str:
    """
    Checks that the environment variable CERTORAKEY is legal and returns a valid Certora key.
    If the environment variable CERTORAKEY is undefined or empty, the public key is returned.
    If the environment variable CERTORAKEY has a different legal value, returns it.
    @raise RuntimeError if CERTORAKEY has an illegal value.
    """
    key = os.environ.get("CERTORAKEY", "")
    if not key:
        key = PUBLIC_KEY
        arg_logger.warning("Couldn't find Certora Key. Proceeding with Certora Public Key.")
        arg_logger.warning("If you have a private key, press ctrl+c and set the environment variable CERTORAKEY")
        time.sleep(1)

    if not re.match(r'^[0-9A-Fa-f]+$', key):  # checks if the key is a hexadecimal number (without leading 0x)
        raise RuntimeError("environment variable CERTORAKEY has an illegal value")
    if not len(key) in LEGAL_CERTORA_KEY_LENGTHS:
        raise RuntimeError("environment variable CERTORAKEY has an illegal length")
    return key


def check_deployment_args(args: argparse.Namespace) -> None:
    """
    Checks that the user didn't choose both --staging and --cloud
    @param args: A namespace including all CLI arguments provided
    @raise argparse.ArgumentTypeError if both --staging and --cloud options are present in args
    """
    if args.staging:
        if args.cloud:
            raise argparse.ArgumentTypeError("cannot use both --staging and --cloud")
        args.env = DEFAULT_STAGING_ENV
    else:
        args.env = DEFAULT_CLOUD_ENV


def check_solc_solc_map(args: argparse.Namespace) -> None:
    """
    Executes all post-parsing checks of --solc and --solc_map arguments:
    1. --solc and --solc_map cannot be used together
    2. if both --solc and --solc_map were not used, and we are not in conf file mode,
       take the default solc and check its validity
    3. if --solc_map is used and we are not in .conf file mode:
       verify that every contract appears in the map and that every mapping has a valid contract as a
       key. Note: we rely on type_solc_map() to guarantee that no contract appears with conflicting values in the map
    @param args: A namespace including all CLI arguments provided
    @raise argparse.ArgumentTypeError if:
                1. both --solc and --solc_map options are present in args
                2. A key in the solc mapping is not a valid contract
                3. Some contracts do not appear as keys in the solc map
    """
    if args.solc is not None and args.solc_map is not None:
        raise argparse.ArgumentTypeError("You cannot use both --solc and --solc_map arguments")

    if args.solc_map is None:
        args.solc = is_solc_file_valid(args.solc)
    else:  # we use solc_map, check its validity
        orphan_contracts = deepcopy(args.contracts)

        for (contract, solc) in args.solc_map.items():
            if contract not in args.contracts:
                raise argparse.ArgumentTypeError(
                    f"--solc_map argument {contract}={solc}: {contract} is not a contract")
            orphan_contracts.remove(contract)

        if len(orphan_contracts) > 0:
            raise argparse.ArgumentTypeError(
                f"Some contracts do not appear in --solc_map: {', '.join(orphan_contracts)}")


def check_optimize_map(args: argparse.Namespace) -> None:
    """
    Executes all post-parsing checks of --optimize_map and --optimize arguments:
    1. --optimize and --optimize_map cannot be used together
    2. if --optimize_map is used and we are not in .conf file mode:
       Verify that every contract appears exactly once in the map and that every mapping has a valid contract as a
       key. Note: we rely on type_optimize_map() to guarantee that no contract appears with conflicting values
    @param args: A namespace including all CLI arguments provided
    @raise argparse.ArgumentTypeError if:
                1. both --optimize and --optimize_map options are present in args
                2. A key in the mapping is not a valid contract
                3. Some contracts do not appear as keys in the map
    """
    if args.optimize is not None and args.optimize_map is not None:
        raise argparse.ArgumentTypeError("You cannot use both --optimize and --optimize_map arguments")

    if args.optimize_map is not None:

        # See if any contract is missing a number of runs in the map
        orphan_contracts = deepcopy(args.contracts)

        for (contract, num_runs) in args.optimize_map.items():
            if contract not in args.contracts:
                raise argparse.ArgumentTypeError(
                    f"--optimize_map argument {contract}={num_runs}: {contract} is not a contract")
            orphan_contracts.remove(contract)

        if len(orphan_contracts) > 0:
            raise argparse.ArgumentTypeError(
                f"Some contracts do not appear in --optimize_map: {', '.join(orphan_contracts)}")

        # See that there is no --optimize_runs inside --solc_args
        if args.solc_args is not None:
            if '--optimize-runs' in args.solc_args:
                raise argparse.ArgumentTypeError(
                    "You cannot use both --optimize_map and the --solc_args argument --optimize-runs")


def handle_optimize(args: argparse.Namespace) -> None:
    """
    Checks that there are no conflicts between --optimize and --solc_args. If all is good, adds the necessary number of
    runs to solc_args.
    --optimize 800 should be identical to --solc_args '["--optimize", "--optimize-runs", "800"]'. We convert from
    --optimize to --solc_args in this function, unless there is an error.

    We throw on the following errors:
    * If the number of runs between --optimize and --solc_args does not agree
    * --solc_args '["--optimize", "--optimize-runs", "800"]' is malformed AND we use --optimize

    We ignore the following errors:
    * --solc_args '["--optimize", "--optimize-runs", "800"]' is malformed and we DO NOT use --optimize: solc would catch

    It is not considered an error if the number of runs between --optimize and --solc_args agrees, but we warn about
    the redundancy
    """
    if args.solc_args is not None and args.optimize is not None:
        if '--optimize' in args.solc_args:
            if '--optimize-runs' in args.solc_args:
                opt_runs_idx = args.solc_args.index('--optimize-runs')
                num_runs_idx = opt_runs_idx + 1
                if len(args.solc_args) < num_runs_idx:
                    raise argparse.ArgumentTypeError(
                        "solc argument --optimize-runs must be provided an integer value")
                num_runs = args.solc_args[num_runs_idx]
                try:
                    num_runs = int(num_runs)
                except ValueError:
                    raise argparse.ArgumentTypeError("solc argument --optimize-runs must be provided an integer value")
                if num_runs != int(args.optimize):
                    raise argparse.ArgumentTypeError(f"The number of runs to optimize for in --optimize {args.optimize}"
                                                     f" does not agree with solc argument --optimize-runs {num_runs}")
            else:
                '''
                Default number of runs is 200
                https://solidity-fr.readthedocs.io/fr/latest/using-the-compiler.html
                '''
                num_runs = 200
                if num_runs != int(args.optimize):
                    raise argparse.ArgumentTypeError(f"The number of runs to optimize for in --optimize {args.optimize}"
                                                     f" does not agree with solc argument --optimize "
                                                     f"(default of 200 runs)")

            arg_logger.warning("Using solc arguments --optimize (and --optimize-runs) is redundant when"
                               " using certoraRun argument --optimize")
        elif '--optimize-runs' in args.solc_args:
            raise argparse.ArgumentTypeError("solc argument --optimize-runs must appear with solc argument --optimize")
        else:  # Neither --optimize nor --optimize_args are in --solc_args
            args.solc_args += ["--optimize", "--optimize_args", f"{args.optimize}"]
    elif args.optimize is not None:
        # arg.solc_args is None
        args.solc_args = ["--optimize", "--optimize_args", f"{args.optimize}"]


def check_rule(args: argparse.Namespace) -> None:
    """
    Checks that we do not use both --rule (or --settings -rule) in any other mode than --verify
    @param args: a namespace containing command line arguments
    @raises ArgumentTypeError when a user chose a rule with --rule or --settings -rule when not in verify mode
    """
    if args.rule is None:
        return

    if not args.verify and args.bytecode_spec is None:
        raise argparse.ArgumentTypeError(
            "checking for a specific rule is only supported with --verify and --bytecode_spec")


class UniqueStore(argparse.Action):
    """
    This class makes the argparser throw an error for a given flag if it was inserted more than once
    """

    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: Any,  # type: ignore
                 option_string: str) -> None:
        if getattr(namespace, self.dest, self.default) is not self.default:
            parser.error(f"{option_string} appears several times.")
        setattr(namespace, self.dest, values)


def __alter_args_before_argparse(args_list: List[str]) -> None:
    """
    This function is a hack so we can accept the old syntax and still use argparse.
    This function alters the CL input so that it will be parsed correctly by argparse.

    Currently, it fixes two issues:

    1. We want to accept --javaArgs '-a,-b'
    By argparse's default, it is parsed as two different arguments and not one string.
    The hack is to preprocess the arguments, replace the comma with a commaspace.

    2. A problem with --javaArgs -single_flag. The fix is to add a space before the dash artificially.

    NOTE: Must use remove_parsing_whitespace() to undo these changes on argparse.ArgumentParser.parse_args() output!
    :param args_list: A list of CLI options as strings
    """
    for idx, arg in enumerate(args_list):
        if isinstance(arg, str):
            if ',' in arg:
                args_list[idx] = arg.replace(",", ", ")
                arg = args_list[idx]
            if len(arg) > 1 and arg[0] == "-" and arg[1] != "-":  # fixes a problem with --javaArgs -single_flag
                args_list[idx] = " " + arg


def check_args_post_argparse(args: argparse.Namespace) -> None:
    """
    Performs checks over the arguments after basic argparse parsing

    argparse parses option one by one. This is the function that checks all relations between different options and
    arguments. We assume here that basic syntax was already checked.
    @param args: A namespace including all CLI arguments provided
    @raise argparse.ArgumentTypeError if input is illegal
    """
    if args.path is None:
        args.path = str(__default_path())
    check_files_input(args.files)
    check_contract_name_arg_inputs(args)  # Here args.contracts is set
    check_packages_arguments(args)
    check_solc_solc_map(args)
    check_optimize_map(args)
    check_arg_and_setting_consistency(args)
    check_rule(args)
    certora_root_dir = as_posix(get_certora_root_directory())
    default_jar_path = Path(certora_root_dir) / "emv.jar"
    if args.jar is not None or \
            (default_jar_path.is_file() and args.staging is None and args.cloud is None):
        args.local = True
    else:
        args.local = False
        check_deployment_args(args)

    if args.java_args is not None:
        args.java_args = ' '.join(args.java_args).replace('"', '')

    if args.typecheck_only and args.disableLocalTypeChecking:
        raise argparse.ArgumentTypeError("cannot use both --typecheck_only and --disableLocalTypeChecking")

    if args.typecheck_only and args.build_only:
        raise argparse.ArgumentTypeError("cannot use both --typecheck_only and --build_only")

    if args.local and args.typecheck_only:
        raise argparse.ArgumentTypeError("cannot use --typecheck_only in local tool runs")

    if args.send_only:
        if args.local:
            arg_logger.warning("--send_only has no effect in local tool runs")

        if args.short_output:
            arg_logger.warning("When using --send_only, --short_output is automatically enabled; "
                               "--short_output in the command line is redundant")
        else:
            args.short_output = True

    if args.optimize:
        handle_optimize(args)

    if args.debug is None and args.debug_topics:
        raise argparse.ArgumentTypeError("cannot use --debug_topics without --debug")


def __default_path() -> Path:
    path = Path.cwd() / "contracts"
    if path.is_dir():
        return path.resolve()
    return Path.cwd().resolve()


def pre_arg_fetching_checks(args_list: List[str]) -> None:
    """
    This function runs checks on the raw arguments before we attempt to read them with argparse.
    We also replace certain argument values so the argparser will accept them.
    NOTE: use remove_parsing_whitespace() on argparse.ArgumentParser.parse_args() output!
    :param args_list: A list of CL arguments
    :raises argparse.ArgumentTypeError if there are errors (see individual checks for more details):
        - There are wrong quotation marks “ in use
    """
    __check_no_pretty_quotes(args_list)
    __alter_args_before_argparse(args_list)


def __check_no_pretty_quotes(args_list: List[str]) -> None:
    """
    :param args_list: A list of CL arguments
    :raises argparse.ArgumentTypeError if there are wrong quotation marks “ in use (" are the correct ones)
    """
    for arg in args_list:
        if '“' in arg:
            raise argparse.ArgumentTypeError('Please replace “ with " quotation marks')


def handle_version_flag(args_list: List[str]) -> None:
    for arg in args_list:
        if arg == "--version":
            print_version()  # exits the program
            exit(0)


def __get_argparser() -> argparse.ArgumentParser:
    """
    @return: argparse.ArgumentParser with all relevant option arguments, types and logic.

    Do not use `default` as this will cause the conf file loading to be incorrect (conf file will consider the default
    as a user-override, even if the user did not override the option).
    """
    parser = argparse.ArgumentParser(prog="certora-cli arguments and options", allow_abbrev=False)
    parser.add_argument('files', type=type_input_file, nargs='*',
                        help='[contract.sol[:contractName] ...] or CONF_FILE.conf or TAC_FILE.tac')

    mode_args = parser.add_argument_group("Mode of operation. Please choose one, unless using a .conf or .tac file")
    mode_args.add_argument("--verify", nargs='+', type=type_verify_arg, action='append',
                           help='Matches specification files to contracts. For example: '
                                '--verify [contractName:specName.spec ...]')
    mode_args.add_argument("--assert", nargs='+', dest='assert_contracts', type=type_contract, action='append',
                           help='The list of contracts to assert. Usage: --assert [contractName ...]')
    mode_args.add_argument("--bytecode", nargs='+', dest='bytecode_jsons', type=type_json_file, action='append',
                           help='List of EVM bytecode json descriptors. Usage: --bytecode [bytecode1.json ...]')
    mode_args.add_argument("--bytecode_spec", type=type_readable_file, action=UniqueStore,
                           help='Spec to use for the provided bytecodes. Usage: --bytecode_spec myspec.spec')

    # ~~ Useful arguments ~~

    useful_args = parser.add_argument_group("Most frequently used options")
    useful_args.add_argument("--msg", help='Add a message description (alphanumeric string) to your run.',
                             action=UniqueStore)
    useful_args.add_argument("--rule", "--rules", nargs='+', action='append',
                             help="List of specific properties (rules or invariants) you want to verify. "
                                  "Usage: --rule [rule1 rule2 ...] or --rules [rule1 rule2 ...]")

    # ~~ Run arguments ~~

    run_args = parser.add_argument_group("Options affecting the type of verification run")
    run_args.add_argument("--multi_assert_check", action='store_true',
                          help="Check each assertion separately by decomposing every rule "
                               "into multiple sub-rules, each of which checks one assertion while it assumes all "
                               "preceding assertions")

    run_args.add_argument("--rule_sanity", action=UniqueStore,
                          type=type_rule_sanity_flag,
                          nargs="?",
                          default=None,  # default when no --rule_sanity given, may take from --settings
                          const="basic",  # default when --rule_sanity is given, but no argument to it
                          help="Sanity checks for all the rules")

    run_args.add_argument("--short_output", action='store_true',
                          help="Reduces verbosity. It is recommended to use this option in continuous integration")

    # used for build + typechecking only (relevant only when sending to cloud)
    run_args.add_argument('--typecheck_only', action='store_true', help='Stop after typechecking')

    # when sending to the cloud, do not wait for the results
    '''
    Note: --send_only also implies --short_output.
    '''
    run_args.add_argument('--send_only', action='store_true', help='Do not wait for verifications results')

    # ~~ Solidity arguments ~~

    solidity_args = parser.add_argument_group("Options that control the Solidity compiler")
    solidity_args.add_argument("--solc", action=UniqueStore, help="Path to the solidity compiler executable file")
    solidity_args.add_argument("--solc_args", type=type_list, action=UniqueStore,
                               help="List of string arguments to pass for the Solidity compiler, for example: "
                                    "\"['--optimize', '--optimize-runs', '200']\"")
    solidity_args.add_argument("--solc_map", action=UniqueStore, type=type_solc_map,
                               help="Matches each Solidity contract with a Solidity compiler executable file. "
                                    "Usage: <contract_1>=<solc_1>,<contract_2>=<solc_2>[,...] ")
    solidity_args.add_argument("--path", type=type_dir, action=UniqueStore,
                               help='Use the given path as the root of the source tree instead of the root of the '
                                    'filesystem. Default: $PWD/contracts if exists, else $PWD')
    solidity_args.add_argument("--optimize", type=type_non_negative_integer, action=UniqueStore,
                               help="Tells the Solidity compiler to optimize the gas costs of the contract for a given "
                                    "number of runs")
    solidity_args.add_argument("--optimize_map", type=type_optimize_map, action=UniqueStore,
                               help="Matches each Solidity contract with a number of runs to optimize for. "
                                    "Usage: <contract_1>=<num_runs_1>,<contract_2>=<num_runs_2>[,...]")

    # ~~ Package arguments (mutually exclusive) ~~
    solidity_args.add_argument("--packages_path", type=type_dir, action=UniqueStore,
                               help="Path to a directory including the Solidity packages (default: $NODE_PATH)")
    solidity_args.add_argument("--packages", nargs='+', type=type_package, action=UniqueStore,
                               help='A mapping [package_name=path, ...]')

    # ~~ Loop handling arguments ~~

    loop_args = parser.add_argument_group("Options regarding source code loops")
    loop_args.add_argument("--optimistic_loop", action='store_true',
                           help="After unrolling loops, assume the loop halt conditions hold")
    loop_args.add_argument("--loop_iter", type=type_non_negative_integer, action=UniqueStore,
                           help="The maximal number of loop iterations we verify for. Default: 1")

    # ~~ Options that help reduce the running time ~~

    run_time_args = parser.add_argument_group("Options that help reduce running time")

    # Currently the jar only accepts a single rule with -rule
    run_time_args.add_argument("--method", action=UniqueStore, type=type_method,
                               help="Parametric rules will only verify given method. "
                                    "Usage: --method 'fun(uint256,bool)'")
    run_time_args.add_argument("--cache", help='name of the cache to use', action=UniqueStore)
    run_time_args.add_argument("--smt_timeout", type=type_positive_integer, action=UniqueStore,
                               help="Set max timeout for all SMT solvers in seconds, default is 600")

    # ~~ Linkage arguments ~~

    linkage_args = parser.add_argument_group("Options to set addresses and link contracts")
    linkage_args.add_argument("--link", nargs='+', type=type_link_arg, action='append',
                              help='Links a slot in a contract with another contract. Usage: ContractA:slot=ContractB')
    linkage_args.add_argument("--address", nargs='+', type=type_address, action=UniqueStore,
                              help='Set an address manually. Default: automatic assignment by the python script. '
                                   'Format: <contractName>:<number>')
    linkage_args.add_argument("--structLink", nargs='+', type=type_struct_link, action=UniqueStore, dest='struct_link',
                              help='Linking to a struct field, <contractName>:<number>=<contractName>')

    # ~~ Debugging arguments ~~

    info_args = parser.add_argument_group("Debugging options")
    info_args.add_argument("--debug", nargs='?', default=None, const="",
                           help="Use this flag to see debug statements. A comma separated list filters logger topics")
    info_args.add_argument("--debug_topics", action="store_true", help="Include topic names in debug messages")

    # --version was handled before, it is here just for the help message
    info_args.add_argument('--version', action='version', help='Show the tool version',
                           version='This message should never be reached')

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Hidden flags ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # ~~ Running Environment arguments ~~
    env_args = parser.add_argument_group("Running environment selection arguments")
    """
    Behavior:
    if --cloud is not used, args.cloud is None
    if --cloud is used without an argument, arg.cloud == DEFAULT_CLOUD_ENV (currently 'production')
    if --cloud is used with an argument, stores it under args.cloud
    same for --staging, except the default is 'master'
    """
    env_args.add_argument("--staging", nargs='?', action=UniqueStore, const=DEFAULT_STAGING_ENV,
                          help=argparse.SUPPRESS)
    env_args.add_argument("--cloud", nargs='?', action=UniqueStore, const=DEFAULT_CLOUD_ENV,
                          help=argparse.SUPPRESS)

    # ~~ Java arguments ~~

    java_args = parser.add_argument_group("Arguments passed to the .jar file")

    # Path to the Certora prover's .jar file
    java_args.add_argument("--jar", type=type_jar, action=UniqueStore, help=argparse.SUPPRESS)

    # arguments to pass to the .jar file
    java_args.add_argument("--javaArgs", type=type_java_arg, action='append', dest='java_args',
                           help=argparse.SUPPRESS)

    # ~~ Partial run arguments ~~

    partial_args = parser.add_argument_group("These arguments run only specific parts of the tool, or skip parts")

    # used for debugging command line option parsing.
    partial_args.add_argument('--check_args', action='store_true', help=argparse.SUPPRESS)

    # used for debugging the build only
    partial_args.add_argument('--build_only', action='store_true', help=argparse.SUPPRESS)

    # A setting for disabling the local type checking (e.g., if we have a bug in the jar published with the python and
    # want users not to get stuck and get the type checking from the cloud instead).
    partial_args.add_argument('--disableLocalTypeChecking', action='store_true', help=argparse.SUPPRESS)

    # Do not compare the verification results with expected.json
    partial_args.add_argument("--no_compare", action='store_true', help=argparse.SUPPRESS)
    partial_args.add_argument("--expected_file", type=type_optional_readable_file, action=UniqueStore,
                              help='JSON file to use as expected results for comparing the output')

    # ~~ Cloud control arguments ~~

    cloud_args = parser.add_argument_group("Fine cloud control arguments")

    cloud_args.add_argument('--queue_wait_minutes', type=type_non_negative_integer, action=UniqueStore,
                            help=argparse.SUPPRESS)
    cloud_args.add_argument('--max_poll_minutes', type=type_non_negative_integer, action=UniqueStore,
                            help=argparse.SUPPRESS)
    cloud_args.add_argument('--log_query_frequency_seconds', type=type_non_negative_integer, action=UniqueStore,
                            help=argparse.SUPPRESS)
    cloud_args.add_argument('--max_attempts_to_fetch_output', type=type_non_negative_integer, action=UniqueStore,
                            help=argparse.SUPPRESS)
    cloud_args.add_argument('--delay_fetch_output_seconds', type=type_non_negative_integer, action=UniqueStore,
                            help=argparse.SUPPRESS)
    cloud_args.add_argument('--process', action=UniqueStore, default='emv', help=argparse.SUPPRESS)

    # ~~ Miscellaneous hidden arguments ~~

    misc_hidden_args = parser.add_argument_group("Miscellaneous hidden arguments")

    misc_hidden_args.add_argument("--settings", type=type_settings_arg, action='append', help=argparse.SUPPRESS)

    misc_hidden_args.add_argument("--log_branch", action=UniqueStore, help=argparse.SUPPRESS)

    # Disable automatic cache key generation. Useful for CI testing
    misc_hidden_args.add_argument("--disable_auto_cache_key_gen", action='store_true', help=argparse.SUPPRESS)

    # If the control flow graph is deeper than this argument, do not draw it
    misc_hidden_args.add_argument("--max_graph_depth", type=type_non_negative_integer, action=UniqueStore,
                                  help=argparse.SUPPRESS)

    # Path to a directory at which tool output files will be saved
    misc_hidden_args.add_argument("--toolOutput", type=type_tool_output_path, action=UniqueStore, dest='tool_output',
                                  help=argparse.SUPPRESS)

    # A json file containing a map from public function signatures to internal function signatures for function finding
    # purposes
    misc_hidden_args.add_argument("--internal_funcs", type=type_json_file, action=UniqueStore,
                                  help=argparse.SUPPRESS)

    # Run in Coinbase features mode
    misc_hidden_args.add_argument("--coinbaseMode", action='store_true', help=argparse.SUPPRESS)

    return parser


def prepare_replay_mode(args: argparse.Namespace) -> None:
    """
    extract all input files from json and dump them
     - a conf file will be used as in CONF mode
     - .certora_build.json and .certora_verify.json will be used as if they
       had been produced by certoraBuild.py:build(..)
    """
    print('Got a .json file as input. Running in replay mode.')
    replay_json_filename = Path(args.files[0])
    replay_conf, replay_namespace = dump_replay_files(replay_json_filename)
    if replay_conf:
        run_logger.debug("using conf from replay to update args")
        read_from_conf(replay_conf, args)
    elif replay_namespace:
        run_logger.debug("using args from replay file as args")
        args = replay_namespace
        # do our args postprocessing on the imported args
        flatten_arg_lists(args)
        check_mode_of_operation(args)


def dump_replay_files(replay_json_filename: Path) -> Tuple[Optional[Dict[str, Any]], Optional[argparse.Namespace]]:
    """
    Dump the replay data from the replay_json (files .certora_build.json, etc)
    Also return the config (format as in .conf files).
    :param replay_json_filename: json file with replay data
    :return: config as a json object in .conf file format, if available in the replay file, alternatively a namespace
        created from the raw_args entry in the replay file
    """
    with replay_json_filename.open() as replay_json_file:
        run_logger.debug(f'Reading replay json configuration from: {abs_posix_path(replay_json_filename)}')
        replay_json = json.load(replay_json_file)
        repro = replay_json['reproduction']

        # dump certora_[build,verify,metadata]
        pairs = [(repro['certoraMetaData'], CERTORA_METADATA_FILE),
                 (repro['certoraBuild'], CERTORA_BUILD_FILE),
                 (repro['certoraVerify'], CERTORA_VERIFY_FILE),
                 ]

        for json_data, dump_target_name in pairs:
            with dump_target_name.open("w") as dump_target:
                json.dump(json_data, dump_target)

        # dump certora_settings (directory and all contents)
        if CERTORA_CONFIG_DIR.is_dir():
            run_logger.debug(f'deleting dir {abs_posix_path(CERTORA_CONFIG_DIR)}')
            shutil.rmtree(CERTORA_CONFIG_DIR)

        run_logger.debug(f'creating dir {abs_posix_path(CERTORA_CONFIG_DIR)}')
        CERTORA_CONFIG_DIR.mkdir()

        for file_name, file_contents in repro['certoraConfig'].items():
            split_path = Path(file_name).parts

            split_path_from_configdir = split_path[split_path.index(CERTORA_CONFIG_DIR.name):]

            file_path_from_conf_dir = Path(os.path.join(*split_path_from_configdir))

            # Recursively create all the directories in the path of the extra directory, if they do not exist
            dir_containing_file = file_path_from_conf_dir.parent
            if not dir_containing_file.is_dir():
                dir_containing_file.mkdir(parents=True)

            with file_path_from_conf_dir.open("w") as dump_target:
                run_logger.debug(f"dumping: {file_path_from_conf_dir}")
                dump_target.write(file_contents)

        # read conf (in .conf file format) from corresponding entry in json
        try:
            conf_json = repro['certoraMetaData']['conf']
            namespace = None
        except KeyError:
            # no conf entry, trying to reconstruct from raw_args
            raw_args = repro['certoraMetaData']['raw_args']
            __alter_args_before_argparse(raw_args)
            parser = __get_argparser()
            namespace = parser.parse_args(raw_args[1:])
            arg_logger.debug(f'parsed back raw_args from replay json: {namespace}')
            conf_json = None

    return conf_json, namespace


def get_args(args_list: Optional[List[str]] = None) -> Tuple[argparse.Namespace, Dict[str, Any]]:
    if args_list is None:
        args_list = sys.argv

    '''
    Compiles an argparse.Namespace from the given list of command line arguments.
    Additionally returns the prettified dictionary version of the input arguments as generated by current_conf_to_file
    and printed to the .conf file in .lastConfs.

    Why do we handle --version before argparse?
    Because on some platforms, mainly CI tests, we cannot fetch the installed distribution package version of
    certora-cli. We want to calculate the version lazily, only when --version was invoked.
    We do it pre-argparse, because we do not care bout the input validity of anything else if we have a --version flag
    '''
    handle_version_flag(args_list)

    pre_arg_fetching_checks(args_list)
    parser = __get_argparser()

    # if there is a --help flag, we want to ignore all parsing errors, even those before it:
    if '--help' in args_list:
        parser.print_help()
        exit(0)

    args = parser.parse_args(args_list)
    setup_log_arguments(args)

    __remove_parsing_whitespace(args_list)

    format_input(args)

    check_mode_of_operation(args)  # Here args.mode is set
    setup_cache(args)  # Here args.cache, args.user_defined_cache are set

    if args.mode == Mode.REPLAY:
        prepare_replay_mode(args)

    if args.mode == Mode.CONF:
        read_from_conf_file(args)

    # Store current options (including the ones read from .conf file)
    conf_options = current_conf_to_file(args)

    # Setup defaults (defaults are not recorded in conf file)
    if args.expected_file is None:
        args.expected_file = "expected.json"

    check_args_post_argparse(args)

    arg_logger.debug("parsed args successfully.")
    arg_logger.debug(f"args= {args}")
    if args.check_args:
        sys.exit(0)
    return args, conf_options


def entry_point() -> None:
    """
    This function is the entry point of the certora_cli customer-facing package, as well as this script.
    It is important this function gets no arguments!
    """
    run_certora(sys.argv[1:], is_library=False)


if __name__ == '__main__':
    entry_point()
