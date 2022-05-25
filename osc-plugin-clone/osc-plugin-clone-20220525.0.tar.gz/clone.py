#!/usr/bin/python

import osc.cmdln as cmdln

import osc_plugin_clone


@cmdln.option(
    '--build-suffix', dest='build_suffix',
    help='build suffix to use instead of automatically incremented one',
)
@cmdln.option(
    '--preserve-metadata', dest='keep_metadata', action='store_true',
    help='do not modify the project and repository references in the metadata',
)
@cmdln.option(
    '--copy-packages-only', dest='copy_only', action='store_true',
    help='do not copy the metadata or the project configuration',
)
@cmdln.option(
    '--no-verify', dest='no_verify', action='store_true',
    help='do not verify the correctness of copies',
)
def do_clone(self, subcmd, opts, sourceprj, destprj):
    """${cmd_name}: Create a clone of a project at an OBS server.

    Create a project, if necessary, copy and mangle the metadata and the
    project configuration, copy all packages.

    This command modifies the metadata to refer to corresponding projects and
    repositories in the target namespace unless asked not to, so if the projects
    or repositories do not exist yet, it will fail at the last stage.

    ${cmd_usage}
    ${cmd_option_list}
    """
    osc_plugin_clone.do_clone(self, subcmd, opts, sourceprj, destprj)


@cmdln.option(
    '--build-suffix', dest='build_suffix',
    help='build suffix to use instead of automatically incremented one',
)
@cmdln.option(
    '--preserve-metadata', dest='keep_metadata', action='store_true',
    help='do not modify the project and repository references in the metadata',
)
@cmdln.option(
    '--no-verify', dest='no_verify', action='store_true',
    help='do not verify the correctness of copies',
)
def do_fork(self, subcmd, opts, sourcedistro, destdistro):
    """${cmd_name}: Fork a distribution at an OBS server.

    Create clones of all components of the distribution, copy and mangle
    the metadata and the project configurations.

    ${cmd_usage}
    ${cmd_option_list}
    """
    osc_plugin_clone.do_fork(self, subcmd, opts, sourcedistro, destdistro)
