import shutil
from pathlib import Path

from . import Machine

test_dir = Path("/tmp/understory-web.host-test")


def setup_module(module):
    try:
        shutil.rmtree(test_dir)
    except FileNotFoundError:
        pass


def test_machine():
    machine = Machine()
    assert machine.run(f"mkdir {test_dir}").returncode == 0
    assert machine.run(f"ls {test_dir} -1").returncode == 0


def test_cd():
    machine = Machine()
    with machine.cd(test_dir) as root_dir:
        root_dir.run("mkdir foobar").returncode == 0
        with root_dir.cd("foobar") as foobar_dir:
            foobar_dir.run("mkdir batbaz").returncode == 0
            with foobar_dir.cd("batbaz") as batbaz_dir:
                batbaz_dir.run("mkdir a b c").returncode == 0
                assert batbaz_dir.run("ls -1").lines[:3] == ["a", "b", "c"]
    assert (test_dir / "foobar/batbaz/a").exists()
