import pathlib

import attribuutit.shp as shp

SHP_ROOT = pathlib.Path('local', 'incoming')


def test_shp_load(capsys):
    path = SHP_ROOT / 'ne_110m_admin_0_tiny_countries.shp'
    result = shp.load(path)
    assert result is None
    out, err = capsys.readouterr()
    assert 'bbox: ' in out
