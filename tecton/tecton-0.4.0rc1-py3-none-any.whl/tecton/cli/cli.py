import glob
import importlib
import io
import os
import sys
import tarfile
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Callable
from typing import List
from typing import Tuple

import click
import pytest
import requests
from colorama import Fore
from google.protobuf.empty_pb2 import Empty
from yaspin.spinners import Spinners

import tecton
from .cli_utils import bold
from .cli_utils import confirm_or_exit
from tecton._internals import metadata_service
from tecton._internals import sdk_decorators
from tecton._internals.analytics import TectonStateUpdateMetrics
from tecton._internals.display import Displayable
from tecton._internals.fco import Fco
from tecton._internals.tecton_errors import TectonAPIInaccessibleError
from tecton._internals.utils import format_freshness_table
from tecton._internals.utils import format_materialization_attempts
from tecton._internals.utils import get_all_freshness
from tecton.cli import api_key
from tecton.cli import common
from tecton.cli import printer
from tecton.cli import workspace
from tecton.cli.command import _cluster_url
from tecton.cli.command import TectonCommand
from tecton.cli.command import TectonGroup
from tecton.cli.common import get_current_workspace
from tecton.cli.engine import dump_local_state
from tecton.cli.engine import update_tecton_state
from tecton.cli.error_utils import pretty_error
from tecton.okta import OktaAuthorizationFlow
from tecton_proto.metadataservice.metadata_service_pb2 import GetFeatureViewRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetMaterializationStatusRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetRestoreInfoRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetStateUpdateLogRequest
from tecton_spark import repo_file_handler
from tecton_spark.fco_container import FcoContainer

CONTEXT_SETTINGS = {
    "max_content_width": 160,
    "help_option_names": ["-h", "--help"],
}

_CLIENT_VERSION_INFO_RESPONSE_HEADER = "x-tecton-client-version-info"
_CLIENT_VERSION_WARNING_RESPONSE_HEADER = "x-tecton-client-version-warning"


@click.group(name="tecton", context_settings=CONTEXT_SETTINGS, cls=TectonGroup)
@click.option("--verbose/--no-verbose", default=False, help="Be verbose")
@click.option("--debug/--no-debug", default=False, help="Enable debug info.")
@click.pass_context
def cli(ctx, verbose, debug):
    "Tecton command-line tool."
    from tecton_spark.logger import set_logging_level
    import logging

    set_logging_level(logging.ERROR)
    sdk_decorators.disable_sdk_public_method_decorator()

    # add cwd to path
    sys.path.append("")


@cli.command(requires_auth=False)
def version():
    """Print version."""
    tecton.version.summary()


class EngineCommand(TectonCommand):
    def __init__(
        self, *args, apply: bool, upgrade_all: bool = False, destroy: bool = False, has_plan_id: bool = False, **kwargs
    ):
        @click.pass_context
        def callback(ctx, skip_tests, safety_checks, json_out, suppress_warnings, plan_id=None):
            args = EngineArgs(
                skip_tests=skip_tests,
                no_safety_checks=(not safety_checks),
                json_out=json_out,
                suppress_warnings=suppress_warnings,
                debug=common.get_debug(ctx),
            )
            if plan_id:
                args.plan_id = plan_id
            return run_engine(args, apply=apply, upgrade_all=upgrade_all, destroy=destroy)

        params = [
            # TODO(Add help)
            click.Option(["--skip-tests/--no-skip-tests"], default=False),
            click.Option(
                ["--safety-checks/--no-safety-checks"], default=True, help="Disable interactive safety checks."
            ),
            click.Option(
                ["--json-out"],
                default="",
                help="[BETA][not stable] Output the tecton state update diff (as JSON) to the file path provided.",
            ),
            click.Option(
                ["--suppress-warnings"],
                is_flag=True,
                default=False,
                help="Disable tecton plan linting warnings.",
            ),
        ]
        if has_plan_id:
            params.append(
                click.Option(["--plan-id"], default=None, type=str, help="Id of a previously computed plan to apply.")
            )
        super().__init__(*args, callback=callback, params=params, uses_workspace=True, **kwargs)


cli.add_command(api_key.api_key)
cli.add_command(workspace.workspace)
cli.add_command(
    EngineCommand(
        name="plan",
        apply=False,
        help="Compare your local feature definitions with remote state and *show* the plan to bring them in sync.",
    )
)
cli.add_command(
    EngineCommand(
        name="apply",
        apply=True,
        has_plan_id=True,
        help="Compare your local feature definitions with remote state and *apply* local changes to the remote.",
    )
)
cli.add_command(
    EngineCommand(
        name="upgrade",
        apply=True,
        upgrade_all=True,
        help="Upgrade remote feature definitions.",
        hidden=True,
    )
)
cli.add_command(
    EngineCommand(
        name="destroy",
        destroy=True,
        apply=True,
        help="Destroy all registered objects in this workspace.",
    )
)


@cli.command(uses_workspace=True, requires_auth=False)
@click.pass_context
def test(ctx):
    """Run Tecton tests."""
    run_tests(debug=common.get_debug(ctx))


def py_path_to_module(path: Path, repo_root: Path) -> str:
    return str(path.relative_to(repo_root))[: -len(".py")].replace("./", "").replace("/", ".").replace("\\", ".")


def plural(x, singular, plural):
    if x == 1:
        return singular
    else:
        return plural


def import_module_with_pretty_errors(
    file_path: Path,
    module_path: str,
    py_files: List[Path],
    repo_root: Path,
    debug: bool,
    before_error: Callable[[], None],
) -> ModuleType:
    from pyspark.sql.utils import AnalysisException

    try:
        module = importlib.import_module(module_path)
        if Path(module.__file__) != file_path:
            before_error()
            relpath = file_path.relative_to(repo_root)
            printer.safe_print(
                f"Python module name {bold(module_path)} ({relpath}) conflicts with module {module_path} from {module.__file__}. Please use a different name.",
                file=sys.stderr,
            )
            sys.exit(1)

        return module
    except AnalysisException as e:
        before_error()
        pretty_error(
            Path(file_path),
            py_files,
            exception=e,
            repo_root=repo_root,
            error_message="Analysis error",
            error_details=e.desc,
            debug=debug,
        )
        sys.exit(1)
    except tecton.tecton_errors.TectonValidationError as e:
        before_error()
        pretty_error(Path(file_path), py_files, exception=e, repo_root=repo_root, error_message=e.args[0], debug=debug)
        sys.exit(1)
    except SyntaxError as e:
        before_error()
        details = None
        if e.text and e.offset:
            details = e.text + (" " * e.offset) + "^^^"
        pretty_error(
            Path(file_path),
            py_files,
            exception=e,
            repo_root=repo_root,
            error_message=e.args[0],
            error_details=details,
            debug=debug,
        )
        sys.exit(1)
    except TectonAPIInaccessibleError as e:
        before_error()
        printer.safe_print("Failed to connect to Tecton server at", e.args[1], ":", e.args[0])
        sys.exit(1)
    except Exception as e:
        before_error()
        pretty_error(Path(file_path), py_files, exception=e, repo_root=repo_root, error_message=e.args[0], debug=debug)
        sys.exit(1)


def collect_top_level_objects(py_files: List[Path], repo_root: Path, debug: bool, pretty_errors: bool) -> List[Fco]:
    from tecton._internals.fco import _ALL_FCOS

    modules = [py_path_to_module(p, repo_root) for p in py_files]

    with printer.safe_yaspin(Spinners.earth, text="Importing feature repository modules") as sp:
        for file_path, module_path in zip(py_files, modules):
            sp.text = f"Processing feature repository module {module_path}"

            if pretty_errors:
                module = import_module_with_pretty_errors(
                    file_path=file_path,
                    module_path=module_path,
                    py_files=py_files,
                    repo_root=repo_root,
                    debug=debug,
                    before_error=lambda: sp.fail(printer.safe_string("⛔")),
                )
            else:
                module = importlib.import_module(module_path)

        num_modules = len(modules)
        sp.text = (
            f"Imported {num_modules} Python {plural(num_modules, 'module', 'modules')} from the feature repository"
        )
        sp.ok(printer.safe_string("✅"))

        return list(_ALL_FCOS.values())


def prepare_args(debug: bool) -> Tuple[List[Fco], str, List[Path]]:
    repo_file_handler.ensure_prepare_repo()
    repo_files = repo_file_handler.repo_files()
    repo_root = repo_file_handler.repo_root()

    py_files = [p for p in repo_files if p.suffix == ".py"]
    os.chdir(repo_root)

    top_level_objects = collect_top_level_objects(py_files, repo_root=Path(repo_root), debug=debug, pretty_errors=True)

    return top_level_objects, repo_root, repo_files


def print_version_msg(message, is_warning=False):
    if isinstance(message, list):
        message = message[-1] if len(message) > 0 else ""
    color = Fore.YELLOW
    if is_warning:
        message = "⚠️  " + message
    printer.safe_print(color + message + Fore.RESET)


def check_version():
    try:
        response = metadata_service.instance().Nop(request=Empty())
        client_version_msg_info = response._headers().get(_CLIENT_VERSION_INFO_RESPONSE_HEADER)
        client_version_msg_warning = response._headers().get(_CLIENT_VERSION_WARNING_RESPONSE_HEADER)

        # Currently, only _CLIENT_VERSION_INFO_RESPONSE_HEADER and _CLIENT_VERSION_WARNING_RESPONSE_HEADER
        # metadata is used in the response, whose values have str type.
        # The returned types have 3 cases as of PR #3696:
        # - Metadata value type is List[str] if it's returned from go proxy if direct http is used.
        # - Metadata value is first str in List[str] returned from go proxy if grpc gateway is used.
        # - Metadata value type is str if direct grpc is used.
        # The default values of keys that don't exist are empty strings in any of the 3 cases.
        if client_version_msg_info:
            print_version_msg(client_version_msg_info)
        if client_version_msg_warning:
            print_version_msg(client_version_msg_warning, is_warning=True)
    except Exception as e:
        printer.safe_print("Error connecting to tecton server: ", e, file=sys.stderr)
        sys.exit(1)


@cli.command(hidden=True)
@click.pass_context
def dump(ctx) -> None:
    """Print debug info."""
    top_level_objects, _, _ = prepare_args(common.get_debug(ctx))
    dump_local_state(top_level_objects)


def get_test_paths(repo_root) -> List[str]:
    # Be _very_ careful updating this:
    #    `glob.glob` does bash-style globbing (ignores hidden files)
    #    `pathlib.Path.glob` does _not_ do bash-style glob (it shows hidden)
    #
    # Ignoring hidden files is a very important expectation for our usage of
    # pytest. Otherwise, we may test files that user does not intend us to
    # (like in their .git or .tox directories).
    #
    # NOTE: This won't filter out hidden files for Windows. Potentially:
    #    `bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)`
    # would filter hidden files for Windows, but this would need some testing.
    candidate_test_files = glob.iglob(f"{repo_root}/**/tests/**/*.py", recursive=True)

    VIRTUAL_ENV = os.getenv("VIRTUAL_ENV")
    if VIRTUAL_ENV:
        return list(filter(lambda f: not f.startswith(VIRTUAL_ENV), candidate_test_files))

    return list(candidate_test_files)


def run_tests(debug: bool):
    repo_root = repo_file_handler._maybe_get_repo_root()
    if repo_root is None:
        printer.safe_print("Tecton tests must be run from a feature repo initialized using 'tecton init'!")
        sys.exit(1)

    prepare_args(debug)

    tests = get_test_paths(repo_root)
    if len(tests) == 0:
        printer.safe_print("⚠️  Running Tests: No tests found.")
        return

    os.chdir(repo_root)
    args = ["-s"] + tests

    printer.safe_print("🏃 Running Tests")
    exitcode = pytest.main(args)

    if exitcode == 5:
        # https://docs.pytest.org/en/stable/usage.html#possible-exit-codes
        printer.safe_print("⚠️  Running Tests: No tests found.")
        return None
    elif exitcode != 0:
        printer.safe_print("⛔ Running Tests: Tests failed :(")
        sys.exit(1)
    else:
        printer.safe_print("✅ Running Tests: Tests passed!")


# TODO: This class was created to match the old style arg parse struct when we were migrating to click to avoid having
# do a deep refactoring of the code that depends on it. It should be replaced.
@dataclass
class EngineArgs:
    skip_tests: bool
    no_safety_checks: bool
    json_out: str
    suppress_warnings: bool

    debug: bool


def run_engine(args: EngineArgs, apply: bool = False, destroy=False, upgrade_all=False) -> TectonStateUpdateMetrics:
    check_version()

    # Resolve the json_out_filename prior to running `prepare_args(...)` so
    # that relative directories in the file name are supported (`prepare_args`
    # changes the working directory).
    json_out_path = None
    if args.json_out:
        json_out_path = Path(args.json_out).resolve()

    # Must use hasattr instead of args.plan_id, because only `apply` has the plan_id arg, but this
    # code path is also used by `plan`, `destroy`, and `upgrade`, which will fail on args.plan_id
    plan_id = None
    if hasattr(args, "plan_id"):
        plan_id = args.plan_id

    if destroy:
        top_level_objects: List[Fco] = []
        repo_root = None
        repo_files: List[Path] = []
    else:
        top_level_objects, repo_root, repo_files = prepare_args(args.debug)

    if not (args.skip_tests or apply and plan_id):
        run_tests(args.debug)

    return update_tecton_state(
        objects=top_level_objects,
        apply=apply,
        debug=args.debug,
        interactive=not args.no_safety_checks,
        repo_files=repo_files,
        repo_root=repo_root,
        upgrade_all=upgrade_all,
        suppress_warnings=args.suppress_warnings,
        json_out_path=json_out_path,
        plan_id=plan_id,
        workspace_name=get_current_workspace(),
    )


@cli.command(requires_auth=False)
def init() -> None:
    """Initialize feature repo."""
    init_feature_repo()


def init_feature_repo() -> None:
    if Path().resolve() == Path.home():
        printer.safe_print("You cannot set feature repository root to the home directory", file=sys.stderr)
        sys.exit(1)

    # If .tecton exists in a parent or child directory, error out.
    repo_root = repo_file_handler._maybe_get_repo_root()
    if repo_root not in [Path().resolve(), None]:
        printer.safe_print(".tecton already exists in a parent directory:", repo_root)
        sys.exit(1)

    child_dir_matches = list(Path().rglob("*/.tecton"))
    if len(child_dir_matches) > 0:
        dirs_str = "\n\t".join(map(lambda c: str(c.parent.resolve()), child_dir_matches))
        printer.safe_print(f".tecton already exists in child directories:\n\t{dirs_str}")
        sys.exit(1)

    dot_tecton = Path(".tecton")
    if not dot_tecton.exists():
        dot_tecton.touch()
        printer.safe_print("Local feature repository root set to", Path().resolve(), "\n", file=sys.stderr)
        printer.safe_print("💡 We recommend tracking this file in git:", Path(".tecton").resolve(), file=sys.stderr)
        printer.safe_print(
            "💡 Run `tecton apply` to apply the feature repository to the Tecton cluster.", file=sys.stderr
        )
    else:
        printer.safe_print("Feature repository is already set to", Path().resolve(), file=sys.stderr)


@cli.command(uses_workspace=True)
@click.argument("commit_id", required=False)
def restore(commit_id):
    """Restore feature repo state to that of past `tecton apply`.

    The commit to restore can either be passed as COMMIT_ID, or the latest will be used.
    """
    # Get the repo download URL from the metadata service.
    r = GetRestoreInfoRequest()
    r.workspace = common.get_current_workspace()
    if commit_id:
        r.commit_id = commit_id
    response = metadata_service.instance().GetRestoreInfo(r)

    # Download the repo.
    url = response.signed_url_for_repo_download
    commit_id = response.commit_id
    sdk_version = response.sdk_version
    # TODO: always print this message once enough customers are on new sdk versions
    sdk_version_msg = f"applied by SDK version {sdk_version}" if sdk_version else ""
    printer.safe_print(f"Restoring from commit {commit_id} {sdk_version_msg}")
    try:
        tar_response = requests.get(url)
        tar_response.raise_for_status()
    except requests.RequestException as e:
        raise SystemExit(e)

    # Find the repo root or initialize a default repot if not in a repo.
    root = repo_file_handler._maybe_get_repo_root()
    if not root:
        init_feature_repo()
        root = Path().resolve()
    repo_file_handler.ensure_prepare_repo()

    # Get user confirmation.
    repo_files = repo_file_handler.repo_files()
    if len(repo_files) > 0:
        for f in repo_files:
            printer.safe_print(f)
        confirm_or_exit("This operation may delete or modify the above files. Ok?")
        for f in repo_files:
            os.remove(f)

    # Extract the feature repo.
    with tarfile.open(fileobj=io.BytesIO(tar_response.content), mode="r|gz") as tar:
        for entry in tar:
            if os.path.isabs(entry.name) or ".." in entry.name:
                raise ValueError("Illegal tar archive entry")
            elif os.path.exists(root / Path(entry.name)):
                raise ValueError(f"tecton restore would overwrite an unexpected file: {entry.name}")
            tar.extract(entry, path=root)
    printer.safe_print("Success")


@cli.command(uses_workspace=True)
@click.option("--limit", default=10, type=int, help="Number of log entries to return.")
def log(limit):
    """View log of past `tecton apply`."""
    logRequest = GetStateUpdateLogRequest()
    logRequest.workspace = common.get_current_workspace()
    logRequest.limit = limit
    response = metadata_service.instance().GetStateUpdateLog(logRequest)
    for entry in response.entries:
        printer.safe_print(f"Commit:\t{entry.commit_id}")
        printer.safe_print(f"Author:\t{entry.applied_by}")
        printer.safe_print(f"Date:\t{entry.applied_at.ToDatetime()}")
        printer.safe_print()


@cli.command(requires_auth=False)
@click.argument("tecton_url", required=False)
@click.option(
    "--manual/--no-manual",
    default=False,
    help="Manually require user to open browser and paste login token. Needed when using the Tecton CLI in a headless environment.",
)
def login(tecton_url, manual):
    """Log in and authenticate Tecton CLI.

    The Tecton URL may be optionally passed on the command line as TECTON_URL, otherwise you will be prompted."""
    from urllib.parse import urlparse, urljoin
    from tecton import conf

    host = _cluster_url()

    if tecton_url is None:
        printer.safe_print("Enter configuration. Press enter to use current value")
        prompt = "Tecton Cluster URL [%s]: " % (host or "no current value. example: https://yourco.tecton.ai")
        new_host = input(prompt).strip()
        if new_host:
            host = new_host
    else:
        host = tecton_url
    try:
        urlparse(host)
    except:
        printer.safe_print("Tecton Cluster URL must be a valid URL")
        sys.exit(1)
    # add this check for now since it can be hard to debug if you don't specify https and API_SERVICE fails
    if host is None or not (host.startswith("https://") or host.startswith("http://localhost:")):
        if host is not None and "//" not in host:
            host = f"https://{host}"
        else:
            printer.safe_print("Tecton Cluster URL must start with https://")
            sys.exit(1)

    # get login configs
    login_configs_url = urljoin(host, "api/v1/metadata-service/get-login-configs")

    try:
        response = requests.post(login_configs_url)
        response.raise_for_status()
    except requests.RequestException as e:
        raise SystemExit(e)
    configs = response.json()["key_values"]
    cli_client_id = configs["OKTA_CLI_CLIENT_ID"]
    conf.set("CLI_CLIENT_ID", cli_client_id)
    if "ALPHA_SNOWFLAKE_COMPUTE_ENABLED" in configs:
        conf.set("ALPHA_SNOWFLAKE_COMPUTE_ENABLED", configs["ALPHA_SNOWFLAKE_COMPUTE_ENABLED"])

    flow = OktaAuthorizationFlow(hands_free=not manual)
    auth_code, code_verifier, redirect_uri = flow.get_authorization_code()
    access_token, _, refresh_token, access_token_expiration = flow.get_tokens(auth_code, code_verifier, redirect_uri)
    if not access_token:
        printer.safe_print("Unable to obtain Tecton credentials")
        sys.exit(1)

    conf.set("API_SERVICE", urljoin(host, "api"))
    # FEATURE_SERVICE and API_SERVICE are expected to have the same base URI: <host>/api
    conf.set("FEATURE_SERVICE", conf.get_or_none("API_SERVICE"))
    conf.set("CLI_CLIENT_ID", cli_client_id)
    conf.set("OAUTH_ACCESS_TOKEN", access_token)
    if refresh_token is not None:
        conf.set("OAUTH_REFRESH_TOKEN", refresh_token)
    conf.set("OAUTH_ACCESS_TOKEN_EXPIRATION", access_token_expiration)

    conf.save_tecton_configs()
    conf.save_okta_tokens(access_token, access_token_expiration, refresh_token)
    printer.safe_print(f"✅ Updated configuration at {conf._LOCAL_TECTON_CONFIG_FILE}")


@cli.command()
def freshness():
    """Feature freshness for Feature Views in all workspaces."""
    # TODO: use GetAllFeatureFreshnessRequest once we implement Chronosphere based API.
    freshness_statuses = get_all_freshness(common.get_current_workspace())
    num_fvs = len(freshness_statuses)
    if num_fvs == 0:
        printer.safe_print("No Feature Views found in this workspace.")
        return

    printer.safe_print(format_freshness_table(freshness_statuses))


@cli.command()
@click.pass_context
@click.argument("feature_view_name")
@click.option("--limit", default=100, type=int, help="Set the maximum limit of results.")
@click.option("--errors-only/--no-errors-only", default=False, help="Only show errors.")
def materialization_status(ctx, feature_view_name, limit, errors_only):
    """Show materialization status information for a FeatureView with FEATURE_VIEW_NAME in the 'prod' workspace.

    Prepend the --verbose flag for more information."""
    # Fetch FeatureView
    fvRequest = GetFeatureViewRequest()
    fvRequest.version_specifier = feature_view_name
    fvRequest.workspace = common.get_current_workspace()
    fvRequest.disable_legacy_response = True
    fvResponse = metadata_service.instance().GetFeatureView(fvRequest)
    fco_container = FcoContainer(fvResponse.fco_container)
    fv_proto = fco_container.get_single_root()
    if not fv_proto:
        printer.safe_print(f"Feature view '{feature_view_name}' not found.")
        sys.exit(1)
    fv_id = fv_proto.feature_view_id

    # Fetch Materialization Status
    statusRequest = GetMaterializationStatusRequest()
    statusRequest.feature_package_id.CopyFrom(fv_id)
    statusResponse = metadata_service.instance().GetMaterializationStatus(statusRequest)

    column_names, materialization_status_rows = format_materialization_attempts(
        statusResponse.materialization_status.materialization_attempts,
        verbose=common.get_verbose(ctx),
        limit=limit,
        errors_only=errors_only,
    )

    printer.safe_print("All the displayed times are in UTC time zone")

    # Setting `max_width=0` creates a table with an unlimited width.
    table = Displayable.from_items(headings=column_names, items=materialization_status_rows, max_width=0)
    # Align columns in the middle horizontally
    table._text_table.set_cols_align(["c" for _ in range(len(column_names))])
    printer.safe_print(table)


def main():
    try:
        cli()
    finally:
        metadata_service.close_instance()


if __name__ == "__main__":
    main()
