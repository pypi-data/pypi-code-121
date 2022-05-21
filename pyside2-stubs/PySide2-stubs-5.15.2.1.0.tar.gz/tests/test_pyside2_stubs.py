import pathlib

from mypy import api

# disabled for now
def XXtest_pyside2_stubs() -> None:
    """Run mypy over example files."""
    pyside2_stubs_dir = pathlib.Path(__file__).parent.parent / 'PySide2-stubs'
    # stdout, stderr, exitcode = api.run([str(pyside2_stubs_dir) ,'--show-error-codes'])
    stdout, stderr, exitcode = api.run([
        # pyside2_stubs_dir,
        str(pyside2_stubs_dir / 'QtWidgets.pyi'),
        '--show-error-codes',
    ])
    if stdout:
        print(stdout)
    if stderr:
        print(stderr)

    assert stdout.startswith("Success: no issues found")
    assert not stderr
    assert exitcode == 0


