from pollination.honeybee_energy.settings import SimParDefault, SimParLoadBalance, \
    SimParComfort, SimParSizing, BaselineOrientationSimPars
from queenbee.plugin.function import Function


def test_sim_par_default():
    function = SimParDefault().queenbee
    assert function.name == 'sim-par-default'
    assert isinstance(function, Function)


def test_sim_par_load_balance():
    function = SimParLoadBalance().queenbee
    assert function.name == 'sim-par-load-balance'
    assert isinstance(function, Function)


def test_sim_par_comfort():
    function = SimParComfort().queenbee
    assert function.name == 'sim-par-comfort'
    assert isinstance(function, Function)


def test_sim_par_sizing():
    function = SimParSizing().queenbee
    assert function.name == 'sim-par-sizing'
    assert isinstance(function, Function)


def test_baseline_orientation_sim_pars():
    function = BaselineOrientationSimPars().queenbee
    assert function.name == 'baseline-orientation-sim-pars'
    assert isinstance(function, Function)
