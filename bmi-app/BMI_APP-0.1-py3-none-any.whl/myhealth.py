import json
import pandas as pd

class health():
    """
    Objective : Read JSON data having Height and Weight
    Compute health indicators: BMI, BMI Category, Health Risk
    Calculate total number of overweight people in input data
    """

    # initialize class
    def __init__(self, filename):
        self.filename = filename

    # read json data
    def readJson(self):
        with open(self.filename) as file:
            self.rawdata = json.load(file)

    # Compute BMI, BMI Category, Health Risk using Height and Weight
    def process_data(self, row):
        try:
            bmi = row['WeightKg'] / ((row['HeightCm']/100)**2)
            if bmi <= 18.4:
                return bmi, 'Underweight', 'Malnutrition risk'
            elif bmi <= 24.9:
                return bmi, 'Normal weight', 'Low risk'
            elif bmi <= 29.9:
                return bmi, 'Overweight', 'Enhanced risk'
            elif bmi <= 34.9:
                return bmi, 'Moderately obese', 'Medium risk'
            elif bmi <= 39.9:
                return bmi, 'Severely obese', 'High risk'
            else:
                return bmi, 'Very severely obese', 'Very high risk'
        except Exception as e:
            print(e)

    # Read json data and return the updated data after incorporating health indicators
    def getData(self):
        self.readJson()
        self.df = pd.DataFrame(self.rawdata)    
        
        processes_rows = self.df.apply(lambda row: self.process_data(row), axis=1)    
        self.df[['BMI','BMI Category','Health Risk']] = processes_rows.tolist()

        return self.df

    # Calculate total number of overweight people in input data
    def overweights(self):
        try:
            if not self.df.empty:
                return len(self.df[self.df['BMI Category'] == 'Overweight'])
            else:
                return None
        except Exception as e:
            print(e)