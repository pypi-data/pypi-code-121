import sys
import time
import LibHanger.Library.uwGetter as Getter
import LibHanger.Library.uwLogger as Logger
import LibHanger.Library.uwMath as uwMath
import netkeiber.Library.netkeiberConfiger as hc
from LibHanger.Library.DataAccess.uwPostgres import uwPostgreSQL
from LibHanger.Library.uwDeclare import uwDeclare as en
from netkeiber.Library.netkeiberGlobals import *
from netkeiber.Library.netkeiberDeclare import netkeiberDeclare as nd
from netkeiber.Models.trn_race_id import trn_race_id
from netkeiber.Getter.trn_race_id import getter_trn_race_id
from netkeiber.Getter.get_RaceData import getter_RaceData
from netkeiber.Register.register_RaceData import register_RaceData

def getRaceData(filePath, year):
    
    """
    レースデータ取得メソッド(年単位)

    Parameters
    ----------
    filePath : str
        呼び出し元ファイルのパス
    year : int
        取得年
    """

    # 共通設定
    hc.netkeiberConfiger(gv, filePath, 'config')

    # レースID情報取得クラスインスタンス
    getTrnRaceId = getter_trn_race_id()

    # レースID情報取得
    for month in range(1,13,1):
        getTrnRaceId.getData(year=year, month=month)

    # レコードセット退避
    rsRaceId = getTrnRaceId.rsRaceId

    # uwPostgreSQL
    psgr_trid = uwPostgreSQL(gv.config) # trn_race_id用
    psgr_grad = uwPostgreSQL(gv.config) # getter用
    psgr_regt = uwPostgreSQL(gv.config) # register用

    # reg
    regRaceData = register_RaceData(psgr_trid)
    regRaceData.appendRecsetList(rsRaceId)
    
    # update
    result = regRaceData.execUpdate()
    if result:
        Logger.logging.info('◎trn_race_id Regist Success Count={0}'.format(str(rsRaceId.recordCount)))
    else:
        Logger.logging.info('☓trn_race_id Regist Failed')
        sys.exit()

    # レースデータ取得クラスインスタンス
    getRaceData = getter_RaceData(psgr_grad)

    # 開始ログ
    Logger.logging.info('>> Started the process of acquiring race data. year={0}'.format(str(year)))

    # trn_race_idループ
    while rsRaceId.eof() == False:

        # 処理時間計測 - 開始
        start = time.perf_counter()
        
        # レースデータ取得:パラメーター設定
        getRaceData.openInfoRead = False # 開催情報は取得しない
        race_id = rsRaceId.fields(trn_race_id.race_id.key).value
        racecourse_id = rsRaceId.fields(trn_race_id.racecourse_id.key).value

        # エラーフラグ初期化
        errorFlg = False

        # 開始ログ
        Logger.logging.info('□===== Started get race_id={0} ====='.format(race_id))

        # レースデータ取得
        getRaceData.getData(race_id=race_id, racecourse_id=racecourse_id)

        # レコードセット退避
        rsRaceResult = getRaceData.raceResult.rsRaceResult
        rsRacdInfo = getRaceData.raceResult.rsRaceInfo
        rsMstHorse = getRaceData.raceResult.rsMstHourse
        rsMstJockey = getRaceData.raceResult.rsMstJockey
        rsMstTrainer = getRaceData.raceResult.rsMstTrainer
        rsMstHowner = getRaceData.raceResult.rsMstHowner
        rsHorseResult = getRaceData.horseResult.rsHorseResult
        rsOpenInfo = getRaceData.openInfo.rsOpenInfo
        rsRefundInfo = getRaceData.refundInfo.rsRefundInfo
        rsRaceIdLog = getRaceData.raceIdLog.rsLogRaceId

        # rsRaceIdLog - setDA
        rsRaceIdLog.setDA(psgr_regt)
        
        # エラー有無判定
        if getRaceData.hasError == True:
            # レースIDログ登録
            upResult = rsRaceIdLog.upsert()
            if upResult.result == en.resultRegister.success:
                Logger.logging.warning('◎log_race_id registration process Succeeded. [Error]')
            elif upResult.result == en.resultRegister.failure:
                Logger.logging.error('☓log_race_id registration process failed.')
            sys.exit()

        # DB更新対象セット
        regRaceData = register_RaceData(psgr_regt, race_id)
        regRaceData.appendRecsetList(rsRaceResult)
        regRaceData.appendRecsetList(rsRacdInfo)
        regRaceData.appendRecsetList(rsMstHorse)
        regRaceData.appendRecsetList(rsMstJockey)
        regRaceData.appendRecsetList(rsMstTrainer)
        regRaceData.appendRecsetList(rsMstHowner)
        regRaceData.appendRecsetList(rsHorseResult)
        regRaceData.appendRecsetList(rsOpenInfo)
        regRaceData.appendRecsetList(rsRefundInfo)

        # update
        result = regRaceData.execUpdate()
        if result == en.resultRegister.success:
            Logger.logging.info('◎Race data registration process Succeeded.')
        elif result == en.resultRegister.failure:
            Logger.logging.error('☓Race data registration process Failed.')

        # 処理時間 - 取得
        procTime = time.perf_counter() - start

        # スクレイピング回数、データ取得時間セット
        rsRaceId.editRow()
        rsRaceId.fields(trn_race_id.scraping_count.key).value = getRaceData.scrapingCount
        rsRaceId.fields(trn_race_id.get_time.key).value = uwMath.round(procTime, uwMath.fraction.round)
        rsRaceId.fields(trn_race_id.get_status.key).value = nd.getStatus.acquired.value
        rsRaceId.fields(trn_race_id.updinfo.key).value = Getter.getNow(Getter.datetimeFormat.updinfo)

        # レースID情報登録
        riResult = rsRaceId.upsert()
        if riResult.result == en.resultRegister.success:
            Logger.logging.info('◎trn_race_id registration process Succeeded.')
        elif riResult.result == en.resultRegister.failure:
            Logger.logging.error('☓trn_race_id registration process Failed.')
        
        # レースIDログ登録
        rsRaceIdLog = regRaceData.raceIdLog.rsLogRaceId
        rsRaceIdLog.setDA(psgr_regt)
        upResult = rsRaceIdLog.upsert()
        if upResult.result == en.resultRegister.success:
            Logger.logging.info('◎log_race_id registration process Succeeded.')
        elif upResult.result == en.resultRegister.failure:
            Logger.logging.error('☓log_race_id registration process Failed.')

        # 終了ログ
        if errorFlg == False:
            Logger.logging.info('□===== Finished get race_id={0} ====='.format(race_id))
        else:
            Logger.logging.warning('■===== Finished get race_id={0} (An error has occured)====='.format(race_id))

    # 終了ログ
    Logger.logging.info('<< Race data acquisition process has been completed. year={0}'.format(str(year)))

