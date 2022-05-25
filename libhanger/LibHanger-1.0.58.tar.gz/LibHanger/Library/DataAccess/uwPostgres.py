from LibHanger.Library.DataAccess.Base.uwDataAccess import uwDataAccess
from LibHanger.Library.uwConfig import cmnConfig

class uwPostgreSQL(uwDataAccess):
    
    def __init__(self, config: cmnConfig) -> None:
        super().__init__(config)