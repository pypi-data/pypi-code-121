from kolibri.core.component import Component
from sklearn.preprocessing import PowerTransformer
import numpy as np



class RegressionTargetTransformation(Component):
    """
    - Applies Power Transformation (yeo-johnson , Box-Cox) to target variable (Applicable to Regression only)
      - 'bc' for Box_Coc & 'yj' for yeo-johnson, default is Box-Cox
    - if target containes negtive / zero values , yeo-johnson is automatically selected

  """

    def __init__(self, target, function_to_apply="bc"):
        self.target = target
        if function_to_apply == "bc":
            function_to_apply = "box-cox"
        else:
            function_to_apply = "yeo-johnson"
        self.function_to_apply = function_to_apply

    def inverse_transform(self, dataset, y=None):
        data = self.p_transform_target.inverse_transform(
            np.array(dataset).reshape(-1, 1)
        )
        return data

    def fit(self, dataset, y=None):
        self.fit_transform(dataset, y=y)

        return self

    def transform(self, dataset, y=None):
        data = dataset
        if self.target in dataset.columns:
            # apply transformation
            data[self.target] = self.p_transform_target.transform(
                np.array(data[self.target]).reshape(-1, 1)
            )
        return data

    def fit_transform(self, dataset, y=None):
        data = dataset
        # if target has zero or negative values use yj instead
        if any(data[self.target] <= 0):
            self.function_to_apply = "yeo-johnson"
        # apply transformation
        self.p_transform_target = PowerTransformer(method=self.function_to_apply)
        data[self.target] = self.p_transform_target.fit_transform(
            np.array(data[self.target]).reshape(-1, 1)
        )

        return data