import pathlib

from tests.support.helpers import TiamatPipProject


def test_pycryptodomex(project):
    pkg_name = "cffi"

    ret = project.run("pip", "install", pkg_name)
    assert ret.exitcode == 0
    ret = project.run("pip", "list")
    assert pkg_name in ret.stdout
    assert pkg_name in project.get_store()

    ret = project.run("pip", "uninstall", "-y", pkg_name)
    assert ret.exitcode == 0

    ret = project.run("pip", "list")
    assert ret.exitcode == 0
    assert pkg_name not in ret.stdout
    assert pkg_name not in project.get_store()


def test_pycryptodomex_upgrade(tmp_path):
    """ """
    pkg_name = "pycryptodomex"
    pkg_name = "cffi"
    requirements = [
        "cffi==1.14.4",
    ]
    with TiamatPipProject(
        name=pkg_name, path=tmp_path, requirements=requirements
    ) as project:
        project.copy_generated_project_to(pathlib.Path(tmp_path).resolve())

        code = """
        from cffi import FFI
        FFI()
        """

        ret = project.run_code(code)
        assert ret.exitcode == 0

        ret = project.run("pip", "install", "-U", pkg_name)
        assert ret.exitcode == 0
        ret = project.run("pip", "list")
        store = project.get_store()
        assert pkg_name in store

        ret = project.run_code(code)
        assert ret.exitcode == 0
