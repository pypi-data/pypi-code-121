# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import os
import unittest
import shapelets


class DataAapExamplesTest(unittest.TestCase):

    def test_data_app_examples(self):
        avoid = ["01_anomaly_search_in_stocks_correlation.py", "02_arrythmia_detection.py"]
        client = shapelets.init_session("admin", "admin")
        directory = f"{os.path.dirname(os.path.abspath(__file__))}{os.sep}..{os.sep}..{os.sep}examples{os.sep}shapelets_example{os.sep}dataapps"
        examples = ["Charts", "Contexts", "Controllers", "Data", "Layouts", "Operations", "Use-cases"]
        for example in examples:
            example_dir = f"{directory}{os.sep}{example}"
            for filename in os.listdir(example_dir):
                if filename.endswith(".py") and filename not in avoid:
                    file_dir = f"{example_dir}{os.sep}{filename}"
                    if os.system("python " + file_dir) != 0:
                        self.fail(f"Script {filename} Failed")
                    else:
                        client.delete_data_app(filename.replace(".py", ""))
