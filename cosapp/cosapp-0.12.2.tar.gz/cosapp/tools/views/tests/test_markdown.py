import pytest

from cosapp.ports import Port, PortType
from cosapp.systems import System
from cosapp.tools.views.markdown import system_to_md, port_to_md, PortMarkdownFormatter

# <codecell> Local test classes

class DummyPort(Port):
    def setup(self):
        self.add_variable("a", 1)
        self.add_variable("b", 2)


class AnotherPort(Port):
    def setup(self):
        self.add_variable("aaaa", 1)


class DummyPortWithDesc(Port):
    def setup(self):
        self.add_variable("foo", 1, desc="Foo variable")
        self.add_variable("bar", 2, desc="Bar variable")


class System2(System):
    def setup(self):
        self.add_inward({"data1": 9.0, "data2": 11.0, "data3": 13.0})
        self.add_outward({"local1": 7.0, "a": 14.0, "b": 21.0})
        self.add_output(AnotherPort, "other")


class System3(System):
    def setup(self):
        self.add_input(DummyPort, "entry")
        self.add_output(DummyPort, "exit")


class System4(System):
    def setup(self):
        self.add_inward("X", -1.0)
        self.add_equation("X == 1.")


class DynamicSystem2(System2):
    def setup(self):
        super().setup()
        self.add_transient("A", der="a")
        self.add_rate("db_dt", source="b")


class DynamicSystem3(System3):
    def setup(self):
        super().setup()
        self.add_transient("A", der="entry.a")
        self.add_transient("B", der="entry.b")
        self.add_rate("db_out", source="exit.b")


@pytest.fixture(scope='function')
def composite():
    """Returns composite system with ports and children"""
    top = System3('top')
    top.add_child(System4('sub'))
    top.add_child(DynamicSystem3('dyn'))
    return top


# <codecell>

# TODO("be sure the test is complete")
def test_system_to_md():
    s = System("s")
    markdown = system_to_md(s)
    assert "### Child components" not in markdown
    assert "### Inputs" not in markdown
    assert "### Outputs" not in markdown
    assert "### Residues" not in markdown
    assert f"`{System.INWARDS}`: ExtensiblePort" not in markdown
    assert f"`{System.OUTWARDS}`: ExtensiblePort" not in markdown

    s = System2("s")
    markdown = system_to_md(s)
    assert "### Child components" not in markdown
    assert "### Inputs" in markdown
    assert "### Outputs" in markdown
    assert "### Residues" not in markdown
    assert f"`{System.INWARDS}`: ExtensiblePort" in markdown
    assert f"`{System.OUTWARDS}`: ExtensiblePort" in markdown

    s = System3("s")
    markdown = system_to_md(s)
    assert "### Child components" not in markdown
    assert "### Inputs" in markdown
    assert "### Outputs" in markdown
    assert "### Residues" not in markdown
    assert f"`{System.INWARDS}`: ExtensiblePort" not in markdown
    assert f"`{System.OUTWARDS}`: ExtensiblePort" not in markdown

    s = System4("s")
    markdown = system_to_md(s)
    assert "### Child components" not in markdown
    assert "### Inputs" in markdown
    assert "### Outputs" not in markdown
    assert "### Residues" in markdown
    assert f"`{System.INWARDS}`: ExtensiblePort" in markdown
    assert f"`{System.OUTWARDS}`: ExtensiblePort" not in markdown

    u = System("child")
    s.add_child(u)
    markdown = system_to_md(s)
    assert "### Child components" in markdown

    class NewS(System):
        tags = ["dev"]

    s = NewS("s")
    markdown = system_to_md(s)
    assert "**Tags**" in markdown


@pytest.mark.parametrize("direction", PortType)
@pytest.mark.parametrize(
    "PortCls, expected",
    [
        (DummyPort, "  **a**: 1 |\n  **b**: 2 |"),
        (DummyPortWithDesc, "  **foo**: 1 | Foo variable\n  **bar**: 2 | Bar variable"),
    ],
)
def test_port_to_md(PortCls: type, direction, expected):
    p = PortCls("p", direction)
    div_header = PortMarkdownFormatter.div_header()
    table_header = f"{div_header}\n\n|  |  |\n---|---\n"
    header = f"`p`: {PortCls.__name__}\n{table_header}"
    footer = "\n</div>\n"
    assert port_to_md(p) == f"{header}{expected}{footer}"


def test_PortMarkdownFormatter_div_header():
    assert PortMarkdownFormatter.div_header() == (
        r"<div class='cosapp-port-table' style='margin-left: 25px; margin-top: -12px'>"
        r"<style type='text/css'>"
        r".cosapp-port-table >table >thead{display: none}"
        r".cosapp-port-table tbody tr{background: rgba(255, 255, 255, 0)!important}"
        r".cosapp-port-table tbody tr:hover{background: #e1f5fe!important}"
        r".cosapp-port-table >table {margin-left: unset; margin-right: unset}"
        r"</style>"
    )


def test_PortMarkdownFormatter_wrap():
    assert PortMarkdownFormatter.wrap("foo") == [
        PortMarkdownFormatter.div_header(),
        "", "|  |  |", "---|---",
        "foo",
        "</div>", "",
    ]

    assert PortMarkdownFormatter.wrap(['x', 'y']) == [
        PortMarkdownFormatter.div_header(),
        "", "|  |  |", "---|---",
        "x", "y",
        "</div>", "",
    ]


@pytest.mark.parametrize("direction", PortType)
@pytest.mark.parametrize("PortCls, expected", [
    (
        DummyPort,
        ["`p`: DummyPort"] +
        PortMarkdownFormatter.wrap([
            "  **a**: 1 |",
            "  **b**: 2 |",
        ]),
    ),
    (
        DummyPortWithDesc,
        ["`p`: DummyPortWithDesc"] +
        PortMarkdownFormatter.wrap([
            "  **foo**: 1 | Foo variable",
            "  **bar**: 2 | Bar variable",
        ]),
    ),
    (
        DummyPortWithDesc,
        [
            "`p`: DummyPortWithDesc",
            PortMarkdownFormatter.div_header(),
            "",
            "|  |  |",
            "---|---",
            "  **foo**: 1 | Foo variable",
            "  **bar**: 2 | Bar variable",
            "</div>",
            "",
        ],
    ),
])
def test_PortMarkdownFormatter_content(PortCls: type, direction, expected):
    p = PortCls("p", direction)
    mdt = PortMarkdownFormatter(p)
    assert mdt.content() == expected


@pytest.mark.parametrize("direction", PortType)
@pytest.mark.parametrize("PortCls, expected", [
    (
        DummyPort,
        PortMarkdownFormatter.wrap([
            "  **a**: 1 |",
            "  **b**: 2 |",
        ]),
    ),
    (
        DummyPortWithDesc,
        PortMarkdownFormatter.wrap([
            "  **foo**: 1 | Foo variable",
            "  **bar**: 2 | Bar variable",
        ]),
    ),
])
def test_PortMarkdownFormatter_var_repr(PortCls: type, direction, expected):
    p = PortCls("p", direction)
    mdt = PortMarkdownFormatter(p)
    assert mdt.var_repr() == expected


def test_PortMarkdownFormatter_markdown(composite):
    top = composite
    assert top.name == "top"

    mdt = PortMarkdownFormatter(top.entry)
    assert mdt.markdown() == mdt.markdown(contextual=True)  # test default
    assert mdt.markdown(contextual=True).startswith("`top.entry`: DummyPort")
    assert mdt.markdown(contextual=False).startswith("`entry`: DummyPort")

    mdt = PortMarkdownFormatter(top.exit)
    assert mdt.markdown(contextual=True).startswith("`top.exit`: DummyPort")
    assert mdt.markdown(contextual=False).startswith("`exit`: DummyPort")

    mdt = PortMarkdownFormatter(top.sub.inwards)
    assert mdt.markdown(contextual=True).startswith("`top.sub.inwards`: ExtensiblePort")
    assert mdt.markdown(contextual=False).startswith("`inwards`: ExtensiblePort")

    mdt = PortMarkdownFormatter(top.dyn.entry)
    assert mdt.markdown(contextual=True).startswith("`top.dyn.entry`: DummyPort")
    assert mdt.markdown(contextual=False).startswith("`entry`: DummyPort")

    # Full content test
    top.dyn.entry.a = 3.14
    top.dyn.entry.b = -0.5
    expected = (
        "`top.dyn.entry`: DummyPort\n"
        f"{PortMarkdownFormatter.div_header()}\n"
        "\n|  |  |\n---|---\n"
        "  **a**: 3.14 |\n  **b**: -0.5 |"
        "\n</div>\n"
    )
    assert mdt.markdown() == expected
