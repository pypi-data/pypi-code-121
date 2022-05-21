from threading import RLock

from time import sleep

from pkm.api.packages.package_monitors import PackageInstallMonitoredOp
from pkm.api.pkm import pkm
from pkm.api.distributions.build_monitors import BuildPackageMonitoredOp, BuildPackageHookExecutionEvent
from pkm.resolution.resolution_monitor import DependencyResolutionMonitoredOp, DependencyResolutionIterationEvent, \
    DependencyResolutionConclusionEvent
from pkm.utils.http.http_monitors import FetchResourceMonitoredOp, FetchResourceCacheHitEvent, \
    FetchResourceDownloadStartEvent
from pkm.utils.monitors import Monitor
from pkm.utils.processes import ProcessExecutionMonitoredOp, ProcessExecutionExitEvent, ProcessExecutionOutputLineEvent
from pkm.utils.strings import startswith_any
from pkm_cli.display.display import Display
from pkm_cli.display.progress import Progress
from pkm_cli.display.spinner import Spinner

_packages_being_installed = []
_packages_being_installed_spinner = Spinner("")
_packages_being_installed_spinner_context = None
_packages_being_installed_spinner_lock = RLock()


def with_package_install(e: PackageInstallMonitoredOp):
    global _packages_being_installed_spinner_context

    def update_description():
        description = f"Installing Packages: {','.join(f'{p.name} {p.version}' for p in _packages_being_installed[:3])}"
        if (l := len(_packages_being_installed)) > 3:
            description += f" and {l - 3} more..."
        _packages_being_installed_spinner.description = description

    with _packages_being_installed_spinner_lock:
        if not _packages_being_installed:
            _packages_being_installed_spinner_context = Display.show(_packages_being_installed_spinner)
            _packages_being_installed_spinner_context.__enter__()
        _packages_being_installed.append(e.package)

        update_description()

    yield

    with _packages_being_installed_spinner_lock:
        _packages_being_installed.remove(e.package)

        if not _packages_being_installed:
            _packages_being_installed_spinner_context.__exit__(None, None, None)
        else:
            update_description()


def with_external_proc_execution(e: ProcessExecutionMonitoredOp):
    if Display.verbose:
        def on_output(oe: ProcessExecutionOutputLineEvent):
            Display.print(f"[{e.execution_name}]: {oe.line}", use_markup=False)

        def on_exit(ee: ProcessExecutionExitEvent):
            Display.print(f"[{e.execution_name}]: Ended with exit code: {ee.exit_code}", use_markup=False)

    with e.listen(**locals()), Display.show(Spinner(f"Executing process {e.execution_name}: '{' '.join(e.cmd)}'")):
        yield


def with_fetch_resource(e: FetchResourceMonitoredOp):
    if startswith_any(e.resource_name, ("matching packages for", "metadata for")):
        return  # do not monitor these resources for now..

    done: bool = False

    if Display.verbose:
        def on_cache_hit(_: FetchResourceCacheHitEvent):
            Display.print(f"{e.resource_name} found in cache, using it.")

    def on_download(download: FetchResourceDownloadStartEvent):
        if Display.verbose or download.file_size > 2_000_000:  # 2m
            def monitor():
                with Display.show(Progress(f"Fetch {e.resource_name}", download.file_size)) as progress:
                    while not done:
                        newsize = download.store_path.stat().st_size if download.store_path.exists() else 0
                        progress.completed = newsize
                        sleep(0.25)

            pkm.threads.submit(monitor)

    with e.listen(**locals()):
        try:
            yield
        finally:
            done = True


def with_dependency_resolution(e: DependencyResolutionMonitoredOp):
    progress = Progress("Dependency Resolution", 1)

    def on_iteration(ie: DependencyResolutionIterationEvent):
        progress.completed = len(ie.packages_completed)
        progress.total = len(ie.packages_requested)

    def on_conclusion(ce: DependencyResolutionConclusionEvent):
        d = {k: v for k, v in ce.decisions.items() if str(k) != 'installation-request'}
        Display.print(f"Resolved Requirements: {d}")

    with e.listen(**locals()), Display.show(progress):
        yield


def with_package_build(e: BuildPackageMonitoredOp):
    def on_build_step(bse: BuildPackageHookExecutionEvent):
        Display.print(f"executing PEP517 build hook: {bse.hook}")

    with e.listen(**locals()), Display.show(Spinner(f"building package: {e.package.name} {e.package.version}")):
        yield


_listeners = locals()


def listen(verbose: bool):
    Display.verbose = verbose
    Monitor.add_listeners(**_listeners)
