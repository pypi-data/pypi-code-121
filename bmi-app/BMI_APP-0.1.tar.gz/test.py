import unittest
from BMI_Calculator import myhealth
import json
import pandas as pd


class TestSum(unittest.TestCase):
    def test_overweights(self):
        """
        Test that program correctly calculates number of overweight persons
        """
        # data = [{"Gender": "Male", "HeightCm": 171, "WeightKg": 96 },
        #         { "Gender": "Male", "HeightCm": 161, "WeightKg": 85 },
        #         { "Gender": "Male", "HeightCm": 180, "WeightKg": 77 },
        #         { "Gender": "Female", "HeightCm": 166, "WeightKg": 62},
        #         {"Gender": "Female", "HeightCm": 150, "WeightKg": 70},
        #         {"Gender": "Female", "HeightCm": 167, "WeightKg": 82}]
        
        # data1 = json.loads(data)

        data_dict = {"Gender": ["Male","Male","Male","Male","Female","Female"],
                    "HeightCm": [171,161,180,166,150,167],
                    "WeightKg": [96,85,77,62,70,82]}

        df = pd.DataFrame(data_dict)
        result = myhealth(df).overweights()
        self.assertEqual(result, 1)

if __name__ == '__main__':
    unittest.main()
