import os
import LibHanger.Library.uwLogger as Logger
from netkeiber.Register.Base.baseRegister import baseRegister
from LibHanger.Library.DataAccess.uwPostgres import uwPostgreSQL
from LibHanger.Models.recset import recset

class register_mst_racecourse(baseRegister):
    
    """
    競馬場マスタ登録クラス
    """
    
    def __init__(self, __psgr: uwPostgreSQL, __recset: recset):

        """
        コンストラクタ
        """

        # 基底側コンストラクタ
        super().__init__(__psgr, __recset)
    
    def createInitialData(self, initDataSQLFilePath):
        
        """
        競馬場マスタ初期データ作成
        
        Parameters
        ----------
        initDataSQLFilePath : str
            競馬場マスタ初期データ作成SQLファイルパス
        """
        
        # ファイルパスが見つからない場合処理を中断
        if not os.path.exists(initDataSQLFilePath) : return
        
        # 実行するSQLファイル読込
        with open(initDataSQLFilePath) as sqlfile:
            
            # ファイル読込
            sqldata = sqlfile.read()
            # SQL実行
            result = self.execSqlfile(self.__psgr, sqldata)
            # 結果判定
            if result == self.resultRegister.success:
                Logger.logging.info('execute ok file={}'.format(initDataSQLFilePath))
            elif result == self.resultRegister.failure:
                Logger.logging.error('execute error file={}'.format(initDataSQLFilePath))
