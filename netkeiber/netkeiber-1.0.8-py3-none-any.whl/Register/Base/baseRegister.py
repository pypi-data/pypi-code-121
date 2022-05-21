import LibHanger.Library.uwLogger as Logger
from sqlalchemy.exc import SQLAlchemyError
from LibHanger.Library.uwGlobals import *
from LibHanger.Library.DataAccess.uwPostgres import uwPostgreSQL
from LibHanger.Library.uwDeclare import uwDeclare as en
from LibHanger.Models.recset import recset
from netkeiber.Library.netkeiberDeclare import netkeiberDeclare as nd
from netkeiber.Library.netkeiberException import registerError
from netkeiber.Getter.log_race_id import getter_log_race_id

class baseRegister():
    
    """
    登録処理基底クラス
    """
    
    def __init__(self, __psgr:uwPostgreSQL, __race_id):
        
        """
        コンストラクタ
        
        Parameters
        ----------
        __psgr : uwPostgreSQL
            uwPostgreSQLクラスインスタンス
        __race_id : str
            レースID
        """
        
        # uwPostgreSQL
        self.__psgr = __psgr
        
        # recset
        self.__recsetList = []
    
        # レースIDログ
        self.raceIdLog = getter_log_race_id()
        
        # レースID
        self.race_id = __race_id
        
        # エラー有無
        self.__hasError = False

    @property
    def hasError(self):
        
        """
        エラー有無
        """
        
        return self.__hasError

    def appendRecsetList(self, __recset:recset):
        
        """
        登録対象レコードセットリストの追加

        Parameters
        ----------
        __recset : recset
            レコードセットクラスインスタンス

        """
        
        # 登録対象リストに追加
        self.__recsetList.append(__recset)
    
    def execSqlfile(self, sql):

        """
        SQLファイルを実行する

        Parameters
        ----------
        sql : str
            実行するSQL

        """
        
        # 結果セット
        result = en.resultRegister.success
        
        try:
            # sql - execute
            self.__psgr.sqlExecute(sql)

            # Commit
            self.__psgr.commit()

        except SQLAlchemyError as e:
            
            # 結果セット
            result = en.resultRegister.failure
            # ログ出力
            Logger.logging.error(e)
            # Rollback
            self.__psgr.rollback()
        
        # 処理結果を返す
        return result
    
    def execUpdate(self):
        
        """
        DB更新処理
        """
        
        # open - session
        self.__psgr.openSession()

        # begin - Transaction
        self.__psgr.beginTransaction()
        
        # レコードセットupdate
        for rs in self.__recsetList:
            rsx:recset = rs
            rsx.setDA(self.__psgr)
            upResult = rsx.upsert()
            if upResult.result == en.resultRegister.failure : break

        # 結果判定
        if upResult.result == en.resultRegister.success:
            # commit
            self.__psgr.commit()
            # レースIDログ追加
            self.raceIdLog.setLogRaceId(self.race_id, nd.getterResult.success)

        elif upResult.result == en.resultRegister.failure:
            try:
                try:
                    # rollback
                    self.__psgr.rollback()
                    # raise
                    raise upResult.exceptInfo
                except SQLAlchemyError as e:
                    raise registerError
            except registerError as e:
                # レースIDログ追加
                self.raceIdLog.setLogRaceId(self.race_id, nd.getterResult.error, e)
        
        # session - close
        self.__psgr.closeSession()
        
        # エラー有無セット
        self.__hasError = False if upResult.result == en.resultRegister.success else True
        
        # 結果を返す
        return upResult.result
        