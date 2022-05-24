# -*- coding: utf-8 -*-

from click.testing import CliRunner
import json
import pytest
import tuxsuite.cli
import tuxsuite.build


sample_token = "Q9qMlmkjkIuIGmEAw-Mf53i_qoJ8Z2eGYCmrNx16ZLLQGrXAHRiN2ce5DGlAebOmnJFp9Ggcq9l6quZdDTtrkw"
sample_url = "https://foo.bar.tuxbuild.com/v1"


def test_usage():
    """Test running cli() with no arguments"""
    runner = CliRunner()
    result = runner.invoke(tuxsuite.cli.cli, [])
    assert result.exit_code == 0
    assert "Usage" in result.output
    assert "Commands" in result.output


def test_bake_no_args():
    """Test calling bake() with no options"""
    runner = CliRunner()
    result = runner.invoke(tuxsuite.cli.bake, [])
    assert result.exit_code == 0
    assert "Usage" in result.output
    assert "help" in result.output


def test_bake_usage():
    """Test calling bake() with --help"""
    runner = CliRunner()
    result = runner.invoke(tuxsuite.cli.bake, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output
    assert "tuxsuite bake submit" in result.output


@pytest.fixture
def sample_bitbake_template():
    return """
{
  "container": "ubuntu-20.04",
  "envsetup": "poky/oe-init-build-env",
  "distro": "poky",
  "machine": "qemux86-64",
  "target": "core-image-minimal",
  "sources": {
    "git_trees": [
      {
        "url": "git://git.yoctoproject.org/poky",
        "branch": "dunfell"
      }
    ]
  }
}
"""


def test_bake(mocker, tmp_path, tuxsuite_config, sample_bitbake_template):
    template = tmp_path / "yocto.json"
    template.write_text(sample_bitbake_template)
    build = mocker.patch("tuxsuite.Bitbake.build")
    wait_for_object = mocker.patch("tuxsuite.cli.wait_for_object")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.bake,
        [
            "submit",
            f"{template}",
        ],
    )
    assert result.exit_code == 0
    assert build.call_count == 1
    assert wait_for_object.call_count == 1


def test_bake_invalid_json(mocker, tmp_path, tuxsuite_config, sample_bitbake_template):
    template = tmp_path / "yocto.json"
    template.write_text("random text")
    mocker.patch("tuxsuite.Bitbake.build")
    mocker.patch("tuxsuite.cli.wait_for_object")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.bake,
        [
            "submit",
            f"{template}",
        ],
    )
    assert result.exit_code == 1


def test_build_no_args():
    """Test calling build() with no options"""
    runner = CliRunner()
    result = runner.invoke(tuxsuite.cli.build, [])
    assert result.exit_code == 2
    assert "Usage" in result.output
    assert "help" in result.output


def test_build_usage():
    """Test calling build() with --help"""
    runner = CliRunner()
    result = runner.invoke(tuxsuite.cli.build, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output
    assert "--toolchain" in result.output
    assert "--git-repo TEXT" in result.output


@pytest.fixture
def tuxsuite_config(tmp_path, monkeypatch, tuxauth):
    c = tmp_path / "config.ini"
    with c.open("w") as f:
        f.write("[default]\n")
        f.write(f"token={sample_token}\n")
        f.write(f"api_url={sample_url}\n")
    monkeypatch.setenv("TUXSUITE_CONFIG", str(c))
    return c


def test_build(mocker, tuxsuite_config):
    build = mocker.patch("tuxsuite.Build.build")
    wait_for_object = mocker.patch("tuxsuite.cli.wait_for_object")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.build,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-ref=master",
            "--target-arch=arm64",
            "--kconfig=defconfig",
            "--toolchain=gcc-9",
        ],
    )
    assert result.exit_code == 0
    assert build.call_count == 1
    assert wait_for_object.call_count == 1


def test_build_quiet(mocker, tuxsuite_config):
    Build = mocker.patch("tuxsuite.Build")
    Build.return_value.build_data = "https://tuxsuite.example.com/abcdef0123456789/"
    mocker.patch("tuxsuite.cli.wait_for_object")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.build,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-ref=master",
            "--target-arch=arm64",
            "--kconfig=defconfig",
            "--toolchain=gcc-9",
            "--quiet",
        ],
    )
    assert result.exit_code == 0
    assert "Building Linux Kernel" not in result.output
    assert result.output == "https://tuxsuite.example.com/abcdef0123456789/\n"


def test_build_git_sha(mocker, tuxsuite_config):
    build = mocker.patch("tuxsuite.Build.build")
    wait_for_object = mocker.patch("tuxsuite.cli.wait_for_object")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.build,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-sha=beefbee",
            "--target-arch=arm64",
            "--kconfig=defconfig",
            "--toolchain=gcc-9",
        ],
    )
    assert result.exit_code == 0
    assert build.call_count == 1
    assert wait_for_object.call_count == 1


def test_build_kernel_image(mocker, tuxsuite_config):
    build = mocker.patch("tuxsuite.Build.build")
    wait_for_object = mocker.patch("tuxsuite.cli.wait_for_object")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.build,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-sha=beefbee",
            "--target-arch=arm64",
            "--kconfig=defconfig",
            "--toolchain=gcc-9",
            "--kernel-image=Image",
        ],
    )
    assert result.exit_code == 0
    assert build.call_count == 1
    assert wait_for_object.call_count == 1


def test_build_git_head(mocker, tuxsuite_config):
    get_git_head = mocker.patch("tuxsuite.gitutils.get_git_head")
    get_git_head.return_value = ("https://example.com/linux.git", "deadbeef")
    Build = mocker.patch("tuxsuite.Build")
    Build.return_value.build_data = "https://tuxsuite.example.com/abcdef0123456789/"
    wait_for_object = mocker.patch("tuxsuite.cli.wait_for_object")

    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.build,
        [
            "--git-head",
            "--target-arch=arm64",
            "--kconfig=defconfig",
            "--toolchain=gcc-9",
        ],
    )
    Build.assert_called_with(
        git_repo="https://example.com/linux.git",
        git_sha="deadbeef",
        git_ref=None,
        target_arch="arm64",
        kconfig=("defconfig",),
        toolchain="gcc-9",
        environment=(),
        targets=[],
        make_variables={},
        build_name=None,
        kernel_image=None,
        image_sha=None,
        no_cache=False,
    )
    wait_for_object.assert_called()
    assert result.exit_code == 0


def test_build_download(mocker, tuxsuite_config):
    build = mocker.patch("tuxsuite.Build.build")
    wait_for_object = mocker.patch("tuxsuite.cli.wait_for_object")
    download = mocker.patch("tuxsuite.download.download")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.build,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-ref=master",
            "--target-arch=arm64",
            "--kconfig=defconfig",
            "--toolchain=gcc-9",
            "--download",
        ],
    )
    assert result.exit_code == 0
    assert build.call_count == 1
    assert wait_for_object.call_count == 1
    download.assert_called_with(mocker.ANY, ".")


def test_build_download_output_dir(mocker, tuxsuite_config, tmp_path):
    mocker.patch("tuxsuite.Build.build")
    mocker.patch("tuxsuite.cli.wait_for_object")
    download = mocker.patch("tuxsuite.download.download")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.build,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-ref=master",
            "--target-arch=arm64",
            "--kconfig=defconfig",
            "--toolchain=gcc-9",
            "--download",
            f"--output-dir={tmp_path}",
        ],
    )
    assert result.exit_code == 0
    download.assert_called_with(mocker.ANY, str(tmp_path))


def test_build_show_logs(mocker, tuxsuite_config):
    Build = mocker.patch("tuxsuite.Build")
    build = Build.return_value
    build.build_data = "https://builds.com/21321312312/"
    wait_for_object = mocker.patch("tuxsuite.cli.wait_for_object")
    download_file = mocker.patch("tuxsuite.download.download_file")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.build,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-ref=master",
            "--target-arch=arm64",
            "--kconfig=defconfig",
            "--toolchain=gcc-9",
            "--show-logs",
        ],
    )
    assert result.exit_code == 0
    assert build.build.call_count == 1
    assert wait_for_object.call_count == 1
    download_file.assert_called_with(
        "https://builds.com/21321312312/build.log", mocker.ANY
    )


def test_build_download_show_logs(mocker, tuxsuite_config, tmp_path):
    Build = mocker.patch("tuxsuite.Build")
    build = Build.return_value
    build.uid = "21321312312"
    build.build_data = "https://builds.com/21321312312/"
    wait_for_object = mocker.patch("tuxsuite.cli.wait_for_object")
    runner = CliRunner()
    (tmp_path / "21321312312").mkdir()
    (tmp_path / "21321312312" / "build.log").write_text(
        "log line 1\nlog line 2\nerror: something\n"
    )
    result = runner.invoke(
        tuxsuite.cli.build,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-ref=master",
            "--target-arch=arm64",
            "--kconfig=defconfig",
            "--toolchain=gcc-9",
            "--download",
            f"--output-dir={tmp_path}",
            "--show-logs",
        ],
    )
    assert result.exit_code == 0
    assert build.build.call_count == 1
    assert wait_for_object.call_count == 1
    assert "log line 1\nlog line 2\n" in result.output
    assert "error: something" in result.output


sample_build_set = """
sets:
  - name: test
    builds:
      - {target_arch: arm64, toolchain: gcc-9, kconfig: defconfig}
      - {target_arch: arm64, toolchain: gcc-9, kconfig: allmodconfig}
      - {target_arch: arm64, toolchain: gcc-9, kconfig: allyesconfig}
      - {target_arch: arm, toolchain: gcc-9, kconfig: allmodconfig}
      - {target_arch: x86_64, toolchain: gcc-9, kconfig: allmodconfig}
      - {target_arch: x86_64, toolchain: clang-9, kconfig: allmodconfig}
      - {target_arch: x86_64, toolchain: gcc-9, kconfig: allyesconfig}
      - {target_arch: i386, toolchain: gcc-9, kconfig: allmodconfig}
      - {target_arch: riscv, toolchain: gcc-9, kconfig: allyesconfig}
  - name: arch-matrix
    builds:
      - {target_arch: arm64,  toolchain: gcc-9}
      - {target_arch: arm,    toolchain: gcc-9}
      - {target_arch: i386,   toolchain: gcc-9}
      - {target_arch: riscv,  toolchain: gcc-9}
      - {target_arch: x86_64,    toolchain: gcc-9}
"""


@pytest.fixture
def tux_config(tmp_path, tuxauth):
    config = tmp_path / "buildset.yaml"
    with config.open("w") as f:
        f.write(sample_build_set)
    return config


sample_plan = """
version: 1
name: Simple plan
description: A simple plan
jobs:

- name: tinyconfig
  builds:
    - {toolchain: gcc-8, target_arch: i386, kconfig: tinyconfig}
    - {toolchain: gcc-9, target_arch: i386, kconfig: tinyconfig}
  test: {device: qemu-i386, tests: [ltp-smoke]}
"""


@pytest.fixture
def plan_config(tmp_path, tuxauth):
    config = tmp_path / "plan.yaml"
    with config.open("w") as f:
        f.write(sample_plan)
    return config


@pytest.fixture
def plan_builds():
    build_attrs = {
        "group": "tuxgrp",
        "project": "tuxprj",
        "git_repo": "http://github.com/torvalds/linux",
        "git_ref": "master",
        "target_arch": "arm",
        "kconfig": "defconfig",
        "build_name": "test_build_name",
        "toolchain": "gcc-9",
        "token": "test_token",
        "kbapi_url": "http://test/foo",
        "tuxapi_url": "http://tuxapi",
        "kernel_image": "Image",
    }
    builds = [
        tuxsuite.build.Build(**build_attrs, uid="build-1"),
        tuxsuite.build.Build(**build_attrs, uid="build-2"),
        tuxsuite.build.Build(**build_attrs, uid="build-3"),
        tuxsuite.build.Build(**build_attrs, uid="build-4"),
        tuxsuite.build.Build(**build_attrs, uid="build-5"),
        tuxsuite.build.Build(**build_attrs, uid="build-6"),
        tuxsuite.build.Build(**build_attrs, uid="build-7"),
        tuxsuite.build.Build(**build_attrs, uid="build-8"),
        tuxsuite.build.Build(**build_attrs, uid="build-9"),
    ]
    return builds


@pytest.fixture
def plan_builds_status_list():
    build_attrs = {
        "group": "tuxgrp",
        "project": "tuxprj",
        "git_repo": "http://github.com/torvalds/linux",
        "git_ref": "master",
        "target_arch": "arm",
        "kconfig": "defconfig",
        "build_name": "test_build_name",
        "toolchain": "gcc-9",
        "token": "test_token",
        "kbapi_url": "http://test/foo",
        "tuxapi_url": "http://tuxapi",
        "kernel_image": "Image",
    }
    builds = [
        build_attrs,
        build_attrs,
        build_attrs,
        build_attrs,
        build_attrs,
        build_attrs,
        build_attrs,
        build_attrs,
        build_attrs,
    ]
    return builds


def test_build_set(mocker, tuxsuite_config, tux_config):
    build = mocker.patch("tuxsuite.Plan.submit")
    wait_for_object = mocker.patch("tuxsuite.cli.wait_for_object")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.build_set,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-ref=master",
            f"--tux-config={tux_config}",
            "--set-name=test",
        ],
    )
    assert result.exit_code == 0
    assert build.call_count == 1
    assert wait_for_object.call_count == 1


def test_build_set_quiet(mocker, tuxsuite_config, tux_config):
    BuildSet = mocker.patch("tuxsuite.Plan")
    builds = []
    for i in range(1, 10):
        build = mocker.MagicMock()
        build.build_data = f"https://tuxsuite.example.com/{i}/"
        builds.append(build)
    BuildSet.return_value.builds = builds
    mocker.patch("tuxsuite.cli.wait_for_object")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.build_set,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-ref=master",
            f"--tux-config={tux_config}",
            "--set-name=test",
            "--quiet",
        ],
    )
    assert result.exit_code == 0
    output = "".join([f"https://tuxsuite.example.com/{i}/\n" for i in range(1, 10)])
    assert result.output == output


def test_build_set_git_sha(mocker, tuxsuite_config, tux_config):
    build = mocker.patch("tuxsuite.Plan.submit")
    wait_for_object = mocker.patch("tuxsuite.cli.wait_for_object")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.build_set,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-sha=beefbee",
            f"--tux-config={tux_config}",
            "--set-name=test",
            "--quiet",
        ],
    )
    assert result.exit_code == 0
    assert build.call_count == 1
    assert wait_for_object.call_count == 1


def test_build_set_download(mocker, tuxsuite_config, tux_config, plan_builds):
    build = mocker.patch("tuxsuite.Plan")
    build.return_value.builds = plan_builds
    wait_for_object = mocker.patch("tuxsuite.cli.wait_for_object")
    download = mocker.patch("tuxsuite.download.download")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.build_set,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-ref=master",
            f"--tux-config={tux_config}",
            "--set-name=test",
            "--download",
        ],
    )
    assert result.exit_code == 0
    assert build.call_count == 1
    assert wait_for_object.call_count == 1
    assert download.call_count == 9


def test_build_set_show_logs(mocker, tuxsuite_config, tux_config, plan_builds):
    build = mocker.patch("tuxsuite.Plan")
    build.return_value.builds = plan_builds
    wait_for_object = mocker.patch("tuxsuite.cli.wait_for_object")
    show_log = mocker.patch("tuxsuite.cli.show_log")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.build_set,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-ref=master",
            f"--tux-config={tux_config}",
            "--set-name=test",
            "--show-logs",
        ],
    )
    assert result.exit_code == 0
    assert build.call_count == 1
    assert wait_for_object.call_count == 1
    assert show_log.call_count == 9


def state(mocker, **kwargs):
    s = mocker.MagicMock()

    # defaults
    s.state = "completed"
    s.status = "pass"
    s.icon = "✓"
    s.cli_color = "white"
    s.errors = 0
    s.warnings = 0
    s.final = True

    for k, v in kwargs.items():
        setattr(s, k, v)

    return s


@pytest.fixture
def build_state(mocker):
    return state(mocker)


def test_wait_for_object_pass(mocker, build_state):
    build = mocker.MagicMock()
    build.watch.return_value = [build_state]
    assert tuxsuite.cli.wait_for_object(build)


def test_wait_for_object_pass_with_warnings(mocker, build_state):
    build = mocker.MagicMock()
    build_state.warnings = 1
    build.watch.return_value = [build_state]
    assert tuxsuite.cli.wait_for_object(build)


def test_wait_for_object_fail(mocker, build_state):
    build = mocker.MagicMock()
    build_state.status = "fail"
    build_state.errors = 1
    build.watch.return_value = [build_state]
    assert not tuxsuite.cli.wait_for_object(build)


def test_wait_for_object_infra_failure(mocker, build_state):
    build = mocker.MagicMock()
    build_state.state = "error"
    build.final = True
    build.watch.return_value = [build_state]
    assert not tuxsuite.cli.wait_for_object(build)


def test_wait_for_object_infra_failure_retried(mocker):
    error = state(mocker, state="error", final=False)
    retry_pass = state(mocker)
    build = mocker.MagicMock()
    build.watch.return_value = [error, retry_pass]
    assert tuxsuite.cli.wait_for_object(build)


def test_build_environment_option():
    """Test calling build with --help to see environment option"""
    runner = CliRunner()
    result = runner.invoke(tuxsuite.cli.build, ["--help"])
    assert result.exit_code == 0
    assert "-e, --environment KEY_VALUE" in result.output


def test_build_valid_environment(mocker, tuxsuite_config):
    Build = mocker.patch("tuxsuite.Build")
    build = Build.return_value
    wait_for_object = mocker.patch("tuxsuite.cli.wait_for_object")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.build,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-ref=master",
            "--target-arch=arm64",
            "--kconfig=defconfig",
            "--toolchain=gcc-9",
            "-e KCONFIG_ALLCONFIG=arch/arm64/configs/defconfig",
        ],
    )
    assert result.exit_code == 0
    assert build.build.call_count == 1
    assert wait_for_object.call_count == 1


def test_invalid_environment_key_value(mocker, tuxsuite_config):
    Build = mocker.patch("tuxsuite.Build")
    build = Build.return_value
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.build,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-ref=master",
            "--target-arch=arm64",
            "--kconfig=defconfig",
            "--toolchain=gcc-9",
            "-e INVALID",
        ],
    )
    assert result.exit_code == 1
    assert build.build.call_count == 0
    assert "Key Value pair not valid:  INVALID" in result.output


def test_build_make_targets_vars_argument():
    """Test calling build with --help to see targets argument"""
    runner = CliRunner()
    result = runner.invoke(tuxsuite.cli.build, ["--help"])
    assert result.exit_code == 0
    assert "[VAR=VALUE...] [target ...]" in result.output
    assert "[KEY=VALUE | target] ..." in result.output


def test_build_set_make_targets_vars_argument():
    """Test calling build with --help to see targets argument"""
    runner = CliRunner()
    result = runner.invoke(tuxsuite.cli.build_set, ["--help"])
    assert result.exit_code == 0
    assert "[VAR=VALUE...] [target ...]" in result.output
    assert "[KEY=VALUE | target] ..." in result.output


def test_build_valid_make_targets(mocker, tuxsuite_config):
    Build = mocker.patch("tuxsuite.Build")
    build = Build.return_value
    wait_for_object = mocker.patch("tuxsuite.cli.wait_for_object")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.build,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-ref=master",
            "--target-arch=arm64",
            "--kconfig=defconfig",
            "--toolchain=gcc-9",
            "dtbs config",
        ],
    )
    assert result.exit_code == 0
    assert build.build.call_count == 1
    assert wait_for_object.call_count == 1


def test_build_valid_make_vars(mocker, tuxsuite_config):
    Build = mocker.patch("tuxsuite.Build")
    build = Build.return_value
    wait_for_object = mocker.patch("tuxsuite.cli.wait_for_object")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.build,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-ref=master",
            "--target-arch=arm64",
            "--kconfig=defconfig",
            "--toolchain=gcc-9",
            "LLVM=1",
        ],
    )
    assert result.exit_code == 0
    assert build.build.call_count == 1
    assert wait_for_object.call_count == 1


def test_build_invalid_make_vars(mocker, tuxsuite_config):
    Build = mocker.patch("tuxsuite.Build")
    build = Build.return_value
    wait_for_object = mocker.patch("tuxsuite.cli.wait_for_object")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.build,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-ref=master",
            "--target-arch=arm64",
            "--kconfig=defconfig",
            "--toolchain=gcc-9",
            "LLVM=1=1",
        ],
    )
    assert result.exit_code == 1
    assert build.build.call_count == 0
    assert wait_for_object.call_count == 0


def test_plan_no_args():
    runner = CliRunner()
    result = runner.invoke(tuxsuite.cli.plan, [])
    assert result.exit_code == 2
    assert "Usage" in result.output
    assert "help" in result.output


def test_plan_usage():
    """Test calling plan() with --help"""
    runner = CliRunner()
    result = runner.invoke(tuxsuite.cli.plan, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output
    assert "--git-repo" in result.output
    assert "--name" in result.output
    assert "--description" in result.output


def test_plan_cli(mocker, plan_config):
    plan = mocker.patch("tuxsuite.Plan")
    mocker.patch("tuxsuite.cli.wait_for_object")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.plan,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-ref=master",
            str(plan_config),
        ],
    )
    assert result.exit_code == 0
    plan.assert_called_once()


def test_plan_cli_options(mocker, plan_config, tuxsuite_config):
    download = mocker.patch("tuxsuite.download.download")
    plan_obj = tuxsuite.Plan(
        "", token="token", tuxapi_url="http://api", project="prj", group="grp"
    )
    plan_obj.plan = "1sMUTVjE25tQvDmjJ8SjWblpOJr"
    plan_obj.builds = [
        mocker.Mock(
            uid="1",
            target_arch="arm64",
            toolchain="gcc-10",
            status=sample_plan_result["builds"]["1"],
        ),
        mocker.Mock(
            uid="2",
            target_arch="arm64",
            toolchain="gcc-11",
            status=sample_plan_result["builds"]["2"],
        ),
    ]
    plan_obj.tests = [
        mocker.Mock(
            uid="1",
            wait_for="1",
            tests=["boot", "ltp-smoke"],
            status={**sample_plan_result["tests"]["1"], "waiting_for": "1"},
        ),
    ]
    plan_obj.submit = mocker.Mock()
    plan = mocker.patch("tuxsuite.Plan")
    plan.return_value = plan_obj
    show_log = mocker.patch("tuxsuite.cli.show_log")
    wait_for_object = mocker.patch("tuxsuite.cli.wait_for_object")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.plan,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-ref=master",
            "--download",
            "--show-logs",
            str(plan_config),
        ],
    )

    assert result.exit_code == 0
    plan.assert_called_once()
    assert wait_for_object.call_count == 1
    assert download.call_count == 2
    assert show_log.call_count == 2

    print(result)
    assert (
        """Running Linux Kernel plan 'Simple plan': 'A simple plan'
Plan http://api/v1/groups/grp/projects/prj/plans/1sMUTVjE25tQvDmjJ8SjWblpOJr

uid: 1sMUTVjE25tQvDmjJ8SjWblpOJr

Summary: http://api/v1/groups/grp/projects/prj/plans/1sMUTVjE25tQvDmjJ8SjWblpOJr
2 👾 Pass (1 warning) arm64@gcc-11
1 🎉 Pass arm64@gcc-10 👹 Fail: boot,ltp-smoke"""
        in result.output
    )


def test_plan_empty_config(mocker, plan_config, tuxsuite_config):
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.plan,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-ref=master",
            "--job-name=kconfig",
            str(plan_config),
        ],
    )
    assert result.exit_code == 0
    assert "Empty plan, skipping" in result.output


def test_test_no_args():
    runner = CliRunner()
    result = runner.invoke(tuxsuite.cli.test, [])
    assert result.exit_code == 2
    assert "Usage" in result.output
    assert "help" in result.output


def test_test_usage():
    """Test calling test() with --help"""
    runner = CliRunner()
    result = runner.invoke(tuxsuite.cli.test, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output
    assert "--device" in result.output
    assert "--kernel" in result.output


def test_test_cli(mocker, tuxsuite_config):
    test = mocker.patch("tuxsuite.Test")
    wait_for_object = mocker.patch("tuxsuite.cli.wait_for_object")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.test,
        [
            "--device=qemu-arm64",
            "--kernel=https://example.com/vmlinux",
        ],
    )
    assert result.exit_code == 0
    assert test.call_count == 1
    test.assert_called_once_with(
        device="qemu-arm64",
        kernel="https://example.com/vmlinux",
        ap_romfw=None,
        mcp_fw=None,
        mcp_romfw=None,
        modules=None,
        rootfs=None,
        scp_fw=None,
        scp_romfw=None,
        fip=None,
        parameters={},
        tests=[],
        timeouts={},
        boot_args=None,
        wait_for=None,
    )
    assert wait_for_object.call_count == 1

    mocker.resetall()
    result = runner.invoke(
        tuxsuite.cli.test,
        [
            "--device=qemu-arm64",
            "--kernel=https://example.com/vmlinux",
            "--modules=https://example.com/modules.tar.xz",
            "--tests=ltp-smoke",
        ],
    )
    assert result.exit_code == 0
    assert test.call_count == 1
    test.assert_called_once_with(
        device="qemu-arm64",
        kernel="https://example.com/vmlinux",
        ap_romfw=None,
        mcp_fw=None,
        mcp_romfw=None,
        modules="https://example.com/modules.tar.xz",
        rootfs=None,
        scp_fw=None,
        scp_romfw=None,
        fip=None,
        parameters={},
        tests=["ltp-smoke"],
        timeouts={},
        boot_args=None,
        wait_for=None,
    )
    assert wait_for_object.call_count == 1

    mocker.resetall()
    result = runner.invoke(
        tuxsuite.cli.test,
        [
            "--device=qemu-arm64",
            "--tests=ltp-smoke",
            "--wait-for=mybuilduid",
        ],
    )
    assert result.exit_code == 0
    assert test.call_count == 1
    test.assert_called_once_with(
        device="qemu-arm64",
        kernel=None,
        ap_romfw=None,
        mcp_fw=None,
        mcp_romfw=None,
        modules=None,
        rootfs=None,
        scp_fw=None,
        scp_romfw=None,
        fip=None,
        parameters={},
        tests=["ltp-smoke"],
        timeouts={},
        boot_args=None,
        wait_for="mybuilduid",
    )
    assert wait_for_object.call_count == 1

    mocker.resetall()
    result = runner.invoke(
        tuxsuite.cli.test,
        [
            "--device=qemu-arm64",
            "--timeouts=deploy=1",
            "--timeouts=boot=2",
        ],
    )
    assert result.exit_code == 0
    assert test.call_count == 1
    test.assert_called_once_with(
        device="qemu-arm64",
        kernel=None,
        ap_romfw=None,
        mcp_fw=None,
        mcp_romfw=None,
        modules=None,
        rootfs=None,
        scp_fw=None,
        scp_romfw=None,
        fip=None,
        parameters={},
        tests=[],
        timeouts={"deploy": 1, "boot": 2},
        boot_args=None,
        wait_for=None,
    )
    assert wait_for_object.call_count == 1

    mocker.resetall()
    result = runner.invoke(
        tuxsuite.cli.test,
        [
            "--device=fvp-morello-android",
            "--ap-romfw=tf_bl1.bin",
            "--mcp-fw=mcp_fw.bin",
            "--mcp-romfw=mcp_romfw.bin",
            "--rootfs=rootfs.ext4",
            "--scp-fw=scp_fw.bin",
            "--scp-romfw=scp_romfw.bin",
            "--fip=fip.bin",
            "--parameters=USERDATA=userdata.tar.xz",
            "--parameters=TC_URL=toolchain.tar.xz",
            "--tests=lldb",
            "--",
        ],
    )
    assert result.exit_code == 0
    assert test.call_count == 1
    test.assert_called_once_with(
        device="fvp-morello-android",
        kernel=None,
        ap_romfw="tf_bl1.bin",
        mcp_fw="mcp_fw.bin",
        mcp_romfw="mcp_romfw.bin",
        modules=None,
        rootfs="rootfs.ext4",
        scp_fw="scp_fw.bin",
        scp_romfw="scp_romfw.bin",
        fip="fip.bin",
        parameters={"USERDATA": "userdata.tar.xz", "TC_URL": "toolchain.tar.xz"},
        tests=["lldb"],
        timeouts={},
        boot_args=None,
        wait_for=None,
    )
    assert wait_for_object.call_count == 1


def test_test_cli_errors(mocker):
    test = mocker.patch("tuxsuite.Test")
    mocker.patch("tuxsuite.cli.wait_for_object")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.test,
        [
            "--device=qemu-arm64",
            "--kernel=https://example.com/vmlinux",
            "--wait-for=mybuilduid",
        ],
    )
    assert result.exit_code == 1
    assert test.call_count == 0


def test_build_no_wait(mocker, tmp_path):
    build = mocker.patch("tuxsuite.Build.build")
    format_result = mocker.patch("tuxsuite.cli.format_result")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.build,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-ref=master",
            "--target-arch=arm64",
            "--kconfig=defconfig",
            "--toolchain=gcc-9",
            "--no-wait",
            f"--json-out={tmp_path}/build_result.json",
        ],
    )
    assert result.exit_code == 0
    assert build.call_count == 1
    assert format_result.call_count == 1


def test_build_set_no_wait(
    mocker, tuxsuite_config, tux_config, tmp_path, plan_builds, plan_builds_status_list
):
    build = mocker.patch("tuxsuite.Plan")
    build.return_value.builds = plan_builds
    build.return_value.build_status_list = plan_builds_status_list
    format_result = mocker.patch("tuxsuite.cli.format_result")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.build_set,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-ref=master",
            f"--tux-config={tux_config}",
            "--set-name=test",
            "--no-wait",
            f"--json-out={tmp_path}/build_result.json",
        ],
    )

    assert result.exit_code == 0
    assert build.call_count == 1
    assert format_result.call_count == 9


def test_test_cli_no_wait(mocker, tuxsuite_config):
    test = mocker.patch("tuxsuite.Test")
    format_result = mocker.patch("tuxsuite.cli.format_result")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.test,
        [
            "--device=qemu-arm64",
            "--kernel=https://example.com/vmlinux",
            "--no-wait",
        ],
    )
    assert result.exit_code == 0
    assert test.call_count == 1
    assert format_result.call_count == 1


def test_plan_cli_no_wait(mocker, tuxsuite_config, plan_config):
    plan = mocker.patch("tuxsuite.Plan")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.plan,
        [
            "--git-repo=https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
            "--git-ref=https://example.com/vmlinux",
            f"{plan_config}",
            "--no-wait",
        ],
    )
    assert result.exit_code == 0
    assert plan.call_count == 1


sample_build_result = {
    "project": "ci",
    "git_repo": "https://example.com/linux.git",
    "git_ref": "master",
    "git_sha": "deadbeef",
    "build_name": "",
    "download_url": "https://builds.dev.tuxbuild.com/1sMUTVjE25tQvDmjJ8SjWblpOJr/",
    "errors_count": 0,
    "kconfig": ["tinyconfig"],
    "plan": "null",
    "result": "pass",
    "state": "finished",
    "status_message": "build completed",
    "target_arch": "arm",
    "toolchain": "gcc-9",
    "uid": "1sMUTVjE25tQvDmjJ8SjWblpOJr",
    "warnings_count": 0,
}


sample_test_result = {
    "project": "ci",
    "device": "qemu-i386",
    "plan": "1sMNB0p8a3OrpUmEBgYah0Ycer9",
    "result": "fail",
    "results": {"boot": "fail"},
    "state": "finished",
    "tests": ["boot"],
    "uid": "1sMNBWLFrsOahyXQCNeiT4bgysP",
    "waiting_for": None,
}

sample_all_result = {
    "builds": {
        "count": 3,
        "next": "null",
        "results": [
            sample_build_result,
            {**sample_build_result, **dict({"warnings_count": 1})},
            {**sample_build_result, **dict({"warnings_count": 3})},
            {**sample_build_result, **dict({"result": "fail", "errors_count": 1})},
        ],
    },
    "plans": {
        "count": 1,
        "next": "null",
        "results": [
            {
                "description": "A simple plan",
                "name": "Simple plan",
                "project": "tuxsuite/senthil",
                "uid": "1sMNB0p8a3OrpUmEBgYah0Ycer9",
            }
        ],
    },
    "tests": {
        "count": 1,
        "next": "null",
        "results": [
            sample_test_result,
        ],
    },
}


sample_plan_result = {
    "builds": {
        "1": sample_build_result,
        "2": {**sample_build_result, **dict({"warnings_count": 1})},
        "3": {**sample_build_result, **dict({"warnings_count": 3})},
        "4": {**sample_build_result, **dict({"result": "fail", "errors_count": 1})},
    },
    "tests": {"1": sample_test_result},
}

sample_plan_status = {
    "builds": {
        "1sewrBhxNVbsURAKBjeXX8pyjwY": sample_build_result,
    },
    "tests": {
        "1sewrJ4GHQygVKvTjUxuYRK1hOh": sample_test_result,
    },
}


@pytest.fixture
def build_result(tmp_path):
    build_json = tmp_path / "build_result.json"
    with build_json.open("w") as f:
        f.write(json.dumps(sample_build_result))
    return build_json


@pytest.fixture
def test_result(tmp_path):
    test_json = tmp_path / "test_result.json"
    with test_json.open("w") as f:
        f.write(json.dumps(sample_test_result))
    return test_json


@pytest.fixture
def build_set_result(tmp_path):
    build_set_json = tmp_path / "build_set_result.json"
    build_set = [
        sample_build_result,
        sample_build_result,
    ]
    with build_set_json.open("w") as f:
        f.write(json.dumps(build_set))
    return build_set_json


@pytest.fixture
def plan_result(tmp_path):
    plan_json = tmp_path / "plan_result.json"
    with plan_json.open("w") as f:
        f.write(json.dumps(sample_plan_status))
    return plan_json


def test_results_cli(
    mocker,
    tmp_path,
    tuxsuite_config,
    build_result,
    test_result,
    build_set_result,
    plan_result,
):
    results = mocker.patch(
        "tuxsuite.Results.get_all", return_value=(sample_all_result, "http://api")
    )
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.results,
        [],
    )
    assert result.exit_code == 0
    assert results.call_count == 1

    format_result = mocker.patch("tuxsuite.cli.format_result")
    mocker.resetall()
    results = mocker.patch(
        "tuxsuite.Results.get_build", return_value=sample_build_result
    )
    result = runner.invoke(
        tuxsuite.cli.results,
        [
            "--build=1sMUTVjE25tQvDmjJ8SjWblpOJr",
            f"--json-out={tmp_path}/build_result.json",
        ],
    )
    assert result.exit_code == 0
    assert results.call_count == 1
    assert format_result.call_count == 1

    mocker.resetall()
    results = mocker.patch(
        "tuxsuite.Results.get_test", return_value=(sample_test_result, "http://api")
    )
    result = runner.invoke(
        tuxsuite.cli.results,
        [
            "--test=1sMNBWLFrsOahyXQCNeiT4bgysP",
        ],
    )
    assert result.exit_code == 0
    assert results.call_count == 1
    assert format_result.call_count == 1

    mocker.resetall()
    results = mocker.patch(
        "tuxsuite.Results.get_plan", return_value=(sample_plan_result, "http://api")
    )
    result = runner.invoke(
        tuxsuite.cli.results,
        [
            "--plan=1sMNB0p8a3OrpUmEBgYah0Ycer9",
        ],
    )
    assert result.exit_code == 0
    assert results.call_count == 1
    assert (
        result.output
        == """Summary: https://tuxapi.tuxsuite.com/v1/groups/tuxsuite/projects/tux/plans/1sMNB0p8a3OrpUmEBgYah0Ycer9
1sMUTVjE25tQvDmjJ8SjWblpOJr 🎉 Pass arm@gcc-9
1sMUTVjE25tQvDmjJ8SjWblpOJr 👾 Pass (1 warning) arm@gcc-9
1sMUTVjE25tQvDmjJ8SjWblpOJr 👾 Pass (3 warnings) arm@gcc-9
1sMUTVjE25tQvDmjJ8SjWblpOJr 👹 Fail (1 error) arm@gcc-9
builds (4): 🎉 1 👾 2 👹 1
tests (1): 👹 1
"""
    )

    mocker.resetall()
    results = mocker.patch(
        "tuxsuite.Results.get_build", return_value=sample_build_result
    )
    result = runner.invoke(
        tuxsuite.cli.results,
        [
            f"--from-json={build_result}",
        ],
    )
    assert result.exit_code == 0
    assert results.call_count == 1
    assert format_result.call_count == 1

    mocker.resetall()
    results = mocker.patch(
        "tuxsuite.Results.get_test", return_value=(sample_test_result, "http://api")
    )
    result = runner.invoke(
        tuxsuite.cli.results,
        [
            f"--from-json={test_result}",
        ],
    )
    assert result.exit_code == 0
    assert results.call_count == 1
    assert format_result.call_count == 1

    mocker.resetall()
    results = mocker.patch(
        "tuxsuite.Results.get_build", return_value=sample_build_result
    )
    result = runner.invoke(
        tuxsuite.cli.results,
        [
            f"--from-json={build_set_result}",
            f"--json-out={tmp_path}/build_set_result.json",
        ],
    )
    assert result.exit_code == 0
    assert results.call_count == 2
    assert format_result.call_count == 2

    mocker.resetall()
    results = mocker.patch(
        "tuxsuite.Results.get_plan", return_value=(sample_plan_result, "http://api")
    )
    result = runner.invoke(
        tuxsuite.cli.results,
        [
            f"--from-json={plan_result}",
        ],
    )
    assert result.exit_code == 0
    assert results.call_count == 1
    assert (
        result.output
        == """Summary: https://tuxapi.tuxsuite.com/v1/groups/tuxsuite/projects/tux/plans/null
1sMUTVjE25tQvDmjJ8SjWblpOJr 🎉 Pass arm@gcc-9
1sMUTVjE25tQvDmjJ8SjWblpOJr 👾 Pass (1 warning) arm@gcc-9
1sMUTVjE25tQvDmjJ8SjWblpOJr 👾 Pass (3 warnings) arm@gcc-9
1sMUTVjE25tQvDmjJ8SjWblpOJr 👹 Fail (1 error) arm@gcc-9
builds (4): 🎉 1 👾 2 👹 1
tests (1): 👹 1
"""
    )


def test_results_cli_errors(mocker, tmp_path, tuxsuite_config, build_set_result):
    results = mocker.patch(
        "tuxsuite.Results.get_all",
        return_value=(sample_all_result, "http://api"),
        side_effect=tuxsuite.exceptions.URLNotFound,
    )
    format_result = mocker.patch("tuxsuite.cli.format_result")
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.results,
        [],
    )
    assert result.exit_code == 1
    assert results.call_count == 1
    assert format_result.call_count == 0

    mocker.resetall()
    results = mocker.patch(
        "tuxsuite.Results.get_build",
        return_value=sample_build_result,
        side_effect=tuxsuite.exceptions.URLNotFound,
    )
    result = runner.invoke(
        tuxsuite.cli.results,
        [
            "--build=1sMUTVjE25tQvDmjJ8SjWblpOJr",
        ],
    )
    assert result.exit_code == 1
    assert results.call_count == 1
    assert format_result.call_count == 0

    mocker.resetall()
    results = mocker.patch(
        "tuxsuite.Results.get_test",
        return_value=(sample_test_result, "http://api"),
        side_effect=tuxsuite.exceptions.URLNotFound,
    )
    result = runner.invoke(
        tuxsuite.cli.results,
        [
            "--test=1sMNBWLFrsOahyXQCNeiT4bgysP",
        ],
    )
    assert result.exit_code == 1
    assert results.call_count == 1
    assert format_result.call_count == 0

    mocker.resetall()
    results = mocker.patch(
        "tuxsuite.Results.get_plan",
        return_value=(sample_all_result, "http://api"),
        side_effect=tuxsuite.exceptions.URLNotFound,
    )
    result = runner.invoke(
        tuxsuite.cli.results,
        [
            "--plan=1sMNB0p8a3OrpUmEBgYah0Ycer9",
        ],
    )
    assert result.exit_code == 1
    assert results.call_count == 1
    assert format_result.call_count == 0

    mocker.resetall()
    results = mocker.patch(
        "tuxsuite.Results.get_build",
        return_value=sample_build_result,
        side_effect=tuxsuite.exceptions.URLNotFound,
    )
    result = runner.invoke(
        tuxsuite.cli.results,
        [
            f"--from-json={build_set_result}",
            f"--json-out={tmp_path}/build_set_result.json",
        ],
    )
    assert result.exit_code == 1
    assert results.call_count == 1
    assert format_result.call_count == 0

    mocker.resetall()
    results = mocker.patch(
        "tuxsuite.Results",
        side_effect=tuxsuite.exceptions.TuxSuiteError,
    )
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.results,
        [],
    )
    assert result.exit_code == 1
    assert results.call_count == 1


def test_patch_series_error(mocker, tuxsuite_config):
    runner = CliRunner()

    # invalid url scheme
    result = runner.invoke(
        tuxsuite.cli.build,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-sha=beefbee",
            "--target-arch=arm64",
            "--kconfig=defconfig",
            "--toolchain=gcc-9",
            "--patch-series=httpsucks.patch",
        ],
    )
    assert result.exit_code == 2
    assert "Error: Invalid value for '-p' / '--patch-series'" in result.output

    mocker.resetall()
    # invalid patch file
    result = runner.invoke(
        tuxsuite.cli.build,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-sha=beefbee",
            "--target-arch=arm64",
            "--kconfig=defconfig",
            "--toolchain=gcc-9",
            "--patch-series=/tmp/invalidpatch",
        ],
    )
    assert result.exit_code == 2
    assert "Error: Invalid value for '-p' / '--patch-series'" in result.output


def test_patch_series_pass(mocker, sample_patch_tgz, sample_patch_mbx, tuxsuite_config):
    build = mocker.patch("tuxsuite.Build.build")
    wait_for_object = mocker.patch("tuxsuite.cli.wait_for_object")
    runner = CliRunner()
    # valid url scheme
    result = runner.invoke(
        tuxsuite.cli.build,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-sha=beefbee",
            "--target-arch=arm64",
            "--kconfig=defconfig",
            "--toolchain=gcc-9",
            "--patch-series=https://www.example.com/example.tgz",
        ],
    )
    assert result.exit_code == 0
    assert build.call_count == 1
    assert wait_for_object.call_count == 1

    mocker.resetall()
    # valid patch file
    result = runner.invoke(
        tuxsuite.cli.build,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-sha=beefbee",
            "--target-arch=arm64",
            "--kconfig=defconfig",
            "--toolchain=gcc-9",
            f"--patch-series={sample_patch_tgz}",
        ],
    )
    assert result.exit_code == 0
    assert build.call_count == 1
    assert wait_for_object.call_count == 1


def test_build_config(mocker, tuxsuite_config):
    config = mocker.MagicMock()
    config.function.return_value = 0
    mocker.patch.dict("tuxsuite.cli.build_handlers", config=config)
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.build,
        [
            "config",
            "205Yag6znViIi4oLWFVDxJC4avb",
        ],
    )
    assert result.exit_code == 2


def test_build_set_empty_config(mocker, tuxsuite_config, tux_config):
    plan_config = mocker.patch("tuxsuite.config.BuildSetConfig")
    plan_config.return_value.plan = None
    runner = CliRunner()
    result = runner.invoke(
        tuxsuite.cli.build_set,
        [
            "--git-repo=https://git.example.com/linux.git",
            "--git-ref=master",
            f"--tux-config={tux_config}",
            "--set-name=test",
        ],
    )
    assert result.exit_code == 0
    assert "Empty plan, skipping" in result.output
