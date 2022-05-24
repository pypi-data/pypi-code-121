from abc import ABC, abstractmethod

import pandas as pd

from tdsql.test_config import TdsqlTestConfig


class BaseClient(ABC):
    @abstractmethod
    def select(self, sql: str, config: TdsqlTestConfig) -> pd.DataFrame:
        pass
