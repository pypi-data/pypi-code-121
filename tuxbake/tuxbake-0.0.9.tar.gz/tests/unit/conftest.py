import os
import subprocess
import pytest


oebuild_git_params = {
    "sources": {
        "git_trees": [
            {"url": "http://git.yoctoproject.org/git/poky", "branch": "main"},
            {"url": "https://github.com/ndechesne/meta-qcom", "branch": "main"},
        ]
    },
    "src_dir": "test/src",
    "build_dir": "test/build",
    "container": "ubuntu-20.04",
    "envsetup": "poky/oe-init-build-env",
    "distro": "poky",
    "machine": "dragonboard-845c",
    "targets": "core-image-minimal",
    "bblayers_conf": ['BBLAYERS += "../meta-qcom/"'],
    "environment": {},
    "local_manifest": "tests/unit/test.xml",
    "pinned_manifest": "",
    "sstate_mirror": "test_sstate",
    "dl_dir": "test_dl_dir",
    "runtime": "",
}


class Helpers:
    """Generic utility functions."""

    @staticmethod
    def setup_git(git_path):
        """
        Create a repo at git_path with two files and one commit.
        """
        files = [
            {
                "filename": "one",
                "contents": "The nice thing about standards is that you have so many to choose from.",
            },
            {"filename": "two", "contents": "☁️🐧☁️"},
        ]
        for f in files:
            with open(os.path.join(git_path, f["filename"]), "w") as h:
                h.write(f["contents"])
        subprocess.check_call(["git", "init"], cwd=git_path)
        subprocess.check_call(["git", "add", "."], cwd=git_path)
        subprocess.check_call(
            ["git", "config", "--local", "user.name", '"pytest ci"'], cwd=git_path
        )
        subprocess.check_call(
            ["git", "config", "--local", "user.email", '"test@email.com"'], cwd=git_path
        )
        subprocess.check_call(["git", "commit", "-m", '"Initial commit"'], cwd=git_path)

    @staticmethod
    def get_branch(path):
        """Get branch name from some repo at path"""
        return (
            subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=path
            )
            .strip()
            .decode("utf-8")
        )

    @staticmethod
    def get_sha(path):
        """Get first commit hash from some repo at path"""
        return (
            subprocess.check_output(
                ["git", "rev-list", "--max-parents=0", "HEAD"], cwd=path
            )
            .strip()
            .decode("utf-8")
        )


@pytest.fixture
def helpers():
    """Provide a helpers fixture so it's available to all tests."""
    return Helpers


@pytest.fixture()
def oebuild_git_object(helpers, tmpdir_factory):
    from tuxbake.models import OEBuild

    git_repo_1 = tmpdir_factory.mktemp("git_1")
    git_repo_2 = tmpdir_factory.mktemp("git_2")
    helpers.setup_git(git_repo_1)
    helpers.setup_git(git_repo_2)
    git_branch_1 = helpers.get_branch(git_repo_1)
    git_branch_2 = helpers.get_branch(git_repo_2)
    git_sha_1 = helpers.get_sha(git_repo_1)
    git_sha_2 = helpers.get_sha(git_repo_2)
    oebuild_git_params["sources"]["git_trees"][0]["url"] = f"{git_repo_1}"
    oebuild_git_params["sources"]["git_trees"][1]["url"] = f"{git_repo_2}"
    oebuild_git_params["sources"]["git_trees"][0]["branch"] = git_branch_1
    oebuild_git_params["sources"]["git_trees"][1]["branch"] = git_branch_2
    oebuild_git_params["sources"]["git_trees"][0]["sha"] = git_sha_1
    oebuild_git_params["sources"]["git_trees"][1]["sha"] = git_sha_2
    source_dir = tmpdir_factory.mktemp("src")
    oebuild_git_params["src_dir"] = source_dir

    oebuild = OEBuild(**oebuild_git_params)
    return (
        oebuild,
        git_repo_1,
        git_repo_2,
        git_branch_1,
        git_branch_2,
        git_sha_1,
        git_sha_2,
        source_dir,
    )


oebuild_repo_object = {
    "sources": {
        "repo": {
            "url": "https://gitlab.com/alok.ranjan1/test-project",
            "branch": "main",
            "manifest": "default.xml",
        },
    },
    "src_dir": "test/src",
    "build_dir": "test/build",
    "container": "ubuntu-20.04",
    "envsetup": "poky/oe-init-build-env",
    "distro": "poky",
    "machine": "dragonboard-845c",
    "targets": "core-image-minimal",
    "local_conf": [
        'PREFERRED_PROVIDER_virtual/kernel = "linux-generic-mainline"',
        'PREFERRED_VERSION_linux-generic-mainline = "git%"',
        'SRCREV_kernel_hikey = "1d1df41c5a33359a00e919d54eaebfb789711fdc"',
        'SRCREV_kernel_juno = "99613159ad749543621da8238acf1a122880144e"',
        'SRCREV_ltp_hikey = "9b0740b72622f56c4d1909e2fdf38e948cf85b53"',
        'PREFERRED_VERSION_ltp = "20210927+git%"',
    ],
    "bblayers_conf": ['BBLAYERS += "../meta-qcom/"'],
    "environment": {"TEMPLATECONF": "../oniro/flavours/linux"},
    "local_manifest": "tests/unit/test.xml",
    "pinned_manifest": "",
    "sstate_mirror": "test_sstate",
    "dl_dir": "test_dl_dir",
    "runtime": "",
}


@pytest.fixture()
def oebuild_repo_init_object():
    from tuxbake.models import OEBuild

    oebuild = OEBuild(**oebuild_repo_object)
    return oebuild
