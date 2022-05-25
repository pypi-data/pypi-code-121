"""
Test the pip install of typed-ast.

Using any available wheel and from source.
This test is particularly important since when building from source, it needs
to link against the "embedded" python interpreter on our package.
It ensures we're properly packaging the Python headers and presenting them
when building a package which requires them.
"""
import sys

import pytest


def extra_args_ids(value):
    if not value:
        return "allow-wheel-install"
    return "build-from-source"


@pytest.mark.parametrize(
    "extra_args",
    (
        [],
        ["--no-binary", "typed-ast"],
    ),
    ids=extra_args_ids,
)
def test_typed_ast(project, extra_args):
    if extra_args and sys.platform.startswith("win"):
        pytest.skip("For now, source builds are being skipped on windows")

    ret = project.run("pip", "list")
    assert ret.exitcode == 0
    assert "typed-ast" not in ret.stdout

    ret = project.run("pip", "install", "typed-ast", *extra_args)
    assert ret.exitcode == 0
    ret = project.run("pip", "list")
    assert "typed-ast" in ret.stdout

    ret = project.run("pip", "uninstall", "-y", "typed-ast")
    assert ret.exitcode == 0
    assert "as it is not installed" not in ret.stderr

    ret = project.run("pip", "list")
    assert ret.exitcode == 0
    assert "typed-ast" not in ret.stdout
