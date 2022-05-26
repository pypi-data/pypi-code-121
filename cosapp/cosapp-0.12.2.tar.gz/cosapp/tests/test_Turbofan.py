import pytest

from cosapp.drivers import NonLinearMethods, NonLinearSolver
from cosapp.tests.library.systems import (
    SimpleTurbofan,
    AdvancedTurbofan,
    ComplexTurbofan,
)


def test_SimpleTurbofan_set_inputs():
    s = SimpleTurbofan("MySimpleTurbofan")

    s.exec_order = ["atm", "inlet", "fan", "duct", "noz"]
    s.duct.inwards.cst_loss = 0.98

    design = s.add_driver(NonLinearSolver("design"))
    design.runner.offdesign.add_unknown("fan.mech_in.PW")

    s.fan.mech_in.XN = 80
    # test inlet XN value
    assert s.fan.mech_in.XN == 80.0
    assert s.duct.inwards.cst_loss == 0.98


def test_SimpleTurbofan_running_80():
    s = SimpleTurbofan("MySimpleTurbofan")

    s.exec_order = ["atm", "inlet", "fan", "duct", "noz"]
    s.duct.inwards.cst_loss = 0.98

    design = s.add_driver(NonLinearSolver("design"))
    design.runner.offdesign.add_unknown("fan.mech_in.PW")

    s.fan.mech_in.XN = 80
    s.run_drivers()
    assert s.fan.mech_in.XN == 80.0
    assert s.fan.gh == pytest.approx(0.0385792701, rel=1e-5)
    assert s.fan.mech_in.PW == pytest.approx(8279856, rel=1e-5)
    # a second run changes fan power because of poor fsolve behavior
    # first run gives fan power residue bigger than 1e-5
    assert s.inlet.W_in.W == pytest.approx(161.463, rel=1e-4)


def test_SimpleTurbofan_running_100():
    s = SimpleTurbofan("MySimpleTurbofan")

    s.exec_order = ["atm", "inlet", "fan", "duct", "noz"]
    s.duct.inwards.cst_loss = 0.98

    design = s.add_driver(NonLinearSolver("design"))
    design.runner.offdesign.add_unknown("fan.mech_in.PW")

    s.fan.mech_in.XN = 100
    s.run_drivers()

    assert s.fan.mech_in.XN == 100.0
    assert s.fan.gh == pytest.approx(0.1566921207, rel=1e-5)
    assert s.fan.mech_in.PW == pytest.approx(10874232, rel=1e-5)
    assert s.inlet.W_in.W == pytest.approx(177.034, rel=1e-5)


def test_AdvancedTurbofan_set_inputs():
    s = AdvancedTurbofan("MyAdvancedTurbofan")

    s.exec_order = ["atm", "inlet", "fan", "merger", "duct", "bleed", "noz"]
    s.duct.inwards.cst_loss = 0.98

    design = s.add_driver(NonLinearSolver("design"))
    design.runner.offdesign.add_unknown("fan.mech_in.PW")

    s.fan.mech_in.XN = 80
    # test inlet XN value
    assert s.fan.mech_in.XN == 80.0
    assert s.duct.inwards.cst_loss == 0.98


def test_AdvancedTurbofan_running_80():
    s = AdvancedTurbofan("MyAdvancedTurbofan")

    s.exec_order = ["atm", "inlet", "fan", "merger", "duct", "bleed", "noz"]
    s.duct.inwards.cst_loss = 0.98

    design = s.add_driver(NonLinearSolver("design"))
    design.add_unknown("fan.mech_in.PW")

    s.fan.mech_in.XN = 80
    s.run_drivers()
    assert s.fan.mech_in.XN == 80.0
    assert s.fan.gh == pytest.approx(0.038579270081290681, rel=1e-5)
    assert s.fan.mech_in.PW == pytest.approx(8279856, rel=1e-5)
    assert s.inlet.W_in.W == pytest.approx(161.463, rel=1e-5)

    assert s.bleed.fl2_out.W == pytest.approx(1.630942952, rel=1e-5)
    assert s.merger.fl2_in.W == pytest.approx(1.630942952, rel=1e-5)
    assert s.bleed.fl2_out.Pt == pytest.approx(180023, rel=1e-5)
    assert s.merger.fl2_in.Pt == pytest.approx(180023, rel=1e-5)
    assert s.bleed.fl2_out.Tt == pytest.approx(324.2258, rel=1e-5)
    assert s.merger.fl2_in.Tt == pytest.approx(324.2258, rel=1e-5)


def test_AdvancedTurbofan_running_100():
    s = AdvancedTurbofan("MyAdvancedTurbofan")

    s.exec_order = ["atm", "inlet", "fan", "merger", "duct", "bleed", "noz"]
    s.duct.inwards.cst_loss = 0.98

    design = s.add_driver(NonLinearSolver("design"))
    design.add_unknown("fan.mech_in.PW")

    s.fan.mech_in.XN = 100
    s.run_drivers()

    assert s.fan.mech_in.XN == 100.0
    assert s.fan.gh == pytest.approx(0.15669212068943689, rel=1e-5)
    assert s.fan.mech_in.PW == pytest.approx(10874232, rel=1e-5)
    assert s.inlet.W_in.W == pytest.approx(177.034, rel=1e-5)

    assert s.bleed.fl2_out.W == pytest.approx(1.7882221046, rel=1e-5)
    assert s.merger.fl2_in.W == pytest.approx(1.7882221046, rel=1e-5)
    assert s.bleed.fl2_out.Pt == pytest.approx(200435.4, rel=1e-5)
    assert s.merger.fl2_in.Pt == pytest.approx(200435.4, rel=1e-5)
    assert s.bleed.fl2_out.Tt == pytest.approx(334.330, rel=1e-5)
    assert s.merger.fl2_in.Tt == pytest.approx(334.330, rel=1e-5)


def test_ComplexTurbofan_set_inputs():
    s = ComplexTurbofan("MyComplexTurbofan")
    s.duct.inwards.cst_loss = 0.98
    s.fanC.ductC.duct.inwards.cst_loss = 0.98
    s.fanC.ductC.bleed.inwards.split_ratio = 0.995
    s.bleed.inwards.split_ratio = 0.99

    design = s.add_driver(NonLinearSolver("design", tol=1e-7))
    design.add_unknown("fanC.mech_in.PW")

    s.fanC.mech_in.XN = 80
    # test inlet XN value
    assert s.fanC.mech_in.XN == 80.0
    assert s.duct.inwards.cst_loss == 0.98
    assert s.fanC.ductC.duct.inwards.cst_loss == 0.98


def test_ComplexTurbofan_running_80():
    s = ComplexTurbofan("MyComplexTurbofan")
    s.duct.inwards.cst_loss = 0.98
    s.fanC.ductC.duct.inwards.cst_loss = 0.98
    s.fanC.ductC.bleed.inwards.split_ratio = 0.995
    s.bleed.inwards.split_ratio = 0.99

    design = s.add_driver(NonLinearSolver("design", tol=1e-7))
    design.add_unknown("fanC.mech_in.PW")

    s.fanC.mech_in.XN = 80
    s.run_drivers()
    assert s.fanC.mech_in.XN == 80.0
    assert s.fanC.gh == pytest.approx(0.03857927008129068, rel=1e-5)
    assert s.fanC.mech_in.PW == pytest.approx(8114258.93, rel=1e-5)
    assert s.inlet.W_in.W == pytest.approx(158.2341, rel=1e-5)

    assert s.bleed.fl2_out.W == pytest.approx(1.59832409, rel=1e-5)
    assert s.merger.fl2_in.W == pytest.approx(1.59832409, rel=1e-5)
    assert s.bleed.fl2_out.Pt == pytest.approx(176422.55, rel=1e-5)
    assert s.merger.fl2_in.Pt == pytest.approx(176422.55, rel=1e-5)
    assert s.bleed.fl2_out.Tt == pytest.approx(324.2258, rel=1e-5)
    assert s.merger.fl2_in.Tt == pytest.approx(324.2258, rel=1e-5)


def test_ComplexTurbofan_internal_loop_ductC_running_80():
    # Another run with an internal loop at ductC level
    s = ComplexTurbofan("MyComplexTurbofan")
    s.duct.inwards.cst_loss = 0.98
    s.fanC.ductC.duct.inwards.cst_loss = 0.98
    s.fanC.ductC.bleed.inwards.split_ratio = 0.995
    s.bleed.inwards.split_ratio = 0.99

    design = s.add_driver(NonLinearSolver("design", tol=1e-7))
    design.add_unknown("fanC.mech_in.PW")

    s.fanC.mech_in.XN = 80
    s.fanC.ductC.add_driver(NonLinearSolver("design", method=NonLinearMethods.POWELL))
    s.run_drivers()

    assert s.fanC.mech_in.XN == 80.0
    assert s.fanC.gh == pytest.approx(0.03857927008, rel=1e-5)
    assert s.fanC.mech_in.PW == pytest.approx(8114258.932, rel=1e-5)
    assert s.inlet.W_in.W == pytest.approx(158.2341, rel=1e-5)

    assert s.bleed.fl2_out.W == pytest.approx(1.59832409, rel=1e-5)
    assert s.merger.fl2_in.W == pytest.approx(1.59832409, rel=1e-5)
    assert s.bleed.fl2_out.Pt == pytest.approx(176422.55, rel=1e-5)
    assert s.merger.fl2_in.Pt == pytest.approx(176422.55, rel=1e-5)
    assert s.bleed.fl2_out.Tt == pytest.approx(324.2258, rel=1e-5)
    assert s.merger.fl2_in.Tt == pytest.approx(324.2258, rel=1e-5)

    assert s.fanC.ductC.bleed.fl2_out.W == pytest.approx(0.79514614358, rel=1e-5)
    assert s.fanC.ductC.merger.fl2_in.W == pytest.approx(0.79514614358, rel=1e-5)
    assert s.fanC.ductC.bleed.fl2_out.Pt == pytest.approx(98802.0075, rel=1e-5)
    assert s.fanC.ductC.merger.fl2_in.Pt == pytest.approx(98802.0075, rel=1e-5)
    assert s.fanC.ductC.bleed.fl2_out.Tt == pytest.approx(273.15, rel=1e-5)
    assert s.fanC.ductC.merger.fl2_in.Tt == pytest.approx(273.15, rel=1e-5)


def test_ComplexTurbofan_internal_loop_fanC_running_80():
    # Another run with an internal loop at fanC level
    s = ComplexTurbofan("MyComplexTurbofan")
    s.duct.inwards.cst_loss = 0.98
    s.fanC.ductC.duct.inwards.cst_loss = 0.98
    s.fanC.ductC.bleed.inwards.split_ratio = 0.995
    s.bleed.inwards.split_ratio = 0.99

    s.add_driver(NonLinearSolver("design", tol=1e-7))

    s.fanC.mech_in.XN = 80
    design = s.fanC.add_driver(NonLinearSolver("design", tol=1e-7))
    design.add_unknown("mech_in.PW")
    s.run_drivers()

    assert s.fanC.mech_in.XN == 80.0
    assert s.fanC.gh / 0.038579270081290681 == pytest.approx(1, rel=1e-5)
    assert s.fanC.mech_in.PW / 8114258.9326799763 == pytest.approx(1.0, rel=1e-5)
    assert s.inlet.W_in.W / 158.23408418127087 == pytest.approx(1, rel=1e-5)

    assert s.bleed.fl2_out.W == pytest.approx(1.59832409, rel=1e-5)
    assert s.merger.fl2_in.W == pytest.approx(1.59832409, rel=1e-5)
    assert s.bleed.fl2_out.Pt == pytest.approx(176422.55, rel=1e-5)
    assert s.merger.fl2_in.Pt == pytest.approx(176422.55, rel=1e-5)
    assert s.bleed.fl2_out.Tt == pytest.approx(324.2258, rel=1e-5)
    assert s.merger.fl2_in.Tt == pytest.approx(324.2258, rel=1e-5)

    assert s.fanC.ductC.bleed.fl2_out.W == pytest.approx(0.79514614358, rel=1e-5)
    assert s.fanC.ductC.merger.fl2_in.W == pytest.approx(0.79514614358, rel=1e-5)
    assert s.fanC.ductC.bleed.fl2_out.Pt == pytest.approx(98802.0075, rel=1e-5)
    assert s.fanC.ductC.merger.fl2_in.Pt == pytest.approx(98802.0075, rel=1e-5)
    assert s.fanC.ductC.bleed.fl2_out.Tt == pytest.approx(273.15, rel=1e-5)
    assert s.fanC.ductC.merger.fl2_in.Tt == pytest.approx(273.15, rel=1e-5)


def test_ComplexTurbofan_running_100():
    s = ComplexTurbofan("MyComplexTurbofan")
    s.duct.inwards.cst_loss = 0.98
    s.fanC.ductC.duct.inwards.cst_loss = 0.98
    s.fanC.ductC.bleed.inwards.split_ratio = 0.995
    s.bleed.inwards.split_ratio = 0.99

    design = s.add_driver(NonLinearSolver("design", tol=1e-7))
    design.add_unknown("fanC.mech_in.PW")

    s.fanC.mech_in.XN = 100
    s.run_drivers()

    assert s.fanC.mech_in.XN == 100.0
    assert s.fanC.gh == pytest.approx(0.15669212069, rel=1e-5)
    assert s.fanC.mech_in.PW == pytest.approx(10656747.6, rel=1e-5)
    assert s.inlet.W_in.W == pytest.approx(173.4933, rel=1e-5)

    assert s.bleed.fl2_out.W == pytest.approx(1.75245766, rel=1e-5)
    assert s.merger.fl2_in.W == pytest.approx(1.75245766, rel=1e-5)
    assert s.bleed.fl2_out.Pt == pytest.approx(196426.7, rel=1e-5)
    assert s.merger.fl2_in.Pt == pytest.approx(196426.7, rel=1e-5)
    assert s.bleed.fl2_out.Tt == pytest.approx(334.330, rel=1e-5)
    assert s.merger.fl2_in.Tt == pytest.approx(334.330, rel=1e-5)


def to_ComplexTurbofan_html():
    s = ComplexTurbofan("MyComplexTurbofan")
    s.duct.inwards.cst_loss = 0.98
    s.fanC.ductC.duct.inwards.cst_loss = 0.98
    s.fanC.ductC.bleed.inwards.split_ratio = 0.995
    s.bleed.inwards.split_ratio = 0.99

    s.add_driver(NonLinearSolver("design", tol=1e-7))

    s.to_html("complexturbofan.html")
