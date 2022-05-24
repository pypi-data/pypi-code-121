from re_common.baselibrary import BaseDicts
from re_common.baselibrary.utils.mfaker import MFaker


def test_basedict_sortkeys():
    fake = MFaker()
    dicts = fake.create_data(MFaker.m_pydict, **fake.py_para())
    print(dicts)
    dicts2 = BaseDicts.sortkeys(dicts)
    print(dicts2)
    print(dicts)


def test_basedict_sortvalues():
    dicts = {'data': 'FDZqqOGNMyGJlNRoCsJd', 'participant': 'petersonadrienne@bennett.com',
             'often': 'KnJSSDeSTPboiwjSdGwR', 'friend': '1639', 'above': '8144', 'in': '1614'}
    dicts2 = BaseDicts.sortvalues(dicts)
    print(dicts2)

