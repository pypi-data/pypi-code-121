from abc import abstractmethod
import pandas as pd


class IModel:

    def train(self, datas):
        pass

    def predict(self):
        pass


class IPerformanceSender:
    def calculate_performance(self, model: IModel, data: pd.DataFrame):
        pass


class ISupervisedModel(IModel):
    @abstractmethod
    def train(self, train_features, train_targets, test_features, test_targets):
        ...

    @abstractmethod
    def predict(self, features) -> pd.DataFrame:
        ...


class IModelFactory:
    def create_model(self) -> IModel:
        pass
