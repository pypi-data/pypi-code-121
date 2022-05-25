"""
Test installing pyOpenSSL.

The reason for this test is because the package is CamelCased
and we need to confirm proper behavior with such named packages
"""


def test_pyopenssl(project):
    """
    Test pacakge name canonicalization.

    The actual package name is pyOpenSSL, however we're using pyopenssl
    to confirm we can properly resolve package names like pip does.
    """
    pkg_name = "pyopenssl"
    real_package_name = "pyOpenSSL"

    ret = project.run("pip", "install", pkg_name)
    assert ret.exitcode == 0
    ret = project.run("pip", "list")
    assert real_package_name in ret.stdout
    assert pkg_name in project.get_store()
    assert real_package_name in project.get_store()

    ret = project.run("pip", "uninstall", "-y", pkg_name)
    assert ret.exitcode == 0
    assert "as it is not installed" not in ret.stderr

    ret = project.run("pip", "list")
    assert ret.exitcode == 0
    assert real_package_name not in ret.stdout
    assert pkg_name not in ret.stdout
    assert real_package_name not in project.get_store()
    assert pkg_name not in project.get_store()
