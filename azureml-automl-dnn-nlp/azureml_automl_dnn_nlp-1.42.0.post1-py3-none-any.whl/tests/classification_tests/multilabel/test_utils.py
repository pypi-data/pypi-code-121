import numpy as np
import pandas as pd
import unittest

from azureml.automl.dnn.nlp.classification.multilabel.utils import change_label_col_format


class UtilTests(unittest.TestCase):
    def test_change_label_col_format_happy_path(self):
        input_df = pd.DataFrame({"input_text_col": np.array(["Some input text!",
                                                             "Some more input text!",
                                                             "Yet more input text, much wow."]),
                                 "labels": np.array(["lbl1", "", "lbl1,lbl2"])})
        change_label_col_format(input_df=input_df, label_col_name="labels")

        expected_input_df = input_df.copy()
        expected_input_df["labels"] = np.array(["['lbl1']", "[]", "['lbl1','lbl2']"])

        np.testing.assert_array_equal(expected_input_df.values, input_df.values)

    def test_change_label_col_format_period_case(self):
        input_df = pd.DataFrame({"input_text_col": np.array(["Some input text!",
                                                             "Some more input text!",
                                                             "Yet more input text, huzzah!"]),
                                 "labels": np.array(["google.com", "bing.com", "microsoft.com"])})
        change_label_col_format(input_df=input_df, label_col_name="labels")

        expected_input_df = input_df.copy()
        expected_input_df["labels"] = np.array(["['com','google']", "['bing','com']", "['com','microsoft']"])

        np.testing.assert_array_equal(expected_input_df.values, input_df.values)
