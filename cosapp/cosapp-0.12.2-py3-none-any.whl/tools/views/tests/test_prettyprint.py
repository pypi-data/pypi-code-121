from io import StringIO
from unittest import skip, TestCase

from cosapp.ports import Port, Scope
from cosapp.systems import System

from ..prettyprint import list_inputs, list_outputs


class TestPrettyPrint(TestCase):
    class TestPort(Port):
        def setup(self):
            self.add_variable("Pt", 101325.0, limits=(0.0, None))
            self.add_variable("W", 1.0, valid_range=(0.0, None))

    class SubSystem(System):
        def setup(self):
            self.add_input(TestPrettyPrint.TestPort, "in_")
            self.add_inward(
                "sloss",
                0.95,
                unit="m/s",
                dtype=float,
                valid_range=(0.8, 1.0),
                invalid_comment="not valid",
                limits=(0.0, 1.0),
                out_of_limits_comment="hasta la vista baby",
                desc="get down",
                scope=Scope.PROTECTED,
            )
            self.add_output(TestPrettyPrint.TestPort, "out")
            self.add_outward(
                "tmp",
                unit="inch/lbm",
                dtype=(int, float, complex),
                valid_range=(1, 2),
                invalid_comment="not valid tmp",
                limits=(0, 3),
                out_of_limits_comment="I'll be back",
                desc="banana",
                scope=Scope.PROTECTED,
            )

            self.add_outward("dummy", 1.0)
            self.add_equation("dummy == 0")

        def compute(self):
            for name in self.out:
                self.out[name] = self.in_[name] * self.sloss

            self.dummy /= 100.0

    class TopSystem(System):

        tags = ["cosapp", "tester"]

        def setup(self):
            self.add_inward("top_k")
            self.add_outward("top_tmp")

            self.add_child(
                TestPrettyPrint.SubSystem("sub"), pulling={"in_": "in_", "out": "out"}
            )

    def test_list_residuals(self):
        s = TestPrettyPrint.TopSystem("test")
        outputs = list_outputs(s, residuals=True)
        self.assertEqual(
            sorted(outputs),
            [
                ("test.sub.out.Pt", {"resids": "", "value": 101325.0}),
                ("test.sub.out.W", {"resids": "", "value": 1.0}),
                ("test.sub.residue.dummy == 0", {"resids": 1.0, "value": ""}),
            ],
        )

    def test_list_locals(self):
        s = TestPrettyPrint.TopSystem("test")
        outputs = list_outputs(s, local=True)
        self.assertEqual(
            sorted(outputs),
            [
                ("test.sub.dummy", {"value": 1.0}),
                ("test.sub.out.Pt", {"value": 101325.0}),
                ("test.sub.out.W", {"value": 1.0}),
                ("test.sub.tmp", {"value": 1}),
            ],
        )

    def test_list_hierarchical(self):
        s = TestPrettyPrint.TopSystem("test")
        inputs = list_inputs(s, hierarchical=False)
        self.assertEqual(
            sorted(inputs),
            [
                ("test.sub.in_.Pt", {"value": 101325.0}),
                ("test.sub.in_.W", {"value": 1.0}),
            ],
        )

    def test_list_data(self):
        s = TestPrettyPrint.TopSystem("test")
        inputs = list_inputs(s, inwards=True)
        self.assertEqual(
            sorted(inputs),
            [
                ("test.sub.in_.Pt", {"value": 101325.0}),
                ("test.sub.in_.W", {"value": 1.0}),
                ("test.sub.sloss", {"value": 0.95}),
            ],
        )

    def test_list_return_value(self):
        s = TestPrettyPrint.TopSystem("test")
        inputs = list_inputs(s, out_stream=None)
        self.assertEqual(
            sorted(inputs),
            [
                ("test.sub.in_.Pt", {"value": 101325.0}),
                ("test.sub.in_.W", {"value": 1.0}),
            ],
        )

        # list explicit outputs
        outputs = list_outputs(s, out_stream=None)
        self.assertEqual(
            sorted(outputs),
            [
                ("test.sub.out.Pt", {"value": 101325.0}),
                ("test.sub.out.W", {"value": 1.0}),
            ],
        )

    @skip("TODO")
    def test_list_no_values(self):
        #  check if warning is displayed
        pass

    def test_simple_list_vars_options(self):
        s = TestPrettyPrint.TopSystem("test")
        # list_inputs test
        stream = StringIO()
        inputs = list_inputs(s, out_stream=stream)
        text = stream.getvalue()
        self.assertEqual(
            sorted(inputs),
            [
                ("test.sub.in_.Pt", {"value": 101325.0}),
                ("test.sub.in_.W", {"value": 1.0}),
            ],
        )
        self.assertEqual(1, text.count("2 Input(s) in 'model'"))
        self.assertEqual(1, text.count("top"))
        self.assertEqual(1, text.count("  test"))
        self.assertEqual(1, text.count("    sub"))
        self.assertEqual(1, text.count("      in_"))
        self.assertEqual(1, text.count("        Pt"))
        num_non_empty_lines = sum([1 for s in text.splitlines() if s.strip()])
        self.assertEqual(num_non_empty_lines, 10)

        # list_outputs test
        stream = StringIO()
        outputs = list_outputs(s, out_stream=stream)
        text = stream.getvalue()
        self.assertEqual(
            sorted(outputs),
            [
                ("test.sub.out.Pt", {"value": 101325.0}),
                ("test.sub.out.W", {"value": 1.0}),
            ],
        )
        self.assertEqual(1, text.count("2 Output(s) in 'model'"))
        self.assertEqual(1, text.count("top"))
        self.assertEqual(1, text.count("  test"))
        self.assertEqual(1, text.count("    sub"))
        self.assertEqual(1, text.count("      out"))
        self.assertEqual(1, text.count("        Pt"))
        num_non_empty_lines = sum([1 for s in text.splitlines() if s.strip()])
        self.assertEqual(num_non_empty_lines, 10)

