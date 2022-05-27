"""
Setup repro environment.

Downloads and installs particular mongodb versions (each binary is renamed
to include its version) into an install directory and symlinks the binaries
with versions to another directory. This script supports community and
enterprise builds.
"""
import argparse
import logging
import os
import re
import sys
from typing import List, NamedTuple, Optional

import inject
import structlog
from evergreen import EvergreenApi

from db_contrib_tool.clients.download_client import DownloadError
from db_contrib_tool.clients.file_service import FileService
from db_contrib_tool.clients.resmoke_proxy import ResmokeProxy
from db_contrib_tool.config import (
    SETUP_REPRO_ENV_CONFIG,
    SETUP_REPRO_ENV_CONFIG_FILE,
    WINDOWS_BIN_PATHS_FILE,
    DownloadTarget,
    SetupReproEnvConfig,
)
from db_contrib_tool.plugin import PluginInterface, Subcommand, SubcommandResult
from db_contrib_tool.services.evergreen_service import EvergreenService
from db_contrib_tool.setup_repro_env.artifact_discovery_service import (
    ArtifactDiscoveryService,
    RequestTarget,
    RequestType,
)
from db_contrib_tool.setup_repro_env.download_service import (
    ArtifactDownloadService,
    DownloadOptions,
)
from db_contrib_tool.utils import evergreen_conn, is_windows

SUBCOMMAND = "setup-repro-env"
BINARY_ARTIFACT_NAME = "Binaries"
KNOWN_BRANCHES = {"master"}
RELEASE_VERSION_RE = re.compile(r"^\d+\.\d+$")
PATCH_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+")
BRANCH_RE = re.compile(r"^v\d+\.\d+")
EXTERNAL_LOGGERS = [
    "evergreen",
    "github",
    "inject",
    "segment",
    "urllib3",
]

LOGGER = structlog.getLogger(__name__)


class SetupReproEnvError(Exception):
    """Errors in setup_repro_env.py.

    The base class of exceptions for this file/subcommand.
    """

    pass


def setup_logging(debug=False):
    """Enable logging."""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        format="[%(asctime)s - %(name)s - %(levelname)s] %(message)s",
        level=log_level,
        stream=sys.stdout,
    )
    for logger in EXTERNAL_LOGGERS:
        logging.getLogger(logger).setLevel(logging.WARNING)
    structlog.configure(logger_factory=structlog.stdlib.LoggerFactory())


class SetupReproParameters(NamedTuple):
    """
    Parameters describing how a repro environment should be setup.

    * edition: MongoDB edition to download.
    * platform: Target platform to download.
    * architecture: Target architecture to download.
    * variant: Build Variant to download from.

    * versions: List of items to download.
    * install_last_lts: If True download last LTS version of mongo.
    * install_last_continuous: If True download last continuous version of mongo.
    * ignore_failed_push: Download version even if the push task failed.
    * fallback_to_master: Should the latest master be downloaded if the version doesn't exist.

    * evg_version_file: Write which evergreen version were downloaded from to this file.

    * download_options: Options specifying how downloads should occur.
    """

    edition: str
    platform: str
    architecture: str
    variant: str

    versions: List[str]
    install_last_lts: bool
    install_last_continuous: bool
    ignore_failed_push: bool
    fallback_to_master: bool

    evg_version_file: Optional[str]

    download_options: DownloadOptions

    def get_download_target(self, platform: Optional[str] = None) -> DownloadTarget:
        """
        Get the download target to use based on these parameters.

        :param platform: Override the platform with this platform.
        :return: Download target specified by this options.
        """
        platform = platform if platform is not None else self.platform
        return DownloadTarget(
            edition=self.edition, platform=platform, architecture=self.architecture
        )


class SetupReproOrchestrator:
    """Orchestrator for setting up repro environments."""

    @inject.autoparams()
    def __init__(
        self,
        evg_service: EvergreenService,
        resmoke_proxy: ResmokeProxy,
        artifact_download_service: ArtifactDownloadService,
        artifact_discovery_service: ArtifactDiscoveryService,
        file_service: FileService,
    ) -> None:
        """
        Initialize the orchestrator.

        :param evg_service: Service for working with evergreen.
        :param resmoke_proxy: Proxy for working with resmoke.
        :param artifact_download_service: Service to download artifacts.
        :param artifact_discovery_service: Service to find artifacts.
        :param file_service: Service to work with the filesystem.
        """
        self.evg_service = evg_service
        self.resmoke_proxy = resmoke_proxy
        self.artifact_download_service = artifact_download_service
        self.artifact_discovery_service = artifact_discovery_service
        self.file_service = file_service

    def interpret_request(self, request: str) -> RequestTarget:
        """
        Translate the request from the user into an item we can understand.

        :param request: Request from user.
        :return: Targeted request to download.
        """
        if request in KNOWN_BRANCHES or BRANCH_RE.match(request):
            return RequestTarget(RequestType.GIT_BRANCH, request)

        if RELEASE_VERSION_RE.match(request):
            return RequestTarget(RequestType.MONGO_RELEASE_VERSION, request)

        if PATCH_VERSION_RE.match(request):
            return RequestTarget(RequestType.MONGO_PATCH_VERSION, request)

        if self.evg_service.query_task_existence(request):
            return RequestTarget(RequestType.EVG_TASK, request)

        if self.evg_service.query_version_existence(request):
            return RequestTarget(RequestType.EVG_VERSION, request)

        return RequestTarget(RequestType.GIT_COMMIT, request)

    def interpret_requests(
        self, request_list: List[str], last_lts: bool, last_continuous: bool
    ) -> List[RequestTarget]:
        """
        Translate all the requests from the user into items we can understand.

        :param request_list: Requests from user.
        :param last_lts: Should 'last lts' version be included.
        :param last_continuous: Should the 'last continuous' version be included.
        :return: List of targeted request to download.
        """
        requests = [self.interpret_request(request) for request in request_list]
        if last_lts or last_continuous:
            requests.extend(self._get_release_versions(last_lts, last_continuous))

        return requests

    def _get_release_versions(
        self, install_last_lts: Optional[bool], install_last_continuous: Optional[bool]
    ) -> List[RequestTarget]:
        """
        Create a list of multiversion versions that should be included.

        :param install_last_lts: True if the last LTS version should be included.
        :param install_last_continuous: True if the last continuous version should be included.
        :return: List of which multiversion versions should be included.
        """
        multiversionconstants = self.resmoke_proxy.get_multiversion_constants()
        releases = {
            multiversionconstants.last_lts_fcv: install_last_lts,
            multiversionconstants.last_continuous_fcv: install_last_continuous,
        }
        LOGGER.debug("LTS and continuous release inclusions", releases=releases)
        out = {
            RequestTarget.previous_release(version)
            for version, requested in releases.items()
            if requested
        }

        return list(out)

    @staticmethod
    def _get_bin_suffix(version: str, evg_project_id: str) -> str:
        """Get the multiversion bin suffix from the evergreen project ID."""
        if re.match(r"(\d+\.\d+)", version):
            # If the cmdline version is already a semvar, just use that.
            return version
        elif evg_project_id in ("mongodb-mongo-master", "mongodb-mongo-master-nightly"):
            # If the version is not a semvar and the project is the master waterfall,
            # we can't add a suffix.
            return ""
        else:
            # Use the Evergreen project ID as fallback.
            return re.search(r"(\d+\.\d+$)", evg_project_id).group(0)

    def execute(self, setup_repro_params: SetupReproParameters) -> bool:
        """Execute setup repro env mongodb."""
        request_list = self.interpret_requests(
            setup_repro_params.versions,
            setup_repro_params.install_last_lts,
            setup_repro_params.install_last_continuous,
        )

        downloaded_versions = []
        failed_requests = []
        link_directories = []

        download_target = setup_repro_params.get_download_target()
        LOGGER.info("Search criteria", search_criteria=download_target)

        for request in request_list:
            LOGGER.info("Setting up request", request=request)
            LOGGER.info("Fetching download URLs from Evergreen")

            try:
                urls_info = self.artifact_discovery_service.find_artifacts(
                    request,
                    setup_repro_params.variant,
                    download_target,
                    setup_repro_params.ignore_failed_push,
                    setup_repro_params.fallback_to_master,
                )

                if urls_info is None:
                    failed_requests.append(request)
                    LOGGER.warning("Unable to find artifacts for request", request=request)
                    continue

                bin_suffix = self._get_bin_suffix(request.identifier, urls_info.project_identifier)
                linked_dir = self.artifact_download_service.download_and_extract(
                    urls_info.urls,
                    bin_suffix,
                    urls_info.evg_version_id,
                    setup_repro_params.download_options,
                )
                if linked_dir:
                    link_directories.append(linked_dir)
                downloaded_versions.append(urls_info.evg_version_id)
                LOGGER.info("Setup request completed", request=request)
            except (
                evergreen_conn.EvergreenConnError,
                DownloadError,
                SetupReproEnvError,
            ):
                failed_requests.append(request)
                LOGGER.error("Setup request failed", request=request, exc_info=True)

        if is_windows():
            self.file_service.write_windows_install_paths(WINDOWS_BIN_PATHS_FILE, link_directories)

        if setup_repro_params.evg_version_file is not None:
            self.file_service.append_lines_to_file(
                setup_repro_params.evg_version_file, downloaded_versions
            )
            LOGGER.info(
                "Finished writing downloaded Evergreen versions",
                target_file=os.path.abspath(setup_repro_params.evg_version_file),
            )

        if len(downloaded_versions) < len(request_list):
            LOGGER.error("Some requests were not able to setup.", failed_requests=failed_requests)
            return False
        LOGGER.info("Downloaded versions", request_list=request_list)
        return True


class SetupReproEnv(Subcommand):
    """Main class for the setup repro environment subcommand."""

    def __init__(
        self,
        download_options,
        install_dir="",
        link_dir="",
        mv_platform=None,
        edition=None,
        architecture=None,
        versions=None,
        variant=None,
        install_last_lts=None,
        install_last_continuous=None,
        evergreen_config=None,
        debug=None,
        ignore_failed_push=False,
        evg_versions_file=None,
        resmoke_cmd=None,
        fallback_to_master=False,
    ):
        """Initialize."""
        setup_logging(debug)

        download_options = DownloadOptions(
            download_binaries=download_options.download_binaries,
            download_symbols=download_options.download_symbols,
            download_artifacts=download_options.download_artifacts,
            download_python_venv=download_options.download_python_venv,
            install_dir=os.path.abspath(install_dir),
            link_dir=os.path.abspath(link_dir),
        )

        self.setup_repro_params = SetupReproParameters(
            edition=edition.lower() if edition else None,
            platform=mv_platform.lower() if mv_platform else None,
            architecture=architecture.lower() if architecture else None,
            variant=variant.lower() if variant else None,
            versions=versions,
            install_last_lts=install_last_lts,
            install_last_continuous=install_last_continuous,
            ignore_failed_push=ignore_failed_push,
            fallback_to_master=fallback_to_master,
            download_options=download_options,
            evg_version_file=evg_versions_file,
        )

        self.evg_api = evergreen_conn.get_evergreen_api(evergreen_config)
        self.resmoke_cmd = resmoke_cmd

    def execute(self):
        """Execute setup repro env mongodb."""

        def dependencies(binder: inject.Binder) -> None:
            """Define dependencies for execution."""
            binder.bind(SetupReproEnvConfig, SETUP_REPRO_ENV_CONFIG)
            binder.bind(EvergreenApi, self.evg_api)
            binder.bind(ResmokeProxy, ResmokeProxy.with_cmd(self.resmoke_cmd))

        inject.configure(dependencies)

        setup_repro_orchestrator = inject.instance(SetupReproOrchestrator)

        success = setup_repro_orchestrator.execute(self.setup_repro_params)
        if success:
            return SubcommandResult.SUCCESS
        return SubcommandResult.FAIL


class _DownloadOptions(object):
    def __init__(self, db, ds, da, dv):
        self.download_binaries = db
        self.download_symbols = ds
        self.download_artifacts = da
        self.download_python_venv = dv


class SetupReproEnvPlugin(PluginInterface):
    """Integration point for setup-repro-env."""

    DEFAULT_INSTALL_DIR = os.path.join(os.getcwd(), "build", "multiversion_bin")
    DEFAULT_LINK_DIR = os.getcwd()
    DEFAULT_WITH_ARTIFACTS_INSTALL_DIR = os.path.join(os.getcwd(), "repro_envs")
    DEFAULT_WITH_ARTIFACTS_LINK_DIR = os.path.join(
        DEFAULT_WITH_ARTIFACTS_INSTALL_DIR, "multiversion_bin"
    )

    @classmethod
    def _update_args(cls, args):
        """Update command-line arguments."""
        if not args.versions:
            args.install_last_lts = True
            args.install_last_continuous = True

        if args.download_artifacts:
            args.install_dir = cls.DEFAULT_WITH_ARTIFACTS_INSTALL_DIR
            args.link_dir = cls.DEFAULT_WITH_ARTIFACTS_LINK_DIR

    def parse(self, subcommand, parser, parsed_args, **kwargs):
        """Parse command-line arguments."""
        if subcommand != SUBCOMMAND:
            return None

        # Shorthand for brevity.
        args = parsed_args
        self._update_args(args)

        download_options = _DownloadOptions(
            db=(not args.skip_binaries),
            ds=args.download_symbols,
            da=args.download_artifacts,
            dv=args.download_python_venv,
        )

        if download_options.download_binaries and args.link_dir is None:
            raise ValueError("link_dir must be specified if downloading binaries")

        return SetupReproEnv(
            install_dir=args.install_dir,
            link_dir=args.link_dir,
            mv_platform=args.platform,
            edition=args.edition,
            architecture=args.architecture,
            versions=args.versions,
            install_last_lts=args.install_last_lts,
            variant=args.variant,
            install_last_continuous=args.install_last_continuous,
            download_options=download_options,
            evergreen_config=args.evergreen_config,
            ignore_failed_push=(not args.require_push),
            evg_versions_file=args.evg_versions_file,
            debug=args.debug,
            resmoke_cmd=args.resmoke_cmd,
            fallback_to_master=args.fallback_to_master,
        )

    @classmethod
    def _add_args_to_parser(cls, parser):
        parser.add_argument(
            "-i",
            "--installDir",
            dest="install_dir",
            default=cls.DEFAULT_INSTALL_DIR,
            help=f"Directory to install the download archive,"
            f" [default: %(default)s, if `--downloadArtifacts` is passed: {cls.DEFAULT_WITH_ARTIFACTS_INSTALL_DIR}]",
        )
        parser.add_argument(
            "-l",
            "--linkDir",
            dest="link_dir",
            default=cls.DEFAULT_LINK_DIR,
            help=f"Directory to contain links to all binaries for each version in the install directory,"
            f" [default: %(default)s, if `--downloadArtifacts` is passed: {cls.DEFAULT_WITH_ARTIFACTS_LINK_DIR}]",
        )
        editions = ("base", "enterprise", "targeted")
        parser.add_argument(
            "-e",
            "--edition",
            dest="edition",
            choices=editions,
            default="enterprise",
            help="Edition of the build to download, [default: %(default)s].",
        )
        parser.add_argument(
            "-p",
            "--platform",
            dest="platform",
            help="Platform to download. "
            f"Available platforms can be found in {SETUP_REPRO_ENV_CONFIG_FILE}.",
        )
        parser.add_argument(
            "-a",
            "--architecture",
            dest="architecture",
            default="x86_64",
            help="Architecture to download, [default: %(default)s]. Examples include: "
            "'arm64', 'ppc64le', 's390x' and 'x86_64'.",
        )
        parser.add_argument(
            "-v",
            "--variant",
            dest="variant",
            default=None,
            help="Specify a variant to use, which supersedes the --platform, --edition and"
            " --architecture options.",
        )
        parser.add_argument(
            "versions",
            nargs="*",
            help="Accepts binary versions, `master`, full git commit hashes, evergreen version ids,"
            " evergreen task ids. Binary version examples: <major.minor>, 4.2, 4.4, 5.0 etc. If no"
            " version is specified the last LTS and the last continuous versions will be installed.",
        )
        parser.add_argument(
            "--installLastLTS",
            dest="install_last_lts",
            action="store_true",
            help="If specified, the last LTS version will be installed",
        )
        parser.add_argument(
            "--installLastContinuous",
            dest="install_last_continuous",
            action="store_true",
            help="If specified, the last continuous version will be installed",
        )
        parser.add_argument(
            "-sb",
            "--skipBinaries",
            dest="skip_binaries",
            action="store_true",
            help="whether to skip downloading binaries.",
        )
        parser.add_argument(
            "-ds",
            "--downloadSymbols",
            dest="download_symbols",
            action="store_true",
            help="whether to download debug symbols.",
        )
        parser.add_argument(
            "-da",
            "--downloadArtifacts",
            dest="download_artifacts",
            action="store_true",
            help="whether to download artifacts.",
        )
        parser.add_argument(
            "-dv",
            "--downloadPythonVenv",
            dest="download_python_venv",
            action="store_true",
            help="whether to download python venv.",
        )
        parser.add_argument(
            "-ec",
            "--evergreenConfig",
            dest="evergreen_config",
            help="Location of evergreen configuration file. If not specified it will look "
            f"for it in the following locations: {evergreen_conn.EVERGREEN_CONFIG_LOCATIONS}",
        )
        parser.add_argument(
            "-d",
            "--debug",
            dest="debug",
            action="store_true",
            help="Set DEBUG logging level.",
        )
        parser.add_argument(
            "-rp",
            "--require-push",
            dest="require_push",
            action="store_true",
            help="Require the push task to be successful for assets to be downloaded",
        )
        parser.add_argument(
            "--resmokeCmd",
            dest="resmoke_cmd",
            default="python buildscripts/resmoke.py",
            help="Command to invoke resmoke.py",
        )
        parser.add_argument(
            "--fallbackToMaster",
            dest="fallback_to_master",
            action="store_true",
            help=(
                "Fallback to downloading the latest binaries from master if the requested "
                "version is not found (Only application for mongo versions)"
            ),
        )
        # Hidden flag to write out the Evergreen versions of the downloaded binaries.
        parser.add_argument(
            "--evgVersionsFile", dest="evg_versions_file", default=None, help=argparse.SUPPRESS
        )

    def add_subcommand(self, subparsers):
        """Create and add the parser for the subcommand."""
        parser = subparsers.add_parser(SUBCOMMAND, help=__doc__)
        self._add_args_to_parser(parser)
