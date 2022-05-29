from typer.testing import CliRunner
from cryptcli import app

runner = CliRunner()

def test_list():
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert result.stdout.count("\n") == 10

    result = runner.invoke(app, ["list", "--num", "20"])
    assert result.exit_code == 0
    assert result.stdout.count("\n") == 20

def test_price():
    result = runner.invoke(app, ["price", "solana"])
    assert result.exit_code == 0

def test_info():
    result = runner.invoke(app, ["info", "litecoin"])
    assert result.exit_code == 0
    
