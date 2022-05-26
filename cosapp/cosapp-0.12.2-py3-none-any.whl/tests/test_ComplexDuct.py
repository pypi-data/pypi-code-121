import pytest

from cosapp.drivers import RunOnce, NonLinearSolver
from cosapp.tests.library.systems import ComplexDuct


def test_ComplexDuct():
    s = ComplexDuct("MyComplexDuct")

    s.fl_in.W = 100
    s.fl_in.Pt = 1020.408163265
    s.fl_in.Tt = 50.
    s.run_once()

    s.bleed.fl2_out.Pt = 1000

    s.add_driver(RunOnce("first run"))
    s.add_driver(NonLinearSolver("design"))
    s.run_drivers()
    assert s.bleed.fl2_out.W == pytest.approx(100 / 99, rel=1e-5)
    assert s.merger.fl2_in.W == pytest.approx(100 / 99, rel=1e-5)
    assert s.bleed.fl2_out.Pt == pytest.approx(1000, rel=1e-5)
    assert s.merger.fl2_in.Pt == pytest.approx(1000, rel=1e-5)
