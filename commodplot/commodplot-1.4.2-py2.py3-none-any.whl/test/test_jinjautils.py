import os
import unittest

import plotly.express as px
import plotly.graph_objects as go

from commodplot import jinjautils


class TestCommodPlotUtil(unittest.TestCase):
    def test_convert_dict_plotly_fig_html_div(self):
        df = px.data.gapminder().query("country=='Canada'")
        fig = px.line(df, x="year", y="lifeExp", title="Life expectancy in Canada")

        data = {}
        data["ch1"] = fig
        data["el"] = 1
        data["innerd"] = {}
        data["innerd"]["ch2"] = fig

        res = jinjautils.convert_dict_plotly_fig_html_div(data)
        self.assertTrue(isinstance(res["ch1"], str))
        self.assertTrue(isinstance(res["innerd"]["ch2"], str))

    def test_render_html_to_file(self):
        dirname, filename = os.path.split(os.path.abspath(__file__))
        test_out_loc = os.path.join(dirname, "test.html")
        if os.path.exists(test_out_loc):
            os.remove(test_out_loc)

        fig = go.Figure(
            data=[go.Bar(x=[1, 2, 3], y=[1, 3, 2])],
            layout=go.Layout(
                title=go.layout.Title(text="A Figure Specified By A Graph Object")
            ),
        )

        data = {"name": "test", "fig1": fig}

        jinjautils.render_html(
            data,
            template="test_report.html",
            filename="test.html",
            package_loader_name="commodplot",
        )

        self.assertTrue(test_out_loc)
        if os.path.exists(test_out_loc):
            os.remove(test_out_loc)


if __name__ == "__main__":
    unittest.main()
