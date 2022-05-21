import argparse
import os
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List, Optional, Dict

import sys

from pkm.api.dependencies.dependency import Dependency
from pkm.api.environments.environment import Environment
from pkm.api.environments.environments_zoo import EnvironmentsZoo
from pkm.api.packages.package_installation import PackageInstallationTarget
from pkm.api.pkm import pkm, HasAttachedRepository
from pkm.api.projects.project import Project
from pkm.api.projects.project_group import ProjectGroup
from pkm.api.repositories.repositories_configuration import RepositoryInstanceConfig
from pkm.utils.commons import UnsupportedOperationException
from pkm.utils.processes import execvpe
from pkm.utils.resources import ResourcePath
from pkm_cli import cli_monitors
from pkm_cli.context import Context
from pkm_cli.display.display import Display
from pkm_cli.reports.added_repositories_report import AddedRepositoriesReport
from pkm_cli.reports.environment_report import EnvironmentReport
from pkm_cli.reports.installed_repositories_report import InstalledRepositoriesReport
from pkm_cli.reports.package_report import PackageReport
from pkm_cli.reports.project_report import ProjectReport
from pkm_cli.scaffold.engine import ScaffoldingEngine
from pkm_cli.utils.clis import command, Arg, create_args_parser, Command, with_extras


def _cli_container() -> PackageInstallationTarget:
    global_env = Environment.current()
    if pkm_container := global_env.app_containers.container_of('pkm-cli'):
        return pkm_container.installation_target
    return global_env.installation_target


@command('pkm repos install', Arg(["-u", "--update"], action="store_true"), Arg('names', nargs=argparse.REMAINDER))
def install_repos(args: Namespace):
    if not args.global_context:
        raise UnsupportedOperationException("repository installation is only supported in global context (add -g)")

    updates = args.names if args.update else []
    _cli_container().install([Dependency.parse(it) for it in args.names], updates=updates)


@command('pkm repos uninstall', Arg('names', nargs=argparse.REMAINDER))
def uninstall_repo(args: Namespace):
    if not args.global_context:
        raise UnsupportedOperationException("repository uninstallation is only supported in global context (add -g)")

    _cli_container().uninstall(args.names)


@command('pkm repos show installed')
def show_installed_repositories(_: Namespace):
    InstalledRepositoriesReport().display()


@command(
    'pkm repos add',
    Arg("name"),
    Arg("type", action=with_extras()),
    Arg(['-b', '--bind-only'], action="store_true", required=False))
def add_repo(args: Namespace):
    def add(with_repo: HasAttachedRepository):
        with_repo.repository_management.add_repository(
            args.name, args.type, getattr(args, 'type_extras', {}), args.bind_only)

    on_environment, on_project, on_project_group, = add, add, add
    Context.of(args).run(**locals())


@command('pkm repos remove', Arg("name"))
def remove_repo(args: Namespace):
    def rm(with_repo: HasAttachedRepository):
        with_repo.repository_management.remove_repository(args.name)

    on_environment, on_project, on_project_group, = rm, rm, rm
    Context.of(args).run(**locals())


@command('pkm repos show added')
def show_added_repositories(args: Namespace):
    def show(with_repo: HasAttachedRepository):
        AddedRepositoriesReport(with_repo).display()

    on_environment, on_project, on_project_group, = show, show, show
    Context.of(args).run(**locals())


@command('pkm run', Arg('cmd', nargs=argparse.REMAINDER))
def run(args: Namespace):
    if not args.cmd:
        raise UnsupportedOperationException("command is required to be executed")

    def on_environment(env: Environment):
        with env.activate():
            sys.exit(execvpe(args.cmd[0], args.cmd[1:], os.environ))

    def on_project(project: Project):
        on_environment(project.attached_environment)

    Context.of(args).run(**locals())


# noinspection PyUnusedLocal
@command('pkm shell', Arg(["-e", '--execute'], required=False, nargs=argparse.REMAINDER))
def shell(args: Namespace):
    def on_environment(env: Environment):
        with env.activate():
            if execution := args.execute:
                sys.exit(execvpe(execution[0], execution[1:], os.environ))

            import xonsh.main
            sys.exit(xonsh.main.main([]))

    def on_project(project: Project):
        on_environment(project.attached_environment)

    def on_free_context():
        on_environment(Environment.current())

    Context.of(args).run(**locals())


# noinspection PyUnusedLocal
@command('pkm build')
def build(args: Namespace):
    def on_project(project: Project):
        if any((u := d.required_url()) and u.protocol == 'file'
               for d in (project.config.project.dependencies or [])):
            Display.print("[orange1]Warning[/] you are building a project that depends on packages located in your "
                          "file system, [red]publishing this project will result in unusable package[/]")
        project.build()

    def on_project_group(project_group: ProjectGroup):
        project_group.build_all()

    Context.of(args).run(**locals())


@command(
    'pkm vbump',
    Arg('particle', choices=['major', 'minor', 'patch', 'a', 'b', 'rc'], nargs='?', default='patch'))
def vbump(args: Namespace):
    def on_project(project: Project):
        new_version = project.bump_version(args.particle)
        Display.print(f"Version bumped to: {new_version}")

    Context.of(args).run(**locals())


@command(
    'pkm install',
    Arg(["-o", "--optional"], help="optional group to use (only for projects)"),
    Arg(["-f", "--force"], action='store_true', help="forcefully remove and reinstall the given pacakges"),
    Arg(["-a", "--app"], action='store_true', help="install package in containerized application mode"),
    Arg(["-u", "--update"], action='store_true', help="update the given packages if already installed"),
    Arg(["-m", "--mode"], required=False, default='editable', choices=['editable', 'copy'],
        help="choose the installation mode for the requested packages."),
    Arg(['-s', '--site'], required=False, choices=['user', 'system'],
        help="applicable for global-context, which site to use - defaults to 'user'"),
    Arg(['-r', '--repo'], required=False,
        help="bind the given packages to a specific repositry by name, use 'default' to remove previous binding"),
    Arg(['-R', '--unnamed-repo'], required=False, action=with_extras(),
        help="bind the given packages to a new unnamed repositry given its configuration"),
    Arg('packages', nargs=argparse.REMAINDER, help="the packages to install (support pep508 dependency syntax)"))
def install(args: Namespace):
    """
    install packages under the current context
    """

    dependencies = [Dependency.parse(it) for it in args.packages]
    editable = args.mode == 'editable'

    def register_repo_bindings(contex: HasAttachedRepository):
        if repo := args.repo:
            repo = None if repo == 'default' else repo
            if any(contex.repository_management.configuration.package_bindings.get(d.package_name) != repo
                   for d in dependencies):
                contex.repository_management.register_bindings([d.package_name for d in dependencies], repo)
                args.force = True
        elif repo_type := args.unnamed_repo:
            print("DBG: recognized unnamed repo option")
            instance_config = RepositoryInstanceConfig(repo_type, None, None, getattr(args, 'unnamed_repo_extras', {}))
            contex.repository_management.register_bindings([d.package_name for d in dependencies], instance_config)
            args.force = True

    def force(target: PackageInstallationTarget):
        if args.force:
            for d in dependencies:
                target.force_remove(d.package_name)

    def on_project(project: Project):
        register_repo_bindings(project)
        if args.app:
            raise UnsupportedOperationException("application install as project dependency is not supported")

        force(project.attached_environment.installation_target)
        project.dev_install(dependencies, optional_group=args.optional, update=args.update, editable=editable)

    def on_environment(env: Environment):
        nonlocal dependencies
        register_repo_bindings(env)
        if args.optional:
            raise UnsupportedOperationException("optional dependencies are only supported inside projects")

        if dependencies:
            target = env.installation_target
            if args.app:
                target = env.app_containers.install(
                    dependencies[0], editable=editable, update=args.update and len(dependencies) == 1)
                dependencies = dependencies[1:]

            if dependencies:
                force(target)
                updates = [d.package_name for d in dependencies] if args.update else None
                editables = {d.package_name: editable for d in dependencies}
                target.install(dependencies, updates=updates, editables=editables)

    Context.of(args).run(**locals())


@command('pkm uninstall', Arg(["-a", "--app"], action='store_true', help="remove containerized packages"),
         Arg(["-f", "--force"], action="store_true",
             help="remove the requested packages even if they are dependant of other packages, "
                  "will not remove any other packages or update pyproject"),
         Arg('package_names', nargs=argparse.REMAINDER, help="the packages to remove"))
def remove(args: Namespace):
    """
    remove packages from the current context
    """

    if not (package_names := args.package_names):
        raise ValueError("no package names are provided to be removed")

    app_install = bool(args.app)

    def _remove(target: PackageInstallationTarget, packages: List[str] = package_names):
        if args.force:
            for package in packages:
                target.force_remove(package)
        else:
            target.uninstall(packages)

    def on_project(project: Project):
        if app_install:
            raise UnsupportedOperationException("application install/remove as project dependency is not supported")

        if args.force:
            _remove(project.attached_environment.installation_target)
        else:
            project.dev_remove(package_names)

    def on_environment(env: Environment):
        if app_install:
            if container := env.installation_target.app_containers.container_of(package_names[0]):
                if len(package_names) == 1:
                    container.uninstall()
                else:
                    _remove(container.installation_target, package_names[1:])
        else:
            _remove(env.installation_target, package_names)

    Context.of(args).run(**locals())


@command('pkm publish', Arg('repo', action=with_extras()), Arg(['-s', '--save'], action='store_true'))
def publish(args: Namespace):
    try:
        from pkm_cli.auth.publish_auth_store import PublishAuthenticationStore
        publish_auth = PublishAuthenticationStore()
    except Exception as e:
        Display.print(f"[red]Could not load publish authentication store: {e}[/red]")
        publish_auth = None

    def on_project(project: Project):
        if not project.is_built_in_default_location():
            project.build()

        if not (publisher := project.repository_management.publisher_for(args.repo)):
            raise UnsupportedOperationException(f"repository: {args.repo} does not support publishing")

        auth_args: Dict[str, str] = {}
        if hasattr(args, 'repo_extras'):
            auth_args = args.repo_extras
        elif publisher.requires_authentication():
            if not publish_auth or not publish_auth.is_configuration_exists() \
                    or not (auth_args := publish_auth.auth_args_for(args.repo)):
                raise UnsupportedOperationException("authentication required")

        project.publish(publisher, auth_args)
        if args.save and publish_auth:
            publish_auth.add_auth_args(args.repo, auth_args)

    Context.of(args).run(**locals())


@command('pkm new', Arg('template'), Arg('template_args', nargs=argparse.REMAINDER))
def new(args: Namespace):
    ScaffoldingEngine().render(
        ResourcePath('pkm_cli.scaffold', f"new_{args.template}.tar.gz"), Path.cwd(), args.template_args)


@command('pkm show context')
def show_context(args: Namespace):
    def on_project(project: Project):
        ProjectReport(project).display()

    def on_environment(env: Environment):
        EnvironmentReport(env).display()

    Context.of(args).run(**locals())


@command('pkm show package', Arg('dependency'))
def show_package(args: Namespace):
    def on_project(project: Project):
        PackageReport(project, args.dependency).display()

    def on_environment(env: Environment):
        PackageReport(env, args.dependency).display()

    Context.of(args).run(**locals())


# noinspection PyUnusedLocal
@command('pkm clean cache')
def clean_cache(args: Namespace):
    pkm.clean_cache()


# noinspection PyUnusedLocal
@command('pkm clean shared')
def clean_shared(args: Namespace):
    def on_env_zoo(env_zoo: EnvironmentsZoo):
        env_zoo.clean_unused_shared()

    Context.of(args).run(**locals())


@command('pkm clean dist', Arg(["--all", "-a"], action="store_true"))
def clean_dist(args: Namespace):
    def on_project(project: Project):
        keep_versions = [project.version] if not args.all else None
        project.directories.clean_dist(keep_versions)

    Context.of(args).run(**locals())


def main(args: Optional[List[str]] = None):
    args = args or sys.argv[1:]

    def customize_command(cmd: ArgumentParser, _: Command):
        cmd.add_argument('-v', '--verbose', action='store_true', help="run with verbose output")
        cmd.add_argument('-c', '--context', help="path to the context to run this command under")
        cmd.add_argument('-g', '--global-context', action='store_true', help="use the global environment context")

    pkm_parser = create_args_parser(
        "pkm - python package management for busy developers", globals().values(), customize_command)

    pargs = pkm_parser.parse_args(args)
    cli_monitors.listen('verbose' in pargs and pargs.verbose)
    if 'func' in pargs:
        pargs.func(pargs)
    else:
        pkm_parser.print_help()

    Display.print("")


if __name__ == "__main__":
    main()
