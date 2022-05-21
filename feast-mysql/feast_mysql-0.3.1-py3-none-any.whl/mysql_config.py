from typing import Optional
from pydantic import StrictStr

from feast.repo_config import FeastConfigBaseModel


class MySQLConfig(FeastConfigBaseModel):
    database: Optional[StrictStr]
    host: StrictStr
    port: int = 3306
    user: StrictStr
    password: StrictStr
