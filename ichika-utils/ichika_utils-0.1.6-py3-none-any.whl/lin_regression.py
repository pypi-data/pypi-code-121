import numpy as np
from sklearn.linear_model import LinearRegression
import asyncio
import uvloop

class LinRegression:
    def __init__(self):
        self.self = self

    async def calcLinRegressionX(self, x_data: list, y_data: list):
        """Calculates the linear regression of the data for the x-axis

        Args:
            x_data (list): list of data for x-axis
            y_data (list): list of data for y-axis

        Returns:
            _type_: dict
        """
        x = np.array(x_data).reshape((-1, 1))
        y = np.array(y_data)
        model = LinearRegression().fit(x, y)
        r_sq = model.score(x, y)
        yIntercept = model.intercept_
        slope = model.coef_
        return {"r_sq": r_sq, "yIntercept": yIntercept, "slope": slope}

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    async def calcLinRegressionY(self, x_new_data: list, y_new_data: list):
        """Calculates the linear regression of the data for the y-axis

        Args:
            x_new_data (list): list of data for x-axis
            y_new_data (list): list of data for y-axis

        Returns:
            _type_: dict
        """
        x_new = np.array(x_new_data)
        y_new = np.array(y_new_data).reshape((-1, 1))
        model = LinearRegression().fit(x_new, y_new)
        r_sq = model.score(x_new, y_new)
        yIntercept = model.intercept_
        slope = model.coef_
        return {"r_sq": r_sq, "yIntercept": yIntercept, "slope": slope}

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
