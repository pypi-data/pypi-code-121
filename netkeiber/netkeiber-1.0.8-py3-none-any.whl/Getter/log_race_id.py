import LibHanger.Library.uwLogger as Logger
import LibHanger.Library.uwGetter as CmnGetter
from enum import Enum
from LibHanger.Models.recset import recset
from netkeiber.Getter.Base.baseGetter import baseGetter
from netkeiber.Models.log_race_id import log_race_id
from netkeiber.Library.netkeiberException import baseException

class getter_log_race_id(baseGetter):
    
    """
    レースIDログクラス
    (log_race_id)
    """
    
    def __init__(self) -> None:
        
        """
        コンストラクタ
        """
        
        # 基底側コンストラクタ
        super().__init__()

        # レコードセット初期化
        self.rsLogRaceId = recset[log_race_id](log_race_id)
    
    def setLogRaceId(self, race_id, getterResult:Enum, e:baseException = None):
        
        """
        レースIDログ-レコードセット生成
        
        Parameters
        ----------
        race_id : str
            レースID
        getterResult : netkeiberDeclare.getterResult
            処理結果
        e : getterError
            getter例外
        """
        
        # レースIDログ生成
        self.rsLogRaceId.newRow()
        self.rsLogRaceId.fields(log_race_id.race_id.key).value = race_id
        self.rsLogRaceId.fields(log_race_id.create_datetime.key).value = CmnGetter.getNow()
        self.rsLogRaceId.fields(log_race_id.result.key).value = getterResult.value
        if not e is None and isinstance(e,baseException):
            self.rsLogRaceId.fields(log_race_id.uuid.key).value = e.exc_uuid
            self.rsLogRaceId.fields(log_race_id.type.key).value = str(e.exc_type)[:50]
            self.rsLogRaceId.fields(log_race_id.value.key).value = str(e.exc_value)[:50]
            self.rsLogRaceId.fields(log_race_id.stacktrace.key).value = e.exc_traceback[:2000]
        elif not e is None:
            self.rsLogRaceId.fields(log_race_id.stacktrace.key).value = str(e)
        self.rsLogRaceId.fields(log_race_id.updinfo.key).value = CmnGetter.getNow(CmnGetter.datetimeFormat.updinfo)
        
        # ログ出力
        if not e is None and isinstance(e,baseException):
            Logger.logging.error(e.exc_uuid)
            Logger.logging.error(e.exc_type)
            Logger.logging.error(e.exc_value)
            Logger.logging.error(e.exc_traceback)
        elif not e is None:
            Logger.logging.error(str(e))
            