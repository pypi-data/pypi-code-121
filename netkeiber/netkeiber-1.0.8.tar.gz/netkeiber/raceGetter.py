import sys
import time
import LibHanger.Library.uwGetter as Getter
import LibHanger.Library.uwMath as uwMath
import netkeiber.Library.netkeiberConfiger as hc
from LibHanger.Library.DataAccess.uwPostgres import uwPostgreSQL
from LibHanger.Library.uwDeclare import uwDeclare as en
from LibHanger.Models.recset import recset
from netkeiber.Library.netkeiberGlobals import *
from netkeiber.Library.netkeiberDeclare import netkeiberDeclare as nd
from netkeiber.Getter.get_RaceData import getter_RaceData
from netkeiber.Register.register_RaceData import register_RaceData
from netkeiber.Models.trn_race_id import trn_race_id

def getRaceData(filePath, race_id):
    
    """
    レースデータ取得メソッド

    Parameters
    ----------
    filePath : str
        呼び出し元ファイルのパス
    race_id : str
        レースID
    """
    
    # 共通設定
    hc.netkeiberConfiger(gv, filePath, 'config')

    # uwPostgreSQL
    psgr_register = uwPostgreSQL(gv.config)
    psgr_trn_race_id = uwPostgreSQL(gv.config)
    psgr_getter_RaceData = uwPostgreSQL(gv.config)

    # レースデータ取得クラスインスタンス
    getRaceData = getter_RaceData(psgr_getter_RaceData)

    # 処理時間計測 - 開始
    start = time.perf_counter()

    # レースデータ取得
    psgr_trn_race_id.openSession(True)
    rsRaceId = recset[trn_race_id](trn_race_id)
    rsRaceId.setDA(psgr_trn_race_id)
    rsRaceId.filter(trn_race_id.race_id == race_id)
    if rsRaceId.eof() == False:
        
        # データ取得:パラメーター設定
        getRaceData.openInfoRead = False # 開催情報は取得しない
        race_id = rsRaceId.fields(trn_race_id.race_id.key).value
        racecourse_id = rsRaceId.fields(trn_race_id.racecourse_id.key).value
        # データ取得
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

        # setDA
        rsRaceIdLog.setDA(psgr_register)

        # エラー有無判定
        if getRaceData.hasError == True:
            # レースIDログ登録
            upResult = rsRaceIdLog.upsert()
            if upResult.result == en.resultRegister.success:
                print('◎Regist Error Log Success')
            elif upResult.result == en.resultRegister.failure:
                print('☓Regist Error Log Failure')
            sys.exit()

        # reg
        regRaceData = register_RaceData(psgr_register, race_id)
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
            print('◎DbUpdate - Success')
        elif result == en.resultRegister.failure:
            print('☓DbUpdate - Failed')

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
            print('◎Regist RaceId Success')
        elif riResult.result == en.resultRegister.failure:
            print('☓Regist Error RaceId Failure')
        
        # レースIDログ登録
        rsRaceIdLog = regRaceData.raceIdLog.rsLogRaceId
        rsRaceIdLog.setDA(psgr_register)
        upResult = rsRaceIdLog.upsert()
        if upResult.result == en.resultRegister.success:
            print('◎Regist Log Success')
        elif upResult.result == en.resultRegister.failure:
            print('☓Regist Error Log Failure')

    # Close
    psgr_trn_race_id.closeSession()