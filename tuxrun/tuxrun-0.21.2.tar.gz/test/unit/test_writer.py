from tuxrun.writer import Writer


def test_write_log_file(tmp_path):
    log_file = tmp_path / "logs.yaml"
    with Writer(log_file) as writer:
        writer.write(
            '{"lvl": "info", "msg": "Hello, world", "dt": "2021-04-08T18:42:25.139513"}'
        )

    log_file.read_text(
        encoding="utf-8"
    ) == '{"lvl": "info", "msg": "Hello, world", "dt": "2021-04-08T18:42:25.139513"}\n'


def test_write_stdout(capsys):
    with Writer(None) as writer:
        writer.write(
            '{"lvl": "info", "msg": "Hello, world", "dt": "2021-04-08T18:42:25.139513"}'
        )

    out, err = capsys.readouterr()
    assert "\x1b[0m \x1b[1;37mHello, world\x1b[0m\n" in out


def test_write_stdout_feedback(capsys):
    with Writer(None) as writer:
        writer.write(
            '{"lvl": "feedback", "msg": "Hello, world", "dt": "2021-04-08T18:42:25.139513", "ns": "testing"}'
        )

    out, err = capsys.readouterr()
    assert "\x1b[0m <\x1b[0;33mtesting\x1b[0m> \x1b[0;33mHello, world\x1b[0m\n" in out


def test_writer_invalid_yaml(capsys, tmpdir):
    data = '{"lvl": "feedback", "msg": "Hello, world", "dt": "2021-04-08T18:42:25.139513", "ns": "testing"}'
    with Writer(tmpdir / "logs.yaml") as writer:
        writer.write("{")
        writer.write("hello world")
        writer.write("{}")
        writer.write(data)
        writer.write("{hello: world}")
    out, err = capsys.readouterr()
    assert (
        out
        == """{
hello world
{}
{hello: world}
"""
    )
    assert err == ""
    assert (tmpdir / "logs.yaml").read_text(encoding="utf-8") == f"- {data}\n"
