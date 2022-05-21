from LibHanger.Library.DataAccess.uwPostgres import uwPostgreSQL
from LibHanger.Models.recset import recset
from LibHanger.Models.saWhere import saWhere
from netkeiber.Getter.Base.baseGetter import baseGetter
from netkeiber.Getter.trn_race_result import getter_trn_race_result
from netkeiber.Getter.trn_horse_result import getter_trn_horse_result
from netkeiber.Getter.trn_open_info import getter_trn_open_info
from netkeiber.Getter.trn_refund_info import getter_trn_refund_info
from netkeiber.Getter.log_race_id import getter_log_race_id
from netkeiber.Models.trn_horse_result import trn_horse_result
from netkeiber.Models.trn_race_info import trn_race_info
from netkeiber.Models.trn_open_info import trn_open_info
from netkeiber.Models.trn_refund_info import trn_refund_info
from netkeiber.Library.netkeiberDeclare import netkeiberDeclare as nd
from netkeiber.Library.netkeiberException import getterError

class getter_RaceData(baseGetter):
    
    """
    レースデータ取得クラス
    """
    
    def __init__(self, __psgr:uwPostgreSQL):
        
        """
        コンストラクタ
        
        Parameters
        ----------
        __psgr : uwPostgreSQL
            uwPostgreSQLクラスインスタンス
        """
        
        # uwPostgreSQL
        self.__psgr = __psgr

        # レース結果取得クラスインスタンス
        self.raceResult = getter_trn_race_result()
        self.raceResult.rsRaceResult.setDA(self.__psgr)
        
        # 競走馬成績取得クラスインスタンス
        self.horseResult = getter_trn_horse_result()
        self.horseResult.rsHorseResult.setDA(self.__psgr)

        # 開催情報取得クラスインスタンス
        self.openInfo = getter_trn_open_info()
        self.openInfo.rsOpenInfo.setDA(self.__psgr)
        
        # 払戻情報取得クラスインスタンス
        self.refundInfo = getter_trn_refund_info()
        self.refundInfo.rsRefundInfo.setDA(self.__psgr)
        
        # レースIDログ
        self.raceIdLog = getter_log_race_id()
        
        # 取得フラグ
        self.openInfoRead = True
        
        # エラー有無
        self.__hasError = False

        # スクレイピング回数
        self.__scrapingCount = 0
        
    @property
    def scrapingCount(self):
        
        """
        スクレイピング回数
        """
        
        return self.__scrapingCount
    
    @property
    def hasError(self):
        
        """
        エラー有無
        """
        
        return self.__hasError
    
    def getData(self, race_id, racecourse_id):
        
        """
        データ取得
        
        Parameters
        ----------
        race_id : str
            レースID
        racecourse_id : str
            競馬場ID
        """
        
        try:
            # session - open
            self.__psgr.openSession()

            # レース結果取得
            self.raceResult.getData(race_id=race_id)
            
            # レース結果の取得件数が0件だった場合は処理を抜ける
            if self.raceResult.rsRaceResult.recordCount == 0:
                return

            # saWhereインスタンス
            saw = saWhere()
            
            # レース結果ループ開始
            rsRaceResult = self.raceResult.rsRaceResult
            rsRaceInfo = self.raceResult.rsRaceInfo
            rsRaceInfo.first()
            while rsRaceResult.eof() == False:
                
                # 競走馬成績取得
                # 取得済データチェック
                saw.clear()
                saw.and_(trn_horse_result.horse_id == rsRaceResult.fields(trn_horse_result.horse_id.key).value) \
                   .and_(trn_horse_result.race_id == rsRaceResult.fields(trn_horse_result.race_id.key).value)
                if self.horseResult.rsHorseResult.find(saw, recset.findOption.cacheAndDataBase) == False:
                    
                    # 競走馬成績取得
                    self.horseResult.getData(horse_id=rsRaceResult.fields(trn_horse_result.horse_id.key).value)
                    
                # 開催情報取得
                dfOpenIdGroup = self.horseResult.rsHorseResult.dfrows.groupby(trn_open_info.open_id.key)
                for open_id, group in dfOpenIdGroup:
                    
                    if self.openInfoRead == False: break
                    
                    # 取得済データチェック
                    rsOpenInfo = self.openInfo.rsOpenInfo
                    saw.clear()
                    saw.and_(trn_open_info.open_id == open_id) \
                       .and_(trn_open_info.racecourse_id == racecourse_id)
                    if rsOpenInfo.find(saw, recset.findOption.cacheAndDataBase) == False:
                        
                        # 開催情報取得
                        self.openInfo.getData(open_id=open_id, racecourse_id=racecourse_id)
                
                # 払戻情報取得
                # 払戻ID取得
                refund_id = rsRaceInfo.fields(trn_race_info.refund_id.key).value
                
                # 取得済データチェック
                rsRefundInfo = self.refundInfo.rsRefundInfo
                saw.clear()
                saw.and_(trn_refund_info.refund_id == refund_id) \
                   .and_(trn_refund_info.racecourse_id == racecourse_id) \
                   .and_(trn_refund_info.race_no == rsRaceInfo.fields(trn_race_info.race_no.key).value)
                if rsRefundInfo.find(saw, recset.findOption.cacheAndDataBase) == False:
                    
                    # 払戻情報取得
                    self.refundInfo.getData(refund_id=refund_id, racecourse_id=racecourse_id)

            # スクレイピング回数取得
            rsList = []
            rsList.append(self.raceResult.scrapingCount)
            rsList.append(self.horseResult.scrapingCount)
            rsList.append(self.openInfo.scrapingCount)
            rsList.append(self.refundInfo.scrapingCount)
            self.__scrapingCount = sum(rsList)

        except getterError as geException:
            self.__hasError = True
            self.raceIdLog.setLogRaceId(race_id, nd.getterResult.error ,geException)
        except Exception as e:
            self.__hasError = True
            self.raceIdLog.setLogRaceId(race_id, nd.getterResult.error ,e)
        finally:
            # session - close
            self.__psgr.closeSession()
