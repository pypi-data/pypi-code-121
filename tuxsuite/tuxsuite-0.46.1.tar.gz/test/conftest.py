# -*- coding: utf-8 -*-

import os
import requests
import tarfile
import tuxsuite.config
import pytest


@pytest.fixture(autouse=True)
def session(mocker):
    mocker.patch("requests.Session.get")
    mocker.patch("requests.Session.post")
    return requests.Session


@pytest.fixture
def response():
    r = requests.Response()
    r.status_code = 200
    return r


@pytest.fixture
def post(session, response):
    session.post.return_value = response
    return session.post


@pytest.fixture
def get(session, response):
    session.get.return_value = response
    return session.get


@pytest.fixture
def tuxauth(mocker):
    get = mocker.Mock(
        return_value=mocker.Mock(
            **{
                "status_code": 200,
                "json.return_value": {
                    "UserDetails": {"Groups": ["tuxsuite"], "Name": "tux"}
                },
            }
        )
    )
    mocker.patch("tuxsuite.config.requests.get", get)
    return get


@pytest.fixture
def sample_token():
    return "Q9qMlmkjkIuIGmEAw-Mf53i_qoJ8Z2eGYCmrNx16ZLLQGrXAHRiN2ce5DGlAebOmnJFp9Ggcq9l6quZdDTtrkw"


@pytest.fixture
def sample_url():
    return "https://foo.bar.tuxbuild.com/v1"


@pytest.fixture(autouse=True)
def home(monkeypatch, tmp_path):
    h = tmp_path / "HOME"
    h.mkdir()
    monkeypatch.setenv("HOME", str(h))
    return h


@pytest.fixture
def config(monkeypatch, sample_token, sample_url, tuxauth):
    monkeypatch.setenv("TUXSUITE_TOKEN", sample_token)
    monkeypatch.setenv("TUXSUITE_URL", sample_url)
    config = tuxsuite.config.Config("/nonexistent")
    config.kbapi_url = sample_url
    config.auth_token = sample_token
    config.token = sample_token
    return config


@pytest.fixture
def sample_plan_config():
    return """
version: 1
name: Simple plan
description: A simple plan
jobs:

- name: simple-gcc
  build: {toolchain: gcc-8, target_arch: i386, kconfig: tinyconfig}
  test: {device: qemu-i386, tests: [ltp-smoke], rootfs: "https://example.com/rootfs.ext4.zst"}

- name: full-gcc
  builds:
    - {toolchain: gcc-8, target_arch: i386, kconfig: tinyconfig}
    - {toolchain: gcc-9, target_arch: i386, kconfig: tinyconfig}
    - {toolchain: gcc-10, target_arch: i386, kconfig: tinyconfig}
  test: {device: qemu-i386, tests: [ltp-smoke]}

- builds:
    - {toolchain: clang-10, target_arch: i386, kconfig: tinyconfig}
    - {toolchain: clang-11, target_arch: i386, kconfig: tinyconfig}
    - {toolchain: clang-nightly, target_arch: i386, kconfig: tinyconfig}
  test: {device: qemu-i386}

- build: {toolchain: clang-nightly, target_arch: i386, kconfig: tinyconfig}
  tests:
    - {device: qemu-i386}
    - {device: qemu-i386, tests: [ltp-smoke]}

- builds:
    - {toolchain: gcc-8, target_arch: i386, kconfig: tinyconfig}
    - {toolchain: gcc-9, target_arch: i386, kconfig: tinyconfig}
    - {toolchain: gcc-10, target_arch: i386, kconfig: tinyconfig}
  tests:
    - {device: qemu-i386}
    - {device: qemu-i386, tests: [ltp-smoke]}

- tests:
    - {kernel: https://storage.tuxboot.com/arm64/Image, device: qemu-arm64, tests: [ltp-smoke]}
    - {kernel: https://storage.tuxboot.com/i386/bzImage, device: qemu-i386, tests: [ltp-smoke]}
    - {kernel: https://storage.tuxboot.com/mips64/vmlinux, device: qemu-mips64, tests: [ltp-smoke]}
    - {kernel: https://storage.tuxboot.com/ppc64/vmlinux, device: qemu-ppc64, tests: [ltp-smoke]}
    - {kernel: https://storage.tuxboot.com/riscv64/Image, device: qemu-riscv64, tests: [ltp-smoke]}
    - {kernel: https://storage.tuxboot.com/x86_64/bzImage, device: qemu-x86_64, tests: [ltp-smoke]}
"""


@pytest.fixture
def plan_config(tmp_path, sample_plan_config):
    c = tmp_path / "planv1.yml"
    c.write_text(sample_plan_config)
    return c


@pytest.fixture
def sample_bake_plan_config():
    return """
common: &commondata
  "container": "ubuntu-20.04"
  "distro": "rpb"
  "envsetup": "setup-environment"
  "machine": "dragonboard-845c"
  "sources": {
    "repo": {
      "branch": "qcom/dunfell",
      "manifest": "default.xml",
      "url": "https://github.com/96boards/oe-rpb-manifest.git",
    }
  }
  "target": "rpb-console-image rpb-console-image-test rpb-desktop-image rpb-desktop-image-test"
version: 1
name: armv7 validation
description: Build and test linux kernel for armv7
jobs:
- name: armv7
  bake: { <<: *commondata, "machine": "ledge-multi-armv7"}

- name: lt-qcom
  bakes:
    - { <<: *commondata}
    - { <<: *commondata}
"""


@pytest.fixture
def bake_plan_config(tmp_path, sample_bake_plan_config):
    bake_config = tmp_path / "sample_bake_plan.yml"
    bake_config.write_text(sample_bake_plan_config)
    return bake_config


@pytest.fixture
def sample_plan_unknown_version():
    return """
version: -1
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
def plan_config_unknown_version(tmp_path, sample_plan_unknown_version):
    config = tmp_path / "plan.yaml"
    with config.open("w") as f:
        f.write(sample_plan_unknown_version)
    return config


@pytest.fixture
def sample_patch():
    return "example mbox patch"


@pytest.fixture
def sample_patch_file(tmp_path, sample_patch):
    p = tmp_path / "patch.mbox"
    p.write_text(sample_patch)
    return str(p)


@pytest.fixture
def sample_patch_dir(tmp_path, sample_patch):
    p = tmp_path / "patch.mbox"
    p.write_text(sample_patch)
    s = tmp_path / "series"
    s.write_text("mock series file")
    return str(tmp_path)


@pytest.fixture
def sample_patch_tgz(tmp_path, sample_patch, sample_patch_dir):
    p = tmp_path / "patch.mbox"
    p.write_text(sample_patch)
    s = tmp_path / "series"
    s.write_text("mock series file")
    tar_file = os.path.join(tmp_path, "patch.tgz")
    with tarfile.open(tar_file, "w:gz") as tar:
        tar.add(tmp_path, arcname=os.path.sep)
    return str(tar_file)


@pytest.fixture
def sample_patch_tgz_no_series(tmp_path, sample_patch, sample_patch_dir):
    p = tmp_path / "patch.mbox"
    p.write_text(sample_patch)
    s = tmp_path / "series"
    os.remove(s)
    tar_file = os.path.join(tmp_path, "no_series_patch.tgz")
    with tarfile.open(tar_file, "w:gz") as tar:
        tar.add(tmp_path, arcname=os.path.sep)
    return str(tar_file)


@pytest.fixture
def sample_patch_mbx(tmp_path, sample_patch, sample_patch_dir):
    p = tmp_path / "patch.mbx"
    p.write_text(sample_patch)
    return str(p)


@pytest.fixture
def sample_manifest():
    return '<?xml version="1.0" encoding="UTF-8"?><manifest></manifest>'


@pytest.fixture
def sample_manifest_file(tmp_path, sample_manifest):
    m = tmp_path / "default.xml"
    m.write_text(sample_manifest)
    return str(m)
