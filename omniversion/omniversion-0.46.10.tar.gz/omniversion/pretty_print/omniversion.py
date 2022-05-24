"""Pretty-printing for omniversion model class"""
from omniversion import Omniversion
from omniversion.pretty_print.helpers import multiline_indent, header


def _pretty_print_omniversion(omniversion: Omniversion, recursive_format) -> str:
    def host_summary(host, dependencies):
        return f"{recursive_format(host)}\n{multiline_indent(recursive_format(dependencies))}\n\n"

    return "\n".join([
        header('Data sources'),
        multiline_indent(recursive_format(omniversion.sources)),
        header('Dependency count'),
        *[multiline_indent(host_summary(host, host.packages.list())) for host in omniversion.hosts],
        header('Available updates'),
        *[multiline_indent(host_summary(host, host.packages.outdated())) for host in omniversion.hosts],
        header('Security audit'),
        *[multiline_indent(host_summary(host, host.packages.audit())) for host in omniversion.hosts],
    ])
