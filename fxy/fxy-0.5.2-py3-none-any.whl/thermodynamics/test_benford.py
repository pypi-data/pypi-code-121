from fxy.thermodynamics.benford import n_probability


def test_n_probability():
    res = (n_probability.subs({'digits': 1})).n()
    assert float(res) == 0.6931471805599453

