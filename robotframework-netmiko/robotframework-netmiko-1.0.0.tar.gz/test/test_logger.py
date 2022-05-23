import io
from contextlib import redirect_stdout
from src.NetmikoLibrary.loggers import HtmlLogger


def test_cli(mock_logger):
    command = "show version"
    message = "test message"
    f = io.StringIO()
    with redirect_stdout(f):
        logger = HtmlLogger()
        logger.cli("192.168.0.1", command, message)

    output = f.getvalue()
    assert 'style' in output
    assert 'code.cli' in output
    assert command in output
    assert message in output


def test_cli_parse(mock_logger):
    command = "show version"
    message = "test message"
    ttp = "ttp template"
    var_value = "abc"
    f = io.StringIO()
    with redirect_stdout(f):
        logger = HtmlLogger()
        logger.cli_parse("192.168.0.1", command, message, ttp, {"server": var_value})

    output = f.getvalue()
    assert command in output
    assert message in output
    assert ttp in output
    assert var_value in output
