import pytest

from cosapp.systems import System
from cosapp.drivers import NonLinearSolver


@pytest.fixture
def PressureLossFactory(test_library, test_data):
    def factory(suffix=""):
        return System.load(test_data / f"system_config_pressureloss{suffix}.json")
    return factory


@pytest.fixture
def system0(PressureLossFactory):
    """pressureLoss0D"""
    return PressureLossFactory()


@pytest.fixture
def system1(PressureLossFactory):
    """pressureLossSys (pressureLoss0D)"""
    s = PressureLossFactory(suffix="1")
    s.exec_order = ["p1"]
    return s


@pytest.fixture
def system2(PressureLossFactory):
    """pressureLossSys (pressureLoss0D + pressureLoss0D)"""
    s = PressureLossFactory(suffix="2")
    s.exec_order = ("p1", "p2")
    return s


@pytest.fixture
def system2tank(PressureLossFactory):
    """pressureLossSys (pressureLoss0D + tank + pressureLoss0D a pressureLossSys)"""
    s = PressureLossFactory(suffix="2tank")
    s.exec_order = ("p1", "tank1", "p2")
    return s


@pytest.fixture
def system11(PressureLossFactory):
    """pressureLossSys(pressureLoss0D) with direct connexion of module
    """
    s = PressureLossFactory(suffix="11")
    s.exec_order = ["p1"]
    s.p1.exec_order = ["p11"]
    return s


@pytest.fixture
def system11bis(PressureLossFactory):
    """pressureLossSys(pressureLoss0D) with connexion of module using `..`
    """
    return PressureLossFactory(suffix="11bis")


@pytest.fixture
def system12(PressureLossFactory):
    """pressureLossSys(pressureLoss0D + pressureLoss0D)
    """
    s = PressureLossFactory(suffix="12")
    s.exec_order = ["p1"]
    s.p1.exec_order = ["p11", "p12"]
    return s


@pytest.fixture
def system22(PressureLossFactory):
    """pressureLossSys(pressureLoss0D + pressureLoss0D) + pressureLoss0D
    """
    s = PressureLossFactory(suffix="22")
    s.exec_order = ["p1", "p2"]
    s.p1.exec_order = ["p11", "p12"]
    return s


@pytest.fixture
def system121(PressureLossFactory):
    """pressureLoss0D + Splitter12 + pressureLoss0D//pressureLoss0D + Mixer21 pressureLoss0D
    """
    s = PressureLossFactory(suffix="121")
    s.exec_order = "p1", "sp", "p2", "p3", "mx", "p4"
    return s


@pytest.fixture
def system131(PressureLossFactory):
    """pressureLoss0D + Mixer21 + pressureLoss0D//pressureLoss0D(backward) + Splitter12 + pressureLoss0D
    """
    s = PressureLossFactory(suffix="131")
    s.exec_order = "p1", "mx", "p2", "sp", "p3", "p4"
    s.p3.K = -12100
    s.p2.K = 100
    s.sp.x = 0.5
    return s


@pytest.fixture
def system222(PressureLossFactory):
    """pLS(pl0 + mx + (pLS (pL0 + mx + (pL0+pL0//pl0(b) + sp + pl0))//pl0(b)) + sp + pL0)
    """
    s = PressureLossFactory(suffix="222")
    s.exec_order = "p1", "m1", "p2", "s1", "p3", "p4"
    s.flnum_in.W = 9.0
    s.flnum_in.Pt = 108100
    s.p2.p22.p221.K = 50
    s.p2.p22.p222.K = 50
    s.p3.K = -32100
    s.p2.p23.K = -12100
    return s


def test_system0(system0):
    s = system0
    s.run_once()
    assert s.flnum_out.Pt == 90000.0


def test_system1(system1):
    s = system1
    s.run_once()
    assert s.p1.flnum_out.Pt == 90000.0


def test_system2(system2):
    s = system2
    s.run_once()
    assert s.p2.flnum_out.Pt == 80000.0


def test_system2tank(system2tank):
    s = system2tank

    # tank is half full
    s.tank1.vol = 10.0
    s.run_once()
    assert s.p2.flnum_out.Pt == 89900.0
    assert s.tank1.vol == 10.9
    assert s.tank1.flnum_out.W == 1.0

    # tank is empty
    s.tank1.vol = 0.0
    s.run_once()
    assert s.p2.flnum_out.Pt == 89900.0
    assert s.tank1.vol == 0.9
    assert s.tank1.flnum_out.W == 1.0

    # tank is full
    s.tank1.vol = 100.0
    s.run_once()
    assert s.p2.flnum_out.Pt == 80000.0
    assert s.tank1.vol == pytest.approx(100)
    assert s.tank1.flnum_out.W == 10.0


def test_system11(system11):
    s = system11
    s.run_once()
    assert s.p1.p11.flnum_out.Pt == pytest.approx(90000, rel=5e-8)


def test_system11bis(system11bis):
    s = system11bis
    s.run_once()
    assert s.p2.p21.flnum_out.Pt == pytest.approx(80000, rel=5e-8)
    assert s.p3.flnum_out.Pt == pytest.approx(70000, rel=5e-8)


def test_system12(system12):
    s = system12
    s.run_once()
    assert s.p1.p12.flnum_out.Pt == pytest.approx(80000, rel=5.0e-8)


def test_system22(system22):
    s = system22
    s.run_once()
    assert s.p2.flnum_out.Pt == pytest.approx(70000, rel=5.0e-8)


def test_system121(system121):
    s = system121
    # test sub-systems are listed in the execution order list
    assert list(s.children) == list(s.exec_order)

    s.run_once()
    assert s.p4.flnum_out.Pt == 74800.0

    s.add_driver(NonLinearSolver("design", tol=5.0e-8))
    s.run_drivers()

    # test iterative loop detection
    assert len(s.residues) == 0
    residues = s.get_unsolved_problem().residues
    assert "mx.(epsilon == 0)" in residues

    assert s.p4.flnum_out.Pt == pytest.approx(77500, rel=1e-6)
    assert s.p2.flnum_out.W == pytest.approx(5, rel=1e-6)
    assert s.mx.flnum_out.W == pytest.approx(s.mx.flnum_in1.W + s.mx.flnum_in2.W, rel=1e-5)


def test_system121_redundant_1(system121):
    """Same as `test_system121` with redundant declaration of unknowns.

    Case 1: system unknown `sp.x` is redeclared as unknown at solver level.
    """
    s = system121
    d = s.add_driver(NonLinearSolver("solver"))
    d.add_unknown("sp.x")

    with pytest.raises(ValueError, match="'sp\.inwards\.x' is defined as design and off-design unknown"):
        s.run_drivers()


def test_system121_redundant_2(system121):
    """Same as `test_system121` with redundant declaration of unknowns.

    Case 2: system unknown `sp.x` is redeclared as unknown at runner level.
    """
    s = system121
    d = s.add_driver(NonLinearSolver("solver"))
    d.runner.add_unknown("sp.x")

    with pytest.raises(ValueError, match="'sp\.inwards\.x' already exists in 'offdesign'"):
        s.run_drivers()


def test_system131(system131):
    # ! Do not suppress this unit test, it's the only one doing new computation with resetting the system
    s = system131
    d = s.add_driver(NonLinearSolver("solver"))

    s.run_drivers()
    assert s.p4.flnum_out.Pt == pytest.approx(67900, rel=1e-5)
    assert s.p2.flnum_out.W == pytest.approx(11, rel=1e-5)
    assert s.p4.flnum_out.W == pytest.approx(10, rel=1e-5)
    assert s.sp.x == pytest.approx(10 / 11, rel=2e-5)

    s.p3.K = -3600
    s.run_drivers()
    assert s.p4.flnum_out.Pt == pytest.approx(65600, rel=1e-5)
    assert s.p2.flnum_out.W == pytest.approx(12, rel=1e-5)
    assert s.p4.flnum_out.W == pytest.approx(10, rel=1e-5)
    assert s.sp.x == pytest.approx(10 / 12, rel=1e-5)

    s.p3.K = -12100
    d.options["factor"] = 0.7
    s.run_drivers()
    assert s.p4.flnum_out.Pt == pytest.approx(67900, rel=1e-5)
    assert s.p2.flnum_out.W == pytest.approx(11, rel=1e-5)
    assert s.p4.flnum_out.W == pytest.approx(10, rel=1e-5)
    assert s.sp.x == pytest.approx(10 / 11, rel=1e-5)

    s.p3.K = -260100
    s.run_drivers()

    assert s.p2.flnum_out.W == pytest.approx(10.2, rel=1e-5)
    assert s.p4.flnum_out.W == pytest.approx(10.0, rel=1e-5)
    assert s.sp.x == pytest.approx(10 / 10.2, rel=1e-5)
    assert s.p4.flnum_out.Pt == pytest.approx(69596, rel=1e-5)


def test_system222(system222):
    """pLS(pl0 + mx + (pLS (pL0 + mx + (pL0+pL0//pl0(b) + sp + pl0))//pl0(b)) + sp + pL0)
    """
    s = system222
    d = s.add_driver(NonLinearSolver("solver"))
    s.run_drivers()

    assert s.p2.p24.flnum_out.Pt == pytest.approx(67900, rel=1e-5)
    assert s.p2.flnum_out.W == pytest.approx(10, rel=1e-5)
    assert s.p4.flnum_out.W == pytest.approx(9, rel=1e-5)
    assert s.s1.x == pytest.approx(9 / 10, rel=1e-5)
    assert s.p2.s21.x == pytest.approx(10 / 11, rel=1e-5)


def test_system222_redundant(system222):
    """Same as `test_system222` with redundant unknowns.
    """
    s = system222
    d = s.add_driver(NonLinearSolver("solver"))
    d.runner.add_unknown(["p2.s21.x", "s1.x"])

    with pytest.raises(ValueError, match="'p2\.s21\.inwards\.x' already exists in 'offdesign'"):
        s.run_drivers()
