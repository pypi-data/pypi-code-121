import unittest

import pandas as pd

from commodplot import commodplottable as cpt


class TestCommodplotTable(unittest.TestCase):
    def test_generate_table(self):
        df = pd.DataFrame(
            [[1, 2, 3, 4], [5, 6, 7, 8], [3, -5, 6, 7]],
            columns=["Foo", "Bar", "Buzz", "Fuzz"],
            index=["First", "Second", "Third"],
        )
        res = cpt.generate_table(df, accounting_col_columns=["Bar"])
        self.assertIn('<style type="text/css">', res)


if __name__ == "__main__":
    unittest.main()
