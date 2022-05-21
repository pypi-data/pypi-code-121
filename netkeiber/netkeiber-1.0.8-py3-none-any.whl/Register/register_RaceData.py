from LibHanger.Library.DataAccess.uwPostgres import uwPostgreSQL
from netkeiber.Register.Base.baseRegister import baseRegister

class register_RaceData(baseRegister):
    
    """
    レースデータ一括登録クラス
    """
    
    def __init__(self, __psgr:uwPostgreSQL, __race_id = '*'):
        
        """
        コンストラクタ
        """
        
        # 基底側コンストラクタ
        super().__init__(__psgr, __race_id)
    