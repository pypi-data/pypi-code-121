import json
import os
from typing import Any, Dict, List
import subprocess
import argparse
from datetime import datetime
from Shared.certoraUtils import Mode
import logging
from pathlib import Path
from copy import deepcopy

CERTORA_METADATA_FILE = Path(".certora_metadata.json")

metadata_logger = logging.getLogger("metadata")


# jsonify sets as lists
class MetadataEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, Mode):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class RunMetaData:
    """
    Carries information about a run of CVT.
    This includes
      - which arguments CVT was started with,
      - information about the state (snapshot) of the git repository that CVT was called in (we expect this to be the
        repository where the program and spec lie in that CVT was started on).

    arguments:
    raw_args -- arguments to `certoraRun.py`, basically python's sys.argv list
    conf -- configuration as processed by certoraConfigIO
    args -- arguments after parsing by certoraRun, includes default values
    origin -- origin URL of the git repo
    revision -- commit hash of the currently checked-out revision
    branch -- branch name of the currently checked-out revision
    cwd_relative -- current working directory, relative to the root of the git repository
    dirty -- true iff the git repository has changes (git diff is not empty)
    """
    def __init__(self, raw_args: List[str], conf: Dict[str, Any], args: Dict[str, str], origin: str, revision: str,
                 branch: str, cwd_relative: Path, dirty: bool):
        self.raw_args = raw_args
        self.conf = conf
        self.args = args
        self.origin = origin
        self.revision = revision
        self.branch = branch
        self.cwd_relative = cwd_relative
        self.dirty = dirty
        self.timestamp = str(datetime.utcnow().timestamp())

    def __repr__(self) -> str:
        return (
            f" raw_args: {self.raw_args}\n" +
            f" conf: {self.conf}\n" +
            f" args: {self.args}\n" +
            f" origin: {self.origin}\n" +
            f" revision: {self.revision}\n" +
            f" branch: {self.branch}\n" +
            f" cwd_relative: {self.cwd_relative}\n" +
            f" dirty: {self.dirty}\n"
        )

    def dump(self) -> None:
        if self.__dict__:  # dictionary containing all the attributes defined for GitInfo
            try:
                dump_dict = deepcopy(self.__dict__)
                # Casting from path to string
                dump_dict['cwd_relative'] = str(self.cwd_relative)
                with CERTORA_METADATA_FILE.open("w+") as output_file:
                    json.dump(dump_dict, output_file, indent=4, sort_keys=True, cls=MetadataEncoder)
            except Exception as e:
                print(f"failed to write meta data file {CERTORA_METADATA_FILE}")
                metadata_logger.debug('encountered an error', exc_info=e)


def improvise_cwd_relative(cwd: Path) -> Path:
    """
    Computes the metadata entry called `cwd_relative`. This entry indicates the working directory of the toolrun
    relative to the repository root of the git repo that the test lies in. Normally this is computed using git calls.
    This method is a fallback for when there is no `git` executable, or the current working dir is not in a git working
    copy.
    It looks for the two standard cases for our internal regression tests, namely `EVMVerifier/Test` and
    `EVMVerifier/CustomersCode`.
    :param cwd: working directory of the current tool run.
    :return:
    """
    cwd_abs = cwd.resolve()
    evmv_test_split = str(cwd_abs).split(f'{os.sep}EVMVerifier{os.sep}Test{os.sep}')
    evmv_customerscode_split = str(cwd_abs).split(f'{os.sep}EVMVerifier{os.sep}CustomersCode{os.sep}')
    base_dir = Path().resolve()
    if len(evmv_test_split) > 1:
        assert len(evmv_test_split) == 2, f'unexpected path split result for ({cwd_abs}).split({evmv_test_split}): ' \
                                          f'{evmv_test_split}'
        base_dir = Path('Test') / evmv_test_split[1]

    if len(evmv_customerscode_split) > 1:
        assert len(evmv_customerscode_split) == 2, f'unexpected path split result for ' \
                                                   f'({cwd_abs}).split({evmv_customerscode_split}): ' \
                                                   f'{evmv_customerscode_split}'
        assert base_dir == Path(), f'unexpected path format, containing both {evmv_test_split} and ' \
                                   f'{evmv_customerscode_split}: {cwd_abs}'
        base_dir = Path(evmv_customerscode_split[1])

    cwd_relative = cwd_abs.relative_to(base_dir)
    metadata_logger.debug(f'improvised base dir reconstruction found {cwd_relative.as_posix()}')
    return cwd_relative


def collect_run_metadata(wd: Path, raw_args: List[str], conf_dict: Dict[str, Any], args: argparse.Namespace
                         ) -> RunMetaData:
    # collect information about current git snapshot
    cwd_abs = wd.resolve()

    is_git_executable = False
    git_present_out = None
    try:
        git_present_out = subprocess.run(['git', '--version'], cwd=wd,
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        is_git_executable = git_present_out.returncode == 0
    except Exception as e:
        metadata_logger.debug('error occurred when running git executable', exc_info=e)
    if not is_git_executable:
        metadata_logger.debug(f'no git executable found in {wd}, not collecting any repo metadata')
        if git_present_out:
            metadata_logger.debug(f'running git --version returned {git_present_out}')
        return RunMetaData(raw_args, conf_dict, vars(args), "", "", "", improvise_cwd_relative(wd), True)

    try:
        sha_out = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=wd,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sha = sha_out.stdout.decode().strip()

        branch_name_out = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=wd,
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        branch_name = branch_name_out.stdout.decode().strip()

        origin_out = subprocess.run(['git', 'remote', 'get-url', 'origin'], cwd=wd,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        origin = origin_out.stdout.decode().strip()

        base_dir_out = subprocess.run(['git', 'rev-parse', '--show-toplevel'], cwd=wd,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        base_dir = base_dir_out.stdout.decode().strip()
        cwd_relative = cwd_abs.relative_to(base_dir)

        dirty_out = subprocess.run(['git', 'diff', '--shortstat'], cwd=wd,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        dirty = dirty_out.stdout.decode().strip() != ''

        data = RunMetaData(raw_args, conf_dict, vars(args), origin, sha, branch_name, cwd_relative, dirty)

        metadata_logger.debug(f' collected data:\n{str(data)}')

        return data
    except Exception as e:
        metadata_logger.debug('error occurred when running git executable', exc_info=e)
        return RunMetaData(raw_args, conf_dict, vars(args), "", "", "", improvise_cwd_relative(wd), True)
