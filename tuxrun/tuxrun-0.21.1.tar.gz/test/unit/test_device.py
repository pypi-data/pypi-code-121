import json
import os
from pathlib import Path

import pytest

from tuxrun.__main__ import main
from tuxrun.devices import Device
from tuxrun.devices.qemu import QemuArmv5
from tuxrun.devices.fvp import FVPMorelloAndroid
from tuxrun.exceptions import InvalidArgument


BASE = (Path(__file__) / "..").resolve()


def test_select():
    assert Device.select("qemu-armv5") == QemuArmv5
    assert Device.select("fvp-morello-android") == FVPMorelloAndroid

    with pytest.raises(InvalidArgument):
        Device.select("Hello")


ARTEFACTS = [
    "bzImage.gz",
    "zImage.xz",
    "modules.tar.xz",
    "tf-bl1.bin",
    "mcp_fw.bin",
    "mcp_romfw.bin",
    "android-nano.img.xz",
    "busybox.img.xz",
    "core-image-minimal-morello-fvp.wic",
    "scp_fw.bin",
    "scp_romfw.bin",
    "fip.bin",
    "ubuntu.satadisk.xz",
]

FVP_MORELLO_ANDROID = [
    "--ap-romfw",
    "tf-bl1.bin",
    "--mcp-fw",
    "mcp_fw.bin",
    "--mcp-romfw",
    "mcp_romfw.bin",
    "--rootfs",
    "android-nano.img.xz",
    "--scp-fw",
    "scp_fw.bin",
    "--scp-romfw",
    "scp_romfw.bin",
    "--fip",
    "fip.bin",
]

metadata = {
    "results": {
        "artifacts": {"kernel": ["bzImage.gz"], "modules": ["modules.tar.xz"]},
    },
    "build": {"target_arch": "arm64"},
}


@pytest.fixture
def artefacts(tmp_path):
    os.chdir(tmp_path)
    for art in ARTEFACTS:
        (tmp_path / art).touch()
    (tmp_path / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    return tmp_path


@pytest.mark.parametrize(
    "args,filename",
    [
        (
            ["--device", "qemu-arm64"],
            "qemu-arm64.yaml",
        ),
        (
            ["--device", "qemu-arm64", "--timeouts", "deploy=4", "boot=12"],
            "qemu-arm64-timeouts.yaml",
        ),
        (
            ["--device", "qemu-arm64", "--tests", "ltp-fcntl-locktests"],
            "qemu-arm64-ltp-fcntl-locktests.yaml",
        ),
        (
            ["--device", "qemu-arm64be"],
            "qemu-arm64be.yaml",
        ),
        (
            ["--device", "qemu-armv5"],
            "qemu-armv5.yaml",
        ),
        (
            ["--device", "qemu-armv5", "--tests", "ltp-fs_bind"],
            "qemu-armv5-ltp-fs_bind.yaml",
        ),
        (
            ["--device", "qemu-armv7"],
            "qemu-armv7.yaml",
        ),
        (
            [
                "--device",
                "qemu-armv7",
                "--tests",
                "kselftest-ipc",
                "--parameters",
                "KSELFTEST=https://example.com/kselftest.tar.xz",
            ],
            "qemu-armv7-kselftest-ipc.yaml",
        ),
        (
            [
                "--device",
                "qemu-armv7",
                "--tests",
                "kselftest-ipc",
                "--parameters",
                "CPUPOWER=https://example.com/cpupower.tar.xz",
                "KSELFTEST=https://example.com/kselftest.tar.xz",
            ],
            "qemu-armv7-kselftest-ipc-cpupower.yaml",
        ),
        (
            [
                "--device",
                "qemu-armv7",
                "--tests",
                "ltp-fs_perms_simple",
                "--tests",
                "ltp-fsx",
                "--tests",
                "ltp-nptl",
                "--timeouts",
                "ltp-fs_perms_simple=4",
                "--timeouts",
                "ltp-fsx=3",
            ],
            "qemu-armv7-ltp-mutliple-tests.yaml",
        ),
        (
            [
                "--device",
                "qemu-armv7",
                "--tests",
                "ltp-fs_perms_simple",
                "ltp-fsx",
                "ltp-nptl",
                "--timeouts",
                "ltp-fs_perms_simple=4",
                "ltp-fsx=3",
            ],
            "qemu-armv7-ltp-timeouts.yaml",
        ),
        (
            ["--device", "qemu-armv7", "--kernel", "zImage.xz"],
            "qemu-armv7-kernel-xz.yaml",
        ),
        (
            ["--device", "qemu-armv7be"],
            "qemu-armv7be.yaml",
        ),
        (
            ["--device", "qemu-i386"],
            "qemu-i386.yaml",
        ),
        (
            ["--device", "qemu-i386", "--tests", "kunit"],
            "qemu-i386-kunit.yaml",
        ),
        (
            ["--device", "qemu-i386", "--tests", "libgpiod"],
            "qemu-i386-libgpiod.yaml",
        ),
        (
            ["--device", "qemu-i386", "--tests", "libhugetlbfs"],
            "qemu-i386-libhugetlbfs.yaml",
        ),
        (
            ["--device", "qemu-i386", "--tests", "perf"],
            "qemu-i386-perf.yaml",
        ),
        (
            ["--device", "qemu-i386", "--tests", "rcutorture"],
            "qemu-i386-rcutorture.yaml",
        ),
        (
            ["--device", "qemu-i386", "--tests", "v4l2"],
            "qemu-i386-v4l2.yaml",
        ),
        (
            [
                "--device",
                "qemu-i386",
                "--tests",
                "kunit",
                "--overlay",
                "http://example.com/overlay1.tar.xz",
                "--overlay",
                "http://example.com/overlay2.tar.xz",
            ],
            "qemu-i386-kunit-overlays.yaml",
        ),
        (
            ["--device", "qemu-i386", "--kernel", "bzImage.gz"],
            "qemu-i386-kernel-gz.yaml",
        ),
        (
            ["--device", "qemu-i386", "--boot-args", "bla blo"],
            "qemu-i386-boot-args.yaml",
        ),
        (
            [
                "--device",
                "qemu-i386",
                "--tests",
                "kselftest-ipc",
                "--parameters",
                "CPUPOWER=https://example.com/cpupower.tar.xz",
                "KSELFTEST=https://example.com/kselftest.tar.xz",
            ],
            "qemu-i386-kselftest-ipc.yaml",
        ),
        (
            ["--device", "qemu-mips32"],
            "qemu-mips32.yaml",
        ),
        (
            [
                "--device",
                "qemu-mips32",
                "--modules",
                "https://example.com/modules.tar.xz",
            ],
            "qemu-mips32-modules.yaml",
        ),
        (
            [
                "--device",
                "qemu-mips32",
                "--modules",
                "https://example.com/modules.tgz",
            ],
            "qemu-mips32-modules-tgz.yaml",
        ),
        (
            [
                "--device",
                "qemu-mips32",
                "--modules",
                "https://example.com/modules.tar.xz",
                "--overlay",
                "http://example.com/overlay2.tar.xz",
                "--tests",
                "kunit",
            ],
            "qemu-mips32-modules-overlays-kunit.yaml",
        ),
        (
            ["--device", "qemu-mips32", "--", "cat", "/proc/cpuinfo"],
            "qemu-mips32-command.yaml",
        ),
        (
            ["--device", "qemu-mips32el"],
            "qemu-mips32el.yaml",
        ),
        (
            ["--device", "qemu-mips64"],
            "qemu-mips64.yaml",
        ),
        (
            ["--device", "qemu-mips64"],
            "qemu-mips64el.yaml",
        ),
        (
            ["--device", "qemu-ppc32"],
            "qemu-ppc32.yaml",
        ),
        (
            ["--device", "qemu-ppc64"],
            "qemu-ppc64.yaml",
        ),
        (
            ["--device", "qemu-ppc64le"],
            "qemu-ppc64le.yaml",
        ),
        (
            ["--device", "qemu-s390"],
            "qemu-s390.yaml",
        ),
        (
            ["--device", "qemu-s390", "--tests", "ltp-smoke"],
            "qemu-s390-ltp-smoke.yaml",
        ),
        (
            ["--device", "qemu-riscv64"],
            "qemu-riscv64.yaml",
        ),
        (
            ["--device", "qemu-sh4"],
            "qemu-sh4.yaml",
        ),
        (
            ["--device", "qemu-sh4", "--boot-args", "hello"],
            "qemu-sh4-boot-args.yaml",
        ),
        (
            ["--device", "qemu-sparc64"],
            "qemu-sparc64.yaml",
        ),
        (
            ["--device", "qemu-x86_64"],
            "qemu-x86_64.yaml",
        ),
        (
            [
                "--device",
                "qemu-x86_64",
                "--rootfs",
                "https://example.com/rootfs.ext4.zst",
            ],
            "qemu-x86_64-rootfs-zst.yaml",
        ),
        (
            [
                "--device",
                "qemu-x86_64",
                "--rootfs",
                "https://example.com/rootfs.ext4.gz",
            ],
            "qemu-x86_64-rootfs-gz.yaml",
        ),
        (
            [
                "--device",
                "fvp-aemva",
                "--bl1",
                "tf-bl1.bin",
                "--fip",
                "fip.bin",
                "--kernel",
                "zImage.xz",
                "--rootfs",
                "https://example.com/rootfs.ext4.zst",
            ],
            "fvp-aemva-kernel-xz.yaml",
        ),
        (
            [
                "--device",
                "fvp-aemva",
                "--bl1",
                "tf-bl1.bin",
                "--fip",
                "fip.bin",
                "--rootfs",
                "https://example.com/rootfs.ext4.zst",
                "--tests",
                "ltp-smoke",
            ],
            "fvp-aemva-ltp-smoke.yaml",
        ),
        (
            [
                "--device",
                "fvp-aemva",
                "--bl1",
                "tf-bl1.bin",
                "--fip",
                "fip.bin",
                "--rootfs",
                "https://example.com/rootfs.ext4.zst",
            ],
            "fvp-aemva.yaml",
        ),
        (
            [
                "--device",
                "fvp-aemva",
                "--bl1",
                "tf-bl1.bin",
                "--fip",
                "fip.bin",
                "--modules",
                "https://example.com/modules.tar.xz",
            ],
            "fvp-aemva-modules.yaml",
        ),
        (
            [
                "--device",
                "fvp-aemva",
                "--bl1",
                "tf-bl1.bin",
                "--fip",
                "fip.bin",
                "--modules",
                "https://example.com/modules.tar.gz",
            ],
            "fvp-aemva-modules-tar-gz.yaml",
        ),
        (
            ["--device", "fvp-morello-android", *FVP_MORELLO_ANDROID],
            "fvp-morello-android.yaml",
        ),
        (
            [
                "--device",
                "fvp-morello-android",
                *FVP_MORELLO_ANDROID,
                "--tests",
                "binder",
            ],
            "fvp-morello-android-binder.yaml",
        ),
        (
            [
                "--device",
                "fvp-morello-android",
                *FVP_MORELLO_ANDROID,
                "--tests",
                "bionic",
            ],
            "fvp-morello-android-bionic.yaml",
        ),
        (
            [
                "--device",
                "fvp-morello-android",
                *FVP_MORELLO_ANDROID,
                "--tests",
                "bionic",
                "--parameters",
                "GTEST_FILTER=hello",
                "BIONIC_TEST_TYPE=dynamic",
            ],
            "fvp-morello-android-bionic-params.yaml",
        ),
        (
            [
                "--device",
                "fvp-morello-android",
                *FVP_MORELLO_ANDROID,
                "--tests",
                "boringssl",
                "--parameters",
                "SYSTEM_URL=system.tar.xz",
            ],
            "fvp-morello-android-boringssl.yaml",
        ),
        (
            [
                "--device",
                "fvp-morello-android",
                *FVP_MORELLO_ANDROID,
                "--tests",
                "boringssl",
                "--parameters",
                "SYSTEM_URL=system.tar.xz",
                "--timeouts",
                "boringssl=4212",
            ],
            "fvp-morello-android-boringssl-timeouts.yaml",
        ),
        (
            [
                "--device",
                "fvp-morello-android",
                *FVP_MORELLO_ANDROID,
                "--tests",
                "compartment",
                "--parameters",
                "USERDATA=userdata.tar.xz",
            ],
            "fvp-morello-android-compartment.yaml",
        ),
        (
            [
                "--device",
                "fvp-morello-android",
                *FVP_MORELLO_ANDROID,
                "--tests",
                "device-tree",
            ],
            "fvp-morello-android-device-tree.yaml",
        ),
        (
            [
                "--device",
                "fvp-morello-android",
                *FVP_MORELLO_ANDROID,
                "--tests",
                "dvfs",
            ],
            "fvp-morello-android-dvfs.yaml",
        ),
        (
            [
                "--device",
                "fvp-morello-android",
                *FVP_MORELLO_ANDROID,
                "--tests",
                "libjpeg-turbo",
                "--parameters",
                "SYSTEM_URL=system.tar.xz",
                "LIBJPEG_TURBO_URL=libjpeg.tar.xz",
            ],
            "fvp-morello-android-libjpeg-turbo.yaml",
        ),
        (
            [
                "--device",
                "fvp-morello-android",
                *FVP_MORELLO_ANDROID,
                "--tests",
                "libpdfium",
                "--parameters",
                "SYSTEM_URL=system.tar.xz",
                "PDFIUM_URL=pdfium.tar.xz",
            ],
            "fvp-morello-android-libpdfium.yaml",
        ),
        (
            [
                "--device",
                "fvp-morello-android",
                *FVP_MORELLO_ANDROID,
                "--tests",
                "libpng",
                "--parameters",
                "SYSTEM_URL=system.tar.xz",
                "PNG_URL=png.tar.xz",
            ],
            "fvp-morello-android-libpng.yaml",
        ),
        (
            [
                "--device",
                "fvp-morello-android",
                *FVP_MORELLO_ANDROID,
                "--tests",
                "lldb",
                "--parameters",
                "LLDB_URL=lldb.tar.xz",
                "TC_URL=toolchain.tar.xz",
            ],
            "fvp-morello-android-lldb.yaml",
        ),
        (
            [
                "--device",
                "fvp-morello-android",
                *FVP_MORELLO_ANDROID,
                "--tests",
                "logd",
                "--parameters",
                "USERDATA=userdata.tar.xz",
            ],
            "fvp-morello-android-logd.yaml",
        ),
        (
            [
                "--device",
                "fvp-morello-android",
                *FVP_MORELLO_ANDROID,
                "--tests",
                "multicore",
            ],
            "fvp-morello-android-multicore.yaml",
        ),
        (
            [
                "--device",
                "fvp-morello-android",
                *FVP_MORELLO_ANDROID,
                "--tests",
                "zlib",
                "--parameters",
                "SYSTEM_URL=system.tar.xz",
            ],
            "fvp-morello-android-zlib.yaml",
        ),
        (
            [
                "--device",
                "fvp-morello-busybox",
                "--ap-romfw",
                "tf-bl1.bin",
                "--mcp-fw",
                "mcp_fw.bin",
                "--mcp-romfw",
                "mcp_romfw.bin",
                "--rootfs",
                "busybox.img.xz",
                "--scp-fw",
                "scp_fw.bin",
                "--scp-romfw",
                "scp_romfw.bin",
                "--fip",
                "fip.bin",
            ],
            "fvp-morello-busybox.yaml",
        ),
        (
            [
                "--device",
                "fvp-morello-busybox",
                "--ap-romfw",
                "tf-bl1.bin",
                "--mcp-fw",
                "mcp_fw.bin",
                "--mcp-romfw",
                "mcp_romfw.bin",
                "--rootfs",
                "busybox.img.xz",
                "--scp-fw",
                "scp_fw.bin",
                "--scp-romfw",
                "scp_romfw.bin",
                "--fip",
                "fip.bin",
                "--tests",
                "purecap",
            ],
            "fvp-morello-busybox-purecap.yaml",
        ),
        (
            [
                "--device",
                "fvp-morello-oe",
                "--ap-romfw",
                "tf-bl1.bin",
                "--mcp-fw",
                "mcp_fw.bin",
                "--mcp-romfw",
                "mcp_romfw.bin",
                "--rootfs",
                "core-image-minimal-morello-fvp.wic",
                "--scp-fw",
                "scp_fw.bin",
                "--scp-romfw",
                "scp_romfw.bin",
                "--fip",
                "fip.bin",
            ],
            "fvp-morello-oe.yaml",
        ),
        (
            [
                "--device",
                "fvp-morello-ubuntu",
                "--ap-romfw",
                "tf-bl1.bin",
                "--mcp-fw",
                "mcp_fw.bin",
                "--mcp-romfw",
                "mcp_romfw.bin",
                "--scp-fw",
                "scp_fw.bin",
                "--scp-romfw",
                "scp_romfw.bin",
                "--fip",
                "fip.bin",
            ],
            "fvp-morello-ubuntu.yaml",
        ),
        (
            ["--tuxmake", "."],
            "tuxmake.yaml",
        ),
    ],
)
def test_definition(monkeypatch, mocker, tmpdir, artefacts, args, filename):
    monkeypatch.setattr("tuxrun.__main__.sys.argv", ["tuxrun"] + args)
    mocker.patch("tuxrun.__main__.Runtime.select", side_effect=Exception)
    mocker.patch("tuxrun.assets.__download_and_cache__", side_effect=lambda a, b: a)
    mocker.patch("tuxrun.__main__.get_test_definitions", return_value="testdef.tar.zst")
    mocker.patch("tempfile.mkdtemp", return_value=tmpdir)
    mocker.patch("shutil.rmtree")

    with pytest.raises(Exception):
        main()
    data = (tmpdir / "definition.yaml").read_text(encoding="utf-8")

    for art in ARTEFACTS:
        data = data.replace(f"file://{artefacts}/{art}", f"/DATA/{art}")
    data = data.replace(
        f'container_name: "{artefacts.name}"', 'container_name: "tuxrun-ci"'
    )
    data = data.replace(
        f'network_from: "{artefacts.name}"', 'network_from: "tuxrun-ci"'
    )

    if os.environ.get("TUXRUN_RENDER"):
        (BASE / "refs" / "definitions" / filename).write_text(data, encoding="utf-8")
    assert data == (BASE / "refs" / "definitions" / filename).read_text(
        encoding="utf-8"
    )
