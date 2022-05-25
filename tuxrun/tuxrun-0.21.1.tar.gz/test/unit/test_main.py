import json
import pytest
import os
import yaml

import tuxrun.__main__
from tuxrun.__main__ import start, main


def touch(directory, name):
    f = directory / name
    f.touch()
    return f


@pytest.fixture
def artefacts(tmp_path):
    os.chdir(tmp_path)
    touch(tmp_path, "arm.dtb")
    touch(tmp_path, "device.yaml")
    touch(tmp_path, "definition.yaml")
    touch(tmp_path, "bios.bin")
    touch(tmp_path, "bzImage")
    touch(tmp_path, "stuff.tar.gz")
    touch(tmp_path, "morestuff.tar.gz")
    touch(tmp_path, "fvp.bin")
    touch(tmp_path, "foo.tar.xz")
    touch(tmp_path, "modules.tar")
    return tmp_path


@pytest.fixture
def device(tmp_path):
    return touch(tmp_path, "device.yaml")


@pytest.fixture
def job(tmp_path):
    return touch(tmp_path, "job.yaml")


@pytest.fixture
def run(mocker):
    return mocker.patch("tuxrun.__main__.run")


@pytest.fixture
def tuxrun_args(monkeypatch, device, job):
    args = ["tuxrun", "--device-dict", str(device), "--definition", str(job)]
    monkeypatch.setattr("sys.argv", args)
    return args


@pytest.fixture
def tuxrun_args_generate(monkeypatch):
    args = [
        "tuxrun",
        "--device",
        "qemu-i386",
        "--kernel",
        "https://storage.tuxboot.com/i386/bzImage",
    ]
    monkeypatch.setattr("sys.argv", args)
    return args


@pytest.fixture
def lava_run_call(mocker):
    return mocker.patch("subprocess.Popen")


@pytest.fixture
def lava_run(lava_run_call, mocker):
    mocker.patch("tuxrun.results.Results.ret", return_value=0)
    proc = lava_run_call.return_value
    proc.wait.return_value = 0
    proc.communicate.return_value = (mocker.MagicMock(), mocker.MagicMock())
    return proc


def test_start_calls_main(monkeypatch, mocker):
    monkeypatch.setattr(tuxrun.__main__, "__name__", "__main__")
    main = mocker.patch("tuxrun.__main__.main")
    with pytest.raises(SystemExit):
        start()
    main.assert_called()


def test_main_usage(monkeypatch, capsys, run):
    monkeypatch.setattr("tuxrun.__main__.sys.argv", ["tuxrun"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
    _, err = capsys.readouterr()
    assert "usage: tuxrun" in err


def test_almost_real_run(tuxrun_args, lava_run, capsys):
    lava_run.stderr = [
        '{"lvl": "info", "msg": "Hello, world", "dt": "2021-04-08T18:42:25.139513"}\n'
    ]
    exitcode = main()
    assert exitcode == 0
    stdout, _ = capsys.readouterr()
    assert "Hello, world" in stdout


FVP_MORELLO_ARGS = [
    "--ap-romfw",
    "fvp.bin",
    "--mcp-fw",
    "fvp.bin",
    "--mcp-romfw",
    "fvp.bin",
    "--rootfs",
    "fvp.bin",
    "--scp-fw",
    "fvp.bin",
    "--scp-romfw",
    "fvp.bin",
    "--fip",
    "fvp.bin",
]


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["--device", "qemu-armv7", "--device-dict", "device.yaml"],
        ["--device", "qemu-armv7", "--boot-args", 'bla"bl'],
        ["--device", "qemu-armv7", "--dtb", "arm.dtb"],
        ["--device", "qemu-arm64", "--bios", "bios.bin"],
        ["--device", "qemu-arm64", "--modules", "modules.tar"],
        ["--kernel", "https://storage.tuxboot.com/i386/bzImage"],
        ["--device-dict", "device.yaml"],
        ["--definition", "definition.yaml"],
        ["--device", "fvp-aemva", "--mcp-fw", "fvp.bin"],
        ["--device", "fvp-aemva", "--modules", "modules.tar"],
        ["--device", "fvp-morello-android", "--mcp-fw", "fvp.bin"],
        ["--device", "fvp-morello-android", "--test", "multicore"],
        [
            "--device",
            "fvp-morello-android",
            *FVP_MORELLO_ARGS,
            "--tests",
            "bionic",
            "--parameters",
            "BIONIC_TEST_TYPE=invalid",
        ],
        ["--device", "fvp-morello-android", *FVP_MORELLO_ARGS, "--tests", "lldb"],
        [
            "--device",
            "fvp-morello-busybox",
            *FVP_MORELLO_ARGS,
            "--tests",
            "libjpeg-turbo",
        ],
        ["--device", "fvp-morello-busybox", *FVP_MORELLO_ARGS, "--tests", "libpng"],
        ["--device", "fvp-morello-busybox", *FVP_MORELLO_ARGS, "--tests", "libpdfium"],
        ["--device", "fvp-morello-busybox", *FVP_MORELLO_ARGS, "--tests", "zlib"],
        ["--device", "fvp-morello-busybox", *FVP_MORELLO_ARGS, "--tests", "boringssl"],
        [
            "--device",
            "fvp-morello-busybox",
            *FVP_MORELLO_ARGS,
            "--kernel",
            "https://storage.tuxboot.com/i386/bzImage",
        ],
        ["--device", "fvp-morello-ubuntu", *FVP_MORELLO_ARGS],
        [
            "--device",
            "fvp-morello-ubuntu",
            "--ap-romfw",
            "fvp.bin",
            "--mcp-fw",
            "fvp.bin",
            "--mcp-romfw",
            "fvp.bin",
            "--scp-fw",
            "fvp.bin",
            "--scp-romfw",
            "fvp.bin",
            "--fip",
            "fvp.bin",
            "--tests",
            "lldb",
        ],
        [
            "--device",
            "fvp-morello-android",
            *FVP_MORELLO_ARGS,
            "--tests",
            "lldb",
            "--parameters",
            "LLDB_URL=http://example.com/lldb.tar.xz",
        ],
        [
            "--device",
            "fvp-morello-android",
            *FVP_MORELLO_ARGS,
            "--tests",
            "libpng",
            "--parameters",
            "SYSTEM_URL=http://example.com/system.tar.xz",
        ],
        [
            "--device",
            "fvp-morello-android",
            *FVP_MORELLO_ARGS,
            "--tests",
            "libjpeg-turbo",
            "--parameters",
            "SYSTEM_URL=http://example.com/system.tar.xz",
        ],
        [
            "--device",
            "fvp-morello-android",
            *FVP_MORELLO_ARGS,
            "--tests",
            "libpdfium",
            "--parameters",
            "SYSTEM_URL=http://example.com/system.tar.xz",
        ],
        [
            "--device",
            "fvp-morello-android",
            *FVP_MORELLO_ARGS,
            "--tests",
            "libpdfium",
            "--parameters",
            "PDF_URL=http://example.com/pdfium-testfiles.tar.xz",
        ],
        [
            "--device",
            "fvp-morello-android",
            *FVP_MORELLO_ARGS,
            "--tests",
            "ltp-smoke",
        ],
        [
            "--device",
            "fvp-morello-android",
            *FVP_MORELLO_ARGS,
            "--tests",
            "kselftest",
        ],
        ["--device", "qemu-arm64", "--tests", "ltp-smoke", "ltp-smoke"],
    ],
)
def test_command_line_errors(argv, capsys, monkeypatch, mocker, artefacts):
    monkeypatch.setattr("tuxrun.__main__.sys.argv", ["tuxrun"] + argv)
    run = mocker.patch("tuxrun.__main__.run", return_value=0)
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
    stdout, stderr = capsys.readouterr()
    assert "usage: tuxrun" in stderr
    assert "tuxrun: error:" in stderr
    run.assert_not_called()


def test_command_line_parameters(monkeypatch, mocker, artefacts):
    monkeypatch.setattr(
        "tuxrun.__main__.sys.argv",
        [
            "tuxrun",
            "--device",
            "fvp-morello-android",
            "--ap-romfw",
            "fvp.bin",
            "--mcp-fw",
            "fvp.bin",
            "--mcp-romfw",
            "fvp.bin",
            "--rootfs",
            "fvp.bin",
            "--scp-fw",
            "fvp.bin",
            "--scp-romfw",
            "fvp.bin",
            "--fip",
            "fvp.bin",
            "--parameters",
            "USERDATA=http://userdata.tar.xz",
        ],
    )
    run = mocker.patch("tuxrun.__main__.run", return_value=0)
    exitcode = main()
    assert exitcode == 0
    assert len(run.call_args.args) == 2
    print(run.call_args.parameters)
    assert run.call_args[0][0].parameters == {"USERDATA": "http://userdata.tar.xz"}


def test_almost_real_run_generate(tuxrun_args_generate, lava_run, capsys):
    lava_run.stderr = [
        '{"lvl": "info", "msg": "Hello, world", "dt": "2021-04-08T18:42:25.139513"}\n'
    ]
    exitcode = main()
    assert exitcode == 0
    stdout, _ = capsys.readouterr()
    assert "Hello, world" in stdout


def test_ignores_empty_line_from_lava_run_stdout(tuxrun_args, lava_run):
    lava_run.stderr = [
        '{"lvl": "info", "msg": "Hello, world", "dt": "2021-04-08T18:42:25.139513"}\n',
        "",
        '{"lvl": "info", "msg": "Hello, world", "dt": "2021-04-08T18:42:26.139513"}\n',
    ]
    exitcode = main()
    assert exitcode == 0


def test_ignores_empty_line_from_lava_run_logfile(tuxrun_args, lava_run, tmp_path):
    log = tmp_path / "log.yaml"
    tuxrun_args += ["--log", str(log)]
    lava_run.stderr = [
        '{"lvl": "info", "msg": "Hello, world", "dt": "2021-04-08T18:42:25.139513"}\n',
        "",
        '{"lvl": "info", "msg": "Hello, world", "dt": "2021-04-08T18:42:26.139513"}\n',
    ]
    exitcode = main()
    assert exitcode == 0
    logdata = yaml.safe_load(log.open())
    assert type(logdata[0]) is dict
    assert type(logdata[1]) is dict


def test_exit_status_is_0_on_success(tuxrun_args, lava_run):
    assert main() == 0


def test_exit_status_matches_results(tuxrun_args, lava_run, mocker):
    mocker.patch("tuxrun.results.Results.ret", return_value=1)
    assert main() == 1


def test_tuxbuild(get, monkeypatch, mocker, run):
    data = json.dumps(
        {
            "results": {
                "artifacts": {"kernel": ["bzImage"], "modules": ["modules.tar.xz"]},
            },
            "build": {"target_arch": "x86_64"},
        }
    )
    mocker.patch("tuxrun.__main__.get_rootfs", return_value="https://example.com")
    get.side_effect = [mocker.Mock(status_code=200, text=data)]
    monkeypatch.setattr("sys.argv", ["tuxrun", "--tuxbuild", "https://example.com"])

    main()
    run.assert_called()
    options = run.call_args[0][0]
    assert options.kernel == "https://example.com/bzImage"
    assert options.modules == "https://example.com/modules.tar.xz"
    assert options.device.name == "qemu-x86_64"
    assert options.dtb is None


def test_tuxbuild_armv5(get, monkeypatch, mocker, run):
    data = json.dumps(
        {
            "results": {
                "artifacts": {"kernel": ["bzImage"], "modules": ["modules.tar.xz"]},
            },
            "build": {"target_arch": "arm"},
        }
    )
    mocker.patch("tuxrun.__main__.get_rootfs", return_value="https://example.com")
    get.side_effect = [mocker.Mock(status_code=200, text=data)]
    monkeypatch.setattr(
        "sys.argv",
        ["tuxrun", "--tuxbuild", "https://example.com", "--device", "qemu-armv5"],
    )

    main()
    run.assert_called()
    options = run.call_args[0][0]
    assert options.kernel == "https://example.com/bzImage"
    assert options.modules == "https://example.com/modules.tar.xz"
    assert options.device.name == "qemu-armv5"
    assert options.dtb == "https://example.com/dtbs/versatile-pb.dtb"


def test_tuxmake_directory(monkeypatch, tmp_path, run):
    tuxmake_build = tmp_path / "build"
    tuxmake_build.mkdir()
    (tuxmake_build / "metadata.json").write_text(
        """
        {
            "results": {
                "artifacts": {"kernel": ["bzImage"], "modules": ["modules.tar.xz"]}
            },
            "build": {"target_arch": "x86_64"}
        }
        """
    )
    monkeypatch.setattr("sys.argv", ["tuxrun", "--tuxmake", str(tuxmake_build)])

    main()
    run.assert_called()
    options = run.call_args[0][0]
    assert options.kernel == f"file://{tuxmake_build}/bzImage"
    assert options.modules == f"file://{tuxmake_build}/modules.tar.xz"
    assert options.device.name == "qemu-x86_64"
    assert options.dtb is None


def test_tuxmake_directory_armv5(monkeypatch, tmp_path, run):
    tuxmake_build = tmp_path / "build"
    tuxmake_build.mkdir()
    (tuxmake_build / "metadata.json").write_text(
        """
        {
            "results": {
                "artifacts": {"kernel": ["zImage"], "modules": ["modules.tar.xz"]}
            },
            "build": {"target_arch": "arm"}
        }
        """
    )
    monkeypatch.setattr(
        "sys.argv",
        ["tuxrun", "--tuxmake", str(tuxmake_build), "--device", "qemu-armv5"],
    )

    main()
    run.assert_called()
    options = run.call_args[0][0]
    assert options.kernel == f"file://{tuxmake_build}/zImage"
    assert options.modules == f"file://{tuxmake_build}/modules.tar.xz"
    assert options.device.name == "qemu-armv5"
    assert options.dtb is None

    (tuxmake_build / "dtbs").mkdir()
    (tuxmake_build / "dtbs" / "versatile-pb.dtb").write_text("")
    main()
    run.assert_called()
    options = run.call_args[0][0]
    assert options.kernel == f"file://{tuxmake_build}/zImage"
    assert options.modules == f"file://{tuxmake_build}/modules.tar.xz"
    assert options.device.name == "qemu-armv5"
    assert options.dtb == f"file://{tuxmake_build}/dtbs/versatile-pb.dtb"


def test_no_modules(monkeypatch, tmp_path, run):
    tuxmake_build = tmp_path / "build"
    tuxmake_build.mkdir()
    (tuxmake_build / "metadata.json").write_text(
        """
        {
            "results": {
                "artifacts": {"kernel": ["bzImage"]}
            },
            "build": {"target_arch": "x86_64"}
        }
        """
    )
    monkeypatch.setattr("sys.argv", ["tuxrun", "--tuxmake", str(tuxmake_build)])

    main()
    run.assert_called()
    options = run.call_args[0][0]
    assert options.modules is None


def test_invalid_tuxmake_directory(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr("sys.argv", ["tuxrun", "--tuxmake", str(tmp_path)])
    with pytest.raises(SystemExit) as exit:
        main()
        assert exit.status_code != 0
    _, err = capsys.readouterr()
    assert "metadata.json" in err


def test_modules(monkeypatch, lava_run_call, lava_run, artefacts):
    monkeypatch.setattr(
        "sys.argv",
        [
            "tuxrun",
            "--kernel=bzImage",
            "--device=qemu-x86_64",
            "--modules=foo.tar.xz",
        ],
    )
    assert main() == 0
    lava_run_call.assert_called()
    args = lava_run_call.call_args[0][0]
    assert f"{artefacts}/foo.tar.xz:{artefacts}/foo.tar.xz:ro" in args


def test_overlays(monkeypatch, lava_run_call, lava_run, artefacts):
    monkeypatch.setattr(
        "sys.argv",
        [
            "tuxrun",
            "--kernel=bzImage",
            "--device=qemu-x86_64",
            "--overlay=stuff.tar.gz",
            "--overlay=morestuff.tar.gz",
        ],
    )
    assert main() == 0
    lava_run_call.assert_called()
    args = lava_run_call.call_args[0][0]
    assert f"{artefacts}/stuff.tar.gz:{artefacts}/stuff.tar.gz:ro" in args
    assert f"{artefacts}/morestuff.tar.gz:{artefacts}/morestuff.tar.gz:ro" in args


def test_custom_commands(monkeypatch, run):
    monkeypatch.setattr(
        "sys.argv",
        ["tuxrun", "--kernel=bzImage", "--device=qemu-x86_64", "cat", "/etc/hostname"],
    )
    main()
    run.assert_called()
    options = run.call_args[0][0]
    assert len(options.tests) == 1
    assert options.tests[0].name == "command"
    assert options.command == ["cat", "/etc/hostname"]


def test_list_devices(mocker, monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        ["tuxrun", "--list-devices"],
    )
    with pytest.raises(SystemExit):
        main()
    stdout, stderr = capsys.readouterr()
    assert stderr == ""
    assert "qemu-i386" in stdout


def test_list_tests(mocker, monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        ["tuxrun", "--list-tests"],
    )
    with pytest.raises(SystemExit):
        main()
    stdout, stderr = capsys.readouterr()
    assert stderr == ""
    assert "ltp-smoke" in stdout


def test_update_cache(mocker, monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        ["tuxrun", "--update-cache"],
    )
    with pytest.raises(SystemExit):
        main()
    stdout, stderr = capsys.readouterr()
    assert (
        stdout
        == """Updating local cache:
* Rootfs:
  * fvp-aemva
  * qemu-arm64
  * qemu-arm64be
  * qemu-armv5
  * qemu-armv7
  * qemu-armv7be
  * qemu-i386
  * qemu-mips32
  * qemu-mips32el
  * qemu-mips64
  * qemu-mips64el
  * qemu-ppc32
  * qemu-ppc64
  * qemu-ppc64le
  * qemu-riscv64
  * qemu-s390
  * qemu-sh4
  * qemu-sparc64
  * qemu-x86_64
* Test definitions
"""
    )


def test_save_results_json(tuxrun_args, lava_run, mocker, tmp_path):
    json = tmp_path / "results.json"
    tuxrun_args += [f"--results={json}"]
    main()
    assert json.read_text().strip() == "{}"


def test_timeouts(monkeypatch, run):
    monkeypatch.setattr(
        "sys.argv",
        [
            "tuxrun",
            "--device=qemu-x86_64",
            "--tests",
            "ltp-smoke",
            "--timeouts",
            "boot=1",
            "ltp-smoke=12",
        ],
    )
    main()
    run.assert_called()
    options = run.call_args[0][0]
    assert len(options.tests) == 1
    assert options.tests[0].name == "ltp-smoke"
    assert options.tests[0].timeout == 12
    assert options.timeouts == {"boot": 1, "ltp-smoke": 12}
