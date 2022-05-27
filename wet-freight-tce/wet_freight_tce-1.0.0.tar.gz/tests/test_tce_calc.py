import pandas as pd
import pytest

from wet_freight_tce import tce_calc


def test_tc2():
    ds = "2021-10-08"
    dd = {
        "FlatRate": 12.31,
        "WorldScale": 100.0,
        "MGO": 705.25,
        "VLSFO": 565.25,
        # 'HSFO': 560.25,
    }
    data = pd.DataFrame(dd, index=[pd.to_datetime(ds)])
    res = tce_calc.calc("TC2_37", data)

    assert res["GrossFreight"][ds] == pytest.approx(488705.4495, abs=1e-1)
    assert res["BunkerCost"][ds] == pytest.approx(413495.95, abs=1e-1)
    assert res["TCE"][ds] == pytest.approx(-1907.8873541902833, abs=1e-1)


def test_tc5():
    ds = "2021-10-06"

    dd = {
        "FlatRate": 20.46,
        "WorldScale": 103.14,
        "MGO": 355.001,
        "VLSFO": 577.27,
        "HSFO": 225.79,
    }

    data = pd.DataFrame(dd, index=[pd.to_datetime(ds)])
    res = tce_calc.calc("tc5", data)

    assert res["GrossFreight"][ds] == pytest.approx(1175484.42, abs=1e-1)
    assert res["BunkerCost"][ds] == pytest.approx(846632.20, abs=1e-1)
    assert res["TCE"][ds] == pytest.approx(4373.586898227754, abs=1e-1)


def test_tc6():
    ds = "2021-10-06"

    dd = {
        "FlatRate": 20.46,
        "WorldScale": 103.14,
        "MGO": 300.00,
        "VLSFO": 300.00,
        "HSFO": 300.00,
    }

    data = pd.DataFrame(dd, index=[pd.to_datetime(ds)])
    res = tce_calc.calc("tc6", data)

    assert res["GrossFreight"][ds] == pytest.approx(633073.32, abs=1e-1)
    assert res["BunkerCost"][ds] == pytest.approx(35721.95, abs=1e-1)
    assert res["TCE"][ds] == pytest.approx(54485.80789543692, abs=1e-1)


def test_tc7():
    ds = "2021-10-06"

    dd = {
        "FlatRate": 20.46,
        "WorldScale": 103.14,
        "MGO": 300.00,
        "VLSFO": 300.00,
        "HSFO": 300.00,
    }

    data = pd.DataFrame(dd, index=[pd.to_datetime(ds)])
    res = tce_calc.calc("tc7", data)

    assert res["GrossFreight"][ds] == pytest.approx(738585.54, abs=1e-1)
    assert res["BunkerCost"][ds] == pytest.approx(251519.11, abs=1e-1)
    assert res["TCE"][ds] == pytest.approx(10447.421728144156, abs=1e-1)


def test_tc12():
    ds = "2021-10-06"

    dd = {
        "FlatRate": 20.46,
        "WorldScale": 103.14,
        "MGO": 300.00,
        "VLSFO": 300.00,
        "HSFO": 300.00,
    }

    data = pd.DataFrame(dd, index=[pd.to_datetime(ds)])
    res = tce_calc.calc("tc12", data)

    assert res["GrossFreight"][ds] == pytest.approx(746985.54, abs=1e-1)
    assert res["BunkerCost"][ds] == pytest.approx(316151.05, abs=1e-1)
    assert res["TCE"][ds] == pytest.approx(7704.059291602547, abs=1e-1)


def test_tc14():
    ds = "2021-10-06"

    dd = {
        "FlatRate": 20.46,
        "WorldScale": 103.14,
        "MGO": 300.00,
        "VLSFO": 300.00,
        "HSFO": 300.00,
    }

    data = pd.DataFrame(dd, index=[pd.to_datetime(ds)])
    res = tce_calc.calc("tc14", data)

    assert res["GrossFreight"][ds] == pytest.approx(801892.87, abs=1e-1)
    assert res["BunkerCost"][ds] == pytest.approx(286288.24, abs=1e-1)
    assert res["TCE"][ds] == pytest.approx(9254.303029258257, abs=1e-1)


def test_td3c():
    ds = "2021-10-06"

    dd = {
        "FlatRate": 20.46,
        "WorldScale": 103.14,
        "MGO": 300.00,
        "VLSFO": 300.00,
        "HSFO": 300.00,
    }

    data = pd.DataFrame(dd, index=[pd.to_datetime(ds)])
    res = tce_calc.calc("td3 c", data)

    assert res["GrossFreight"][ds] == pytest.approx(5770559.88, abs=1e-1)
    assert res["BunkerCost"][ds] == pytest.approx(828927.18, abs=1e-1)
    assert res["TCE"][ds] == pytest.approx(95383.43588761802, abs=1e-1)


def test_td7():
    ds = "2021-10-06"

    dd = {
        "FlatRate": 20.46,
        "WorldScale": 103.14,
        "MGO": 300.00,
        "VLSFO": 300.00,
        "HSFO": 300.00,
    }

    data = pd.DataFrame(dd, index=[pd.to_datetime(ds)])
    res = tce_calc.calc("td7", data)

    assert res["GrossFreight"][ds] == pytest.approx(1688195.52, abs=1e-1)
    assert res["BunkerCost"][ds] == pytest.approx(75808.78, abs=1e-1)
    assert res["TCE"][ds] == pytest.approx(164445.60452030526, abs=1e-1)


def test_td20():
    ds = "2021-10-06"

    dd = {
        "FlatRate": 20.46,
        "WorldScale": 103.14,
        "MGO": 300.00,
        "VLSFO": 300.00,
        "HSFO": 300.00,
    }

    data = pd.DataFrame(dd, index=[pd.to_datetime(ds)])
    res = tce_calc.calc("td20", data)

    assert res["GrossFreight"][ds] == pytest.approx(2863240.7438000003, abs=1e-1)
    assert res["BunkerCost"][ds] == pytest.approx(497147.02, abs=1e-1)
    assert res["TCE"][ds] == pytest.approx(58466.288709876826, abs=1e-1)


def test_td22():
    ds = "2021-10-06"

    dd = {
        "FlatRate": 20.46,
        "WorldScale": 103.14,
        "MGO": 300.00,
        "VLSFO": 300.00,
        "HSFO": 300.00,
    }

    data = pd.DataFrame(dd, index=[pd.to_datetime(ds)])
    res = tce_calc.calc("td22", data)

    assert res["GrossFreight"][ds] == pytest.approx(103.14, abs=1e-1)
    assert res["BunkerCost"][ds] == pytest.approx(2009377.42, abs=1e-1)
    assert res["TCE"][ds] == pytest.approx(-20266.29605561041, abs=1e-1)


def test_td25():
    ds = "2021-10-06"

    dd = {
        "FlatRate": 20.46,
        "WorldScale": 103.14,
        "MGO": 300.00,
        "VLSFO": 300.00,
        "HSFO": 300.00,
    }

    data = pd.DataFrame(dd, index=[pd.to_datetime(ds)])
    res = tce_calc.calc("td25", data)

    assert res["GrossFreight"][ds] == pytest.approx(1555645.08024, abs=1e-1)
    assert res["BunkerCost"][ds] == pytest.approx(454951.02, abs=1e-1)
    assert res["TCE"][ds] == pytest.approx(22223.621876334186, abs=1e-1)
