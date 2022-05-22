from typer.testing import CliRunner

from attribuutit.cli import app

runner = CliRunner()


def test_app():
    non_existing_command = 'uncommand'
    result = runner.invoke(app, [non_existing_command, '--city', 'Oslo'])
    assert result.exit_code == 2
    assert 'Usage: ' in result.stdout
    assert f"Error: No such command '{non_existing_command}'." in result.stdout


def test_app_eject():
    eject_cmd = 'eject'
    result = runner.invoke(app, [eject_cmd, 'stem'])
    assert result.exit_code == 0
    assert 'This will eject an example configuration as stem.json' in result.stdout


def test_app_scan():
    scan_cmd = 'scan'
    result = runner.invoke(app, [scan_cmd, 'stem'])
    assert result.exit_code == 0
    assert 'Real run changing the world following the configuration stem.json - later' in result.stdout


def test_app_scan_dry():
    scan_cmd = 'scan'
    result = runner.invoke(app, [scan_cmd, '--dry-run', 'stem'])
    assert result.exit_code == 0
    assert 'Dry run exposing the plan of execution when following the configuration stem.json - later' in result.stdout


def test_app_inspect_vpf():
    inspect_cmd = 'inspect'
    path_str = 'local/incoming/scenario/42/libref/txt'
    result = runner.invoke(app, [inspect_cmd, '--no-dry-run', path_str])
    assert result.exit_code == 0
    assert 'Real run ' in result.stdout
    assert f' inspecting file at {path_str}' in result.stdout
    assert '9876543210' in result.stdout


def test_app_inspect_shp():
    inspect_cmd = 'inspect'
    path_str = 'local/incoming/ne_110m_admin_0_tiny_countries.shp'
    result = runner.invoke(app, [inspect_cmd, path_str])
    assert result.exit_code == 0
    assert 'Real run ' in result.stdout
    assert f' inspecting file at {path_str}' in result.stdout
    assert '37 records (171 fields)' in result.stdout


def test_app_inspect_tif():
    inspect_cmd = 'inspect'
    path_str = 'local/incoming/GRAY_50M_SR_OB.tif'
    result = runner.invoke(app, [inspect_cmd, '--no-dry-run', path_str])
    assert result.exit_code == 0
    assert 'Real run ' in result.stdout
    assert f' inspecting file at {path_str}' in result.stdout
    assert 'crs_name: WGS_84 (code 4326)\nbbox: ((' in result.stdout


def test_app_inspect_dry():
    inspect_cmd = 'inspect'
    result = runner.invoke(app, [inspect_cmd, '--dry-run', 'Oslo'])
    assert result.exit_code == 0
    assert 'Dry run exposing ' in result.stdout
    assert ' inspecting file at Oslo' in result.stdout
