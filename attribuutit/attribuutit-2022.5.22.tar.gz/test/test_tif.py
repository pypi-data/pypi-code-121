import pathlib

import attribuutit.tif as tif

TIF_ROOT = pathlib.Path('local', 'incoming')


def test_tif_load(capsys):
    path = TIF_ROOT / 'GRAY_50M_SR_OB.tif'
    result = tif.load(path)
    assert result is None
    out, err = capsys.readouterr()
    assert 'crs_name: WGS_84 (code 4326)' in out
