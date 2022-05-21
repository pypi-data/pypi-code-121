import LibHanger.Library.uwLogger as Logger
from LibHanger.Library.DataAccess.uwPostgres import uwPostgreSQL
from netkeiber.Register.Base.baseRegister import baseRegister
from LibHanger.Models.recset import recset

class register_trn_race_result(baseRegister):

    def __init__(self, __psgr: uwPostgreSQL, __recset: recset):
        super().__init__(__psgr, __recset)
        
        self.recset = __recset