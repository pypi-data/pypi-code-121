"""Test export to FMU"""
import importlib
import itertools
import re
import uuid
import zipfile

import numpy
import pandas
import pytest
from numpy.testing import assert_almost_equal

from cosapp.drivers import MonteCarlo, NonLinearSolver, RungeKutta, RunSingleCase
from cosapp.ports.enum import PortType
from cosapp.ports.port import ExtensiblePort
from cosapp.recorders import DataFrameRecorder
from cosapp.systems import System
from cosapp.tools.fmu.exporter import (
    Fmi2Causality,
    Fmi2Variability,
    FmuBuilder,
    TimeIntegrator,
    VariableType,
    to_fmu,
)

# Check optional third parties availability
pytest.importorskip("jinja2")
pytest.importorskip("pythonfmu")


def load_fmu_class(module_name: str, filepath: str):
    # Import the user interface
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    fmu_interface = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fmu_interface)
    # Instantiate the interface
    with open(filepath, "r") as f:
        data = f.read()
        class_name = re.search("class (\w+)\(\s*Fmi2Slave\s*\)\s*:", data).group(1)
    return getattr(fmu_interface, class_name)(instance_name="instance")


def get_variable_names(vars):
    return [var.name for var in vars]


@pytest.mark.parametrize("value", TimeIntegrator)
def test_TimeIntegrator_driver(value):
    assert (
        value.driver == "RungeKutta"
        if value.value.startswith("Runge-Kutta")
        else value.name
    )


@pytest.mark.parametrize("value", TimeIntegrator)
def test_TimeIntegrator_options(value):
    expected = (
        dict(order=int(value.value.split()[1]))
        if value.value.startswith("Runge-Kutta")
        else dict()
    )
    assert value.options == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (True, VariableType.Boolean),
        (2, VariableType.Integer),
        (42.0, VariableType.Real),
        ("hello", VariableType.String),
        (b"hello", TypeError),
        (object(), TypeError),
        (numpy.array(True), VariableType.Boolean),
        (numpy.array(2), VariableType.Integer),
        (numpy.array(42.0), VariableType.Real),
        (numpy.array("hello", dtype="U"), VariableType.String),
        (numpy.array([1, 2]), TypeError),
        (numpy.array(b"hello", dtype="S"), TypeError),
    ],
)
def test_FMUBuilder__get_variable_type(value, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            FmuBuilder._get_variable_type(value)
    else:
        assert FmuBuilder._get_variable_type(value) == expected


@pytest.mark.parametrize(
    "causality, variability",
    itertools.product(Fmi2Causality, (list(Fmi2Variability) + [None])),
)
def test_FMUBuilder__add_variables(causality, variability):
    data = dict((("a", True), ("b", 2), ("c", 42.0), ("d", "hello")))

    vars = FmuBuilder._add_variables(data, causality, variability)

    for v in vars:
        assert v.name in data
        assert v.causality == causality.name
        if variability is None:
            assert v.variability is None
        else:
            assert v.variability == variability.name
    assert len(vars) == len(data)

    with pytest.raises(TypeError):
        FmuBuilder._add_variables({"data": b"hello"}, causality, variability)


def test_FMUBuilder__get_default_value(testtype):
    variables = FmuBuilder._get_default_value(
        list(testtype.inputs[System.INWARDS]), testtype
    )

    for k, v in variables.items():
        if k == "k":
            assert v == pytest.approx(getattr(testtype, k))
        else:
            assert v == getattr(testtype, k)

    variables = FmuBuilder._get_default_value(("k[0]", "k[1]", "k[2]"), testtype)

    for i in range(3):
        assert variables[f"k[{i}]"] == testtype["k"][i]

    with pytest.raises(ValueError):
        FmuBuilder._get_default_value(("k[4]",), testtype)

    with pytest.raises(ValueError):
        FmuBuilder._get_default_value(("rr",), testtype)


def test_FMUBuilder__get_default_variables():
    p1 = ExtensiblePort(System.INWARDS, PortType.IN)
    p1.add_variable("a", True)
    p1.add_variable("b", 2)
    p1.add_variable("c", 42.0)
    p1.add_variable("d", "hello")
    p1.add_variable("e", b"hello")

    p2 = ExtensiblePort("out", PortType.OUT)
    p2.add_variable("f", object())
    p2.add_variable("g", numpy.array(True))
    p2.add_variable("h", numpy.array(2))
    p2.add_variable("i", numpy.array(42.0))
    p2.add_variable("j", numpy.array("hello", dtype="U"))
    p2.add_variable("k", numpy.array([1, 2]))
    p2.add_variable("l", numpy.array(b"hello", dtype="S"))

    out = FmuBuilder._get_default_variables({"p1": p1, System.OUTWARDS: p2}, to_skip=())
    expected = ("p1.a", "p1.b", "p1.c", "p1.d", "g", "h", "i", "j")
    for e in expected:
        assert e in out
    assert len(out) == len(expected)

    out = FmuBuilder._get_default_variables(
        {"p1": p1, System.OUTWARDS: p2}, to_skip=["p1.c", "p1.a", "j"]
    )
    expected = ("p1.b", "p1.d", "g", "h", "i")
    for e in expected:
        assert e in out
    assert len(out) == len(expected)


def test_FMU_export_all_causality(tmp_path, allcausality):
    test = allcausality
    fmu_file = to_fmu(test, dest=tmp_path)

    if fmu_file.suffix == ".fmu":
        with zipfile.ZipFile(fmu_file, "r") as zip_desc:
            zip_desc.extractall(fmu_file.parent)

    fmu_slave = load_fmu_class(
        "allcausality", str(fmu_file.parent / "resources" / "allcausality.py")
    )

    assert len(fmu_slave.vars) == 4
    names = get_variable_names(fmu_slave.vars.values())
    assert "in_.x" in names
    assert fmu_slave.vars[names.index("in_.x")].causality == Fmi2Causality.input
    assert "in_x" in names
    assert fmu_slave.vars[names.index("in_x")].causality == Fmi2Causality.parameter
    assert "out.x" in names
    assert fmu_slave.vars[names.index("out.x")].causality == Fmi2Causality.output
    assert "out_y" in names
    assert fmu_slave.vars[names.index("out_y")].causality == Fmi2Causality.local


def test_FMU_export_hide_all_variables(tmp_path, allcausality):
    test = allcausality
    fmu_folder = FmuBuilder.generate_fmu_facade(
        test, dest=tmp_path, inputs=[], locals=[], outputs=[], parameters=[]
    )

    fmu_slave = load_fmu_class(
        "allcausality",
        str(FmuBuilder._get_project_folder(tmp_path) / "allcausality.py"),
    )

    assert len(fmu_slave.vars) == 0


def test_FMU_export_all_type(tmp_path, testtype):
    test = testtype
    fmu_folder = FmuBuilder.generate_fmu_facade(test, dest=tmp_path)

    fmu_slave = load_fmu_class(
        "testtype", str(FmuBuilder._get_project_folder(tmp_path) / "testtype.py")
    )

    assert len(fmu_slave.vars) == 8


@pytest.mark.parametrize("name", ["k", "l"])
def test_FMU_export_type_failure(tmp_path, testtype, name):
    test = testtype
    with pytest.raises(TypeError):
        to_fmu(test, dest=tmp_path, parameters={name: testtype[name]})


def test_FMU_export_non_linear_multipoints(tmp_path, ode):
    solver = NonLinearSolver("solver")
    solver.add_child(RunSingleCase("pt1"))
    solver.add_child(RunSingleCase("pt2"))

    with pytest.raises(ValueError):
        to_fmu(ode, dest=tmp_path, nonlinear_solver=solver)


def test_FMU_export_non_linear_bad_child(tmp_path, ode):
    solver = NonLinearSolver("solver")
    solver.add_child(MonteCarlo("dummy"))

    with pytest.raises(TypeError):
        to_fmu(ode, dest=tmp_path, nonlinear_solver=solver)


def test_FMU_handle_vector_variable(tmp_path, vector_syst):
    pyfmi = pytest.importorskip("pyfmi")

    fmu_file = to_fmu(
        vector_syst,
        dest=tmp_path,
        inputs=["vi[0]", "vr[1]"],
        outputs=["vi[2]", "vr[2]"],
        fmu_name_suffix=str(uuid.uuid4()).replace("-", ""),
    )

    # Load the FMU
    model = pyfmi.load_fmu(str(fmu_file))

    variables = model.get_model_variables()

    assert model.get_integer([variables["vi[0]"].value_reference])[0] == 1
    model.set_integer([variables["vi[2]"].value_reference], [33])
    assert model.get_integer([variables["vi[2]"].value_reference])[0] == 33

    assert model.get_real([variables["vr[2]"].value_reference])[0] == 3.0
    model.set_real([variables["vr[1]"].value_reference], [42.0])
    assert model.get_real([variables["vr[1]"].value_reference])[0] == 42.0



@pytest.mark.parametrize("integrator", TimeIntegrator)
def test_FMU_export_time_integrator(tmp_path, ode, integrator):
    pyfmi = pytest.importorskip("pyfmi")
    fmu_file = to_fmu(
        ode,
        dest=tmp_path,
        locals={"f": 0.0, "df_dt": 0.0},
        time_integrator=integrator,
        fmu_name_suffix=str(uuid.uuid4()).replace("-", ""),
    )

    # Load the FMU
    model = pyfmi.load_fmu(str(fmu_file))

    # Run the FMU simulation
    results = model.simulate(final_time=1)

    # Reference value
    end_time = results["time"][-1]
    ref = ode(end_time)
    assert results["f"][-1] == pytest.approx(ref, rel=1e-3)



def test_FMU_integration_simple(tmp_path, ode):
    pyfmi = pytest.importorskip("pyfmi")

    # Convert to FMU
    fmu_file = to_fmu(
        ode,
        dest=tmp_path,
        locals=["f", "df_dt"],
        fmu_name_suffix=str(uuid.uuid4()).replace("-", ""),
    )

    # Load the FMU
    model = pyfmi.load_fmu(str(fmu_file))

    # Run the FMU simulation
    results = model.simulate(final_time=1)

    # Reference value
    end_time = results["time"][-1]
    ref = ode(end_time)
    assert results["f"][-1] == pytest.approx(ref, rel=1e-7)


def test_FMU_integration_nonlinear_design(tmp_path, iterativenonlinear):
    """Same as `test_FMU_integration_nonlinear_local` with additional
    problem defined at solver level (off-design problem).
    """
    pyfmi = pytest.importorskip("pyfmi")

    solver = NonLinearSolver("solver", iterativenonlinear)
    solver.add_unknown("nonlinear.k1").add_equation("splitter.p2_out.x == 10")

    # Init
    t_driver = iterativenonlinear.add_driver(
        RungeKutta(order=4, dt=0.1, time_interval=[0, 0.2])
    )
    t_driver.add_child(solver)

    # Set BC
    t_driver.set_scenario(
        init = {"p_in.x": 1.0},
        values = {"p_in.x": "5 - 4 * exp(-t / 0.1)"},
    )
    recorder = t_driver.add_recorder(
        DataFrameRecorder(includes=["p_in.x", "p_out.x", "nonlinear.k1"]), period=0.1
    )
    iterativenonlinear.run_drivers()

    # Reference
    data = recorder.export_data()
    assert_almost_equal(data["p_out.x"], numpy.full(len(data), 10.0))

    # Convert to FMU
    fmu_file = to_fmu(
        iterativenonlinear,
        dest=tmp_path,
        nonlinear_solver=solver,
        locals=["nonlinear.k1"],
        fmu_name_suffix=str(uuid.uuid4()).replace("-", ""),
    )

    # Load the FMU
    model = pyfmi.load_fmu(str(fmu_file))

    # Run the FMU simulation
    inputs = ("p_in.x", lambda t: 5.0 - 4.0 * numpy.exp(-t / 0.1))
    results = model.simulate(final_time=0.3, input=inputs, options={"ncp": 3})
    results = pandas.DataFrame(
        results.data_matrix.T[1:, :],
        columns=["time"] + list(model.get_model_variables()),
    )

    for column in filter(lambda c: c != "time", results.columns):
        assert results[column].values == pytest.approx(data[column].values)


def test_FMU_integration_nonlinear_local(tmp_path, iterativenonlinear):
    pyfmi = pytest.importorskip("pyfmi")

    solver = NonLinearSolver("solver", iterativenonlinear)
    solver.runner.add_unknown("nonlinear.k1").add_equation(
        "splitter.p2_out.x == 10"
    )

    # Init
    t_driver = iterativenonlinear.add_driver(
        RungeKutta(order=4, dt=0.1, time_interval=[0, 0.2])
    )
    t_driver.add_child(solver)

    # Set BC
    t_driver.set_scenario(
        init = {"p_in.x": 1.0},
        values = {"p_in.x": "5 - 4 * exp(-t / 0.1)"},
    )
    recorder = t_driver.add_recorder(
        DataFrameRecorder(includes=["p_in.x", "p_out.x", "nonlinear.k1"]),
        period=0.1,
    )
    iterativenonlinear.run_drivers()

    # Reference
    data = recorder.export_data()
    assert_almost_equal(data["p_out.x"], numpy.full(len(data), 10.0))

    # Convert to FMU
    fmu_file = to_fmu(
        iterativenonlinear,
        dest=tmp_path,
        nonlinear_solver=solver,
        locals=["nonlinear.k1"],
        fmu_name_suffix=str(uuid.uuid4()).replace("-", ""),
    )

    # Load the FMU
    model = pyfmi.load_fmu(str(fmu_file))

    # Run the FMU simulation
    inputs = ("p_in.x", lambda t: 5.0 - 4.0 * numpy.exp(-t / 0.1))
    results = model.simulate(final_time=0.3, input=inputs, options={"ncp": 3})
    results = pandas.DataFrame(
        results.data_matrix.T[1:, :],
        columns=["time"] + list(model.get_model_variables()),
    )

    for column in filter(lambda c: c != "time", results.columns):
        assert results[column].values == pytest.approx(data[column].values)


def test_FMU_integration_vector_problem(tmp_path, vector_problem):
    pyfmi = pytest.importorskip("pyfmi")

    # Setup the system
    solver = NonLinearSolver("solver", vector_problem)

    # Init
    vector_problem.x = 1.0
    vector_problem.add_driver(solver)
    vector_problem.run_drivers()

    # Convert to FMU
    fmu_file = to_fmu(
        vector_problem,
        dest=tmp_path,
        nonlinear_solver=solver,
        inputs=["x"],
        outputs=["y"],
        locals=["dummy_coef[0]"],
        fmu_name_suffix=str(uuid.uuid4()).replace("-", ""),
    )

    # Load the FMU
    model = pyfmi.load_fmu(str(fmu_file))

    # Run the FMU simulation
    inputs = ("x", lambda t: 5.0 - 4.0 * numpy.exp(-t / 0.1))
    results = model.simulate(final_time=0.3, input=inputs, options={"ncp": 3})
    r = pandas.DataFrame(
        results.data_matrix.T[1:, :],
        columns=["time"] + list(model.get_model_variables()),
    )

    assert_almost_equal(r["dummy_coef[0]"].values, 0.5 * (r["x"] + r["y"]))
