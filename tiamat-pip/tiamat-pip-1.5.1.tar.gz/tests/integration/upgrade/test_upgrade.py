def test_pip_upgrade(project, initial_jinja_version, upgraded_jinja_version):
    """
    Test that we can upgrade a package which was shipped with the tiamat package.
    """
    code = """
    import sys
    import jinja2
    sys.stdout.write(jinja2.__version__)
    sys.stdout.flush()
    """
    installed_packages = project.get_installed_packages(include_frozen=True)
    assert "jinja2" in installed_packages
    assert installed_packages["jinja2"] == initial_jinja_version

    ret = project.run_code(code)
    assert ret.exitcode == 0
    assert ret.stdout.strip() == initial_jinja_version

    ret = project.run("pip", "install", f"jinja2=={upgraded_jinja_version}")
    assert ret.exitcode == 0
    installed_packages = project.get_installed_packages()
    assert "jinja2" in installed_packages
    assert installed_packages["jinja2"] == upgraded_jinja_version

    installed_packages = project.get_installed_packages(include_frozen=True)
    assert "jinja2" in installed_packages
    assert installed_packages["jinja2"] == upgraded_jinja_version

    ret = project.run_code(code)
    assert ret.exitcode == 0
    assert ret.stdout.strip() == upgraded_jinja_version
