def test_pip_list(project, base_requirement):
    """
    Test that we can list packages.
    """
    installed_packages = project.run("pip", "list")
    assert base_requirement not in installed_packages.stdout


def test_pip_list_frozen(project, base_requirement):
    """
    Test that we can list the packages frozen into the binary.
    """
    frozen_packages = project.run("pip", "frozen")
    assert base_requirement in frozen_packages.stdout
