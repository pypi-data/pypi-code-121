import re
import urllib.parse as urlParse
import LibHanger.Library.uwLogger as Logger
from enum import Enum
from decimal import Decimal
from pandas.core.frame import DataFrame
from bs4 import BeautifulSoup, ResultSet, Tag
from sqlalchemy.sql.elements import Null
from LibHanger.Models.recset import recset
from Scrapinger.Library.browserContainer import browserContainer
from netkeiber.Library.netkeiberConfig import netkeiberConfig
from netkeiber.Library.netkeiberGlobals import *
from netkeiber.Library.netkeiberException import getterError
from netkeiber.Library.netkeiberException import arrivalOrderValueError
from netkeiber.Library.netkeiberException import gettingValueError
from netkeiber.Models.trn_race_info import trn_race_info
from netkeiber.Models.trn_race_result import trn_race_result
from netkeiber.Models.mst_horse import mst_horse
from netkeiber.Models.mst_jockey import mst_jockey
from netkeiber.Models.mst_trainer import mst_trainer
from netkeiber.Models.mst_howner import mst_howner
from netkeiber.Getter.Base.baseGetter import baseGetter

class getter_trn_race_result(baseGetter):
    
    """
    レース結果取得クラス
    (trn_race_result)
    """
    
    def __init__(self) -> None:
        
        """
        コンストラクタ
        """
        
        super().__init__()

        # レコードセット初期化
        self.rsRaceResult = recset[trn_race_result](trn_race_result)
        self.rsRaceInfo = recset[trn_race_info](trn_race_info)
        self.rsMstHourse = recset[mst_horse](mst_horse)
        self.rsMstJockey = recset[mst_jockey](mst_jockey)
        self.rsMstTrainer = recset[mst_trainer](mst_trainer)
        self.rsMstHowner = recset[mst_howner](mst_howner)

    @Logger.loggerDecorator("getData",['race_id'])
    def getData(self, *args, **kwargs):
        
        """
        レース結果取得
        
        Parameters
        ----------
        kwargs : dict
            @race_id
                取得対象レースID
        """
        
        # レース結果をDataFrameで取得
        try:
            kwargs['getter'] = self
            result = self.getRaceDataToDataFrame(**kwargs)
        except:
            raise getterError
        return result
    
    @Logger.loggerDecorator("getRaceDataToDataFrame")
    def getRaceDataToDataFrame(self, *args, **kwargs):

        """
        レース結果取得
        
        Parameters
        ----------
        kwargs : dict
            @race_id
                取得対象レースID
        """
        
        # 検索url(ルート)
        rootUrl = urlParse.urljoin(gv.netkeiberConfig.netkeibaUrl, gv.netkeiberConfig.netkeibaUrlSearchKeyword.race)
        # 検索url(レース結果)
        raceUrl = urlParse.urljoin(rootUrl, kwargs.get('race_id'))

        # スクレイピング準備
        self.wdc.settingScrape()

        # ページロード
        self.wdc.browserCtl.loadPage(raceUrl)
        
        # pandasデータを返却する
        return self.wdc.browserCtl.createSearchResultDataFrame(**kwargs)

    def getArrivalOrder(self, orderString:str):
        aor = gv.netkeiberConfig.settingValueStruct.ArrivalOrder
        icf = gv.netkeiberConfig.settingValueStruct.InCommingFlg
        retInComFlg = icf.defaultInLine
        
        if orderString.isnumeric(): # 着順が数値の場合
            
            # 着順取得
            orderInt = int(orderString)

        else: # 着順が文字の場合
            
            # 着順、入線フラグ取得
            orderInt, retInComFlg = (aor.exclusion, icf.exclusion) if orderString == aor.exclusionJp else \
                                    (aor.disqualification, icf.disqualification) if orderString == aor.disqualificationJp else \
                                    (aor.stop_competition, icf.stop_competition) if orderString == aor.stop_competitionJp else \
                                    (aor.raceCancel, icf.cancel_race) if orderString == aor.raceCancelJp else \
                                    (int(orderString.replace('({0})'.format(icf.accretionJp), '')), icf.accretion) if icf.accretionJp in orderString else \
                                    (-1, retInComFlg)
        
        # 着順が取得できない場合例外とする
        if orderInt == -1:
            raise arrivalOrderValueError
        
        # 戻り値を返す
        return orderInt, retInComFlg
    
    def getTimeSecond(self, timeString:str) -> Decimal:
        timeSecond = 0
        
        try:
            # 分⇒秒変換
            minute = int(timeString.split(':')[0]) * 60
            
            # 秒数取得
            second = timeString.split(':')[1]
            
            # タイムを秒数に変換
            timeSecond = Decimal(minute) + Decimal(second)
            
        except Exception as e:
            Logger.logging.error('Time Convert Error : Value=' + timeString)
            Logger.logging.error(str(e))
            
        return timeSecond
    
    def getCorner(self, cornerString:str):
        corners = cornerString.split('-') if cornerString != '' else []
        return corners
    
    def getLast3furlong(self, last3furlongString:list):
        last3furlong = 0
        
        try:
            # 上がり3ハロン
            if (len(last3furlongString) > 0):
                tmpLast3furlong:str = last3furlongString[0]
                last3furlong = Decimal(tmpLast3furlong) if self.isdigitEx(tmpLast3furlong) else 0
            
        except Exception as e:
            Logger.logging.error('Last3furlong Get Error : Value=' + last3furlongString)
            Logger.logging.error(str(e))
            
        return last3furlong

    def getWinOdds(self, winOddsString:str):
        winOdds = 0
        
        try:
            # 単勝オッズ
            winOdds = Decimal(winOddsString)
            
        except Exception as e:
            Logger.logging.error('win_odds Get Error : Value=' + winOddsString)
            Logger.logging.error(str(e))
            
        return winOdds
    
    def getPopular(self, popularString:list):
        popular = 0
        
        try:
            # 人気
            if (len(popularString) > 0):
                tmpPopular:str = popularString[0]
                popular = int(tmpPopular) if self.isdigitEx(tmpPopular) else 0
                        
        except Exception as e:
            Logger.logging.error('popular Get Error : Value=' + popularString)
            Logger.logging.error(str(e))
            
        return popular
        
    def getHorseWeight(self, horseWeightString:str):
        horseWeight = 0
        
        try:
            # 馬体重(体重部分取得)
            horseWeightTemp = re.sub("\(.+?\)","",horseWeightString)
            if horseWeightTemp.isdigit():
                horseWeight = int(horseWeightTemp)
                
        except Exception as e:
            Logger.logging.error('horse_weight Get Error : Value=' + horseWeight)
            Logger.logging.error(str(e))
            
        return horseWeight
    
    def getWeightDiff(self, weightDiffString:str):
        weightDiff = 0
        
        try:
            # 馬体重(増減部分取得)
            weightDiffTemp:str = re.findall("(?<=\().+?(?=\))", weightDiffString)[0]
            if weightDiffTemp.replace('+','').isdigit():
                weightDiff = int(weightDiffTemp)
                
        except Exception as e:
            Logger.logging.error('horse_weight(diff) Get Error : Value=' + weightDiffString)
            Logger.logging.error(str(e))
            
        return weightDiff
    
    def getPrizeMoney(self, prizeMoneyString:str):
        prizeMoney = 0
        
        try:
            # 賞金
            prizeMoney_str = prizeMoneyString.replace(',','')
            try:
                prizeMoney = Decimal(prizeMoney_str) if prizeMoney_str != '' else 0
            except ValueError as e:
                raise
            
        except Exception as e:
            Logger.logging.error('prize_money Get Error : Value=' + prizeMoneyString)
            Logger.logging.error(str(e))
            raise gettingValueError
            
        return prizeMoney
    
    def getGrade(self, race_nm:str):
        grd = gv.netkeiberConfig.settingValueStruct.Grade
        grade = grd.defaultGrade
        
        # レース名の中にG1,G2,G3の文字列が存在するか
        if 'G1' in race_nm:
            grade = grd.g1Grade
        elif 'G2' in race_nm:
            grade = grd.g2Grade
        elif 'G3' in race_nm:
            grade = grd.g3Grade
                    
        return grade
    
    def getRaceClass(self, classString:str):
        raceClass = ''
        horseSign = ''
        raceClassTmp = classString.split('\xa0\xa0')
        if len(raceClassTmp) > 0:
            if len(raceClassTmp) == 2:
                raceClass = raceClassTmp[0]
                horseSign = raceClassTmp[1]
            elif len(raceClassTmp) == 1:
                raceClass = raceClassTmp[0]

        return raceClass, horseSign

    def getRaceDate(self, raceDateString:str):
        raceDate = raceDateString.replace('年','/').replace('月','/').replace('日','')
        return raceDate
    
    def getOpenInfo(self, openInfoString:str):
        return openInfoString

    def getHorseSign(self, horseSignString:str):
        return horseSignString
    
    def getDirection(self, directionString:str):
        drc = gv.netkeiberConfig.settingValueStruct.Direction
        direction = ''
        
        if drc.Steeplechase in directionString:
            direction = drc.Steeplechase
        elif '左' in directionString:
            direction = drc.left
        elif '右' in directionString:
            direction = drc.right
        
        return direction
    
    def getDistance(self, distanceString:str):
        distance = 0
        
        distanceTmp = str(re.sub(r"\D", "", distanceString))
        if distanceTmp.isdigit():
            distance = int(distanceTmp)
            
        return distance
    
    def getGroundKbn(self, groundKbnString:str):
        gkb = gv.netkeiberConfig.settingValueStruct.GroundKbn
        ground_kbn = gkb.Turf
        
        if gkb.SteeplechaseAbbr in groundKbnString and not (gkb.DirtAbbr in groundKbnString):
            ground_kbn = gkb.Steeplechase_Turf
        elif gkb.SteeplechaseAbbr in groundKbnString and not (gkb.TurfAbbr in groundKbnString):
            ground_kbn = gkb.Steeplechase_Dirt
        elif gkb.SteeplechaseAbbr in groundKbnString and gkb.TurfAbbr in groundKbnString and gkb.DirtAbbr in groundKbnString:
            ground_kbn = gkb.Steeplechase_TurfAndDirt
        elif gkb.TurfAbbr in groundKbnString:
            ground_kbn = gkb.Turf
        elif gkb.DirtAbbr in groundKbnString:
            ground_kbn = gkb.Dirt
        return ground_kbn
    
    def getWeather(self, weatherString:str):
        weather = ''
    
        weatherTmp = weatherString.split(' : ')
        if len(weatherTmp) > 0:
            weather = weatherTmp[1]
        return weather
    
    def getGroundCond(self, groundCondString:str):
        groundCond = ''
        groundCond_d = ''
        
        groundCondTmp = groundCondString.split('\xa0\xa0')
        if len(groundCondTmp) > 0:
            if len(groundCondTmp) == 1:
                groundCond = groundCondTmp[0].split(' : ')[1]
            elif len(groundCondTmp) == 2:
                groundCond = groundCondTmp[0].split(' : ')[1]
                groundCond_d = groundCondTmp[1].split(' : ')[1]

        return groundCond, groundCond_d
    
    def getRaceTime(self, raceTimeString:str):
        raceTime = ''
        
        raceTimeTmp = raceTimeString.split(' : ')
        if len(raceTimeTmp) > 0:
            raceTime = raceTimeTmp[1]
        return raceTime
    
    def getRefundId(self, raceNum):
        refundId = ''

        if raceNum:
            refundInfo = raceNum.find_all('p')[1].find_all('a')[0]
            refundId = str(refundInfo.get('href')).split('/')[4]
        
        return refundId
    
    class beautifulSoup(browserContainer.beautifulSoup):
        
        """
        ブラウザコンテナ:beautifulSoup
        """
        
        class raceResultCol(Enum):
            
            """
            レース結果列インデックス
            """
            
            arrival_order = 0
            """ 着順 """

            frameNo = 1
            """ 枠番 """
            
            horseNo = 2
            """ 馬番 """
            
            horseId = 3
            """ 競走馬ID """

            sexAge = 4
            """ 性齢 """

            weight = 5
            """ 斤量 """

            jockey_id = 6
            """ 騎手ID """
            
            time = 7
            """ タイム """

            arr_diff = 8
            """ 着差 """

            corners = 10
            """ 通過順 """
            
            last3furlong = 11
            """ あがり3ハロン"""

            win_odds = 12
            """ 単勝オッズ """
            
            popular = 13
            """ 人気 """

            horse_weight = 14
            """ 馬体重 """
            
            trainer_id = 18
            """ 調教師ID """
            
            howner_id = 19
            """ 馬主ID """

            prize_money = 20
            """ 賞金 """

        def __init__(self, _config: netkeiberConfig):
            
            """
            コンストラクタ
            
            Parameters
            ----------
                _config : netkeiberConfig
                    共通設定
            """
            
            super().__init__(_config)
            
            self.config = _config
            self.cbCreateSearchResultDataFrameByBeutifulSoup = self.createSearchResultDataFrameByBeutifulSoup

        def createSearchResultDataFrameByBeutifulSoup(self, soup:BeautifulSoup, *args, **kwargs) -> DataFrame:
            
            """
            レース結果をDataFrameで返す(By BeutifulSoup)
            
            Parameters
            ----------
            soup : BeautifulSoup
                BeautifulSoupオブジェクト
            
            kwargs : dict
                @race_id
                    取得対象レースID
            """

            # レースID取得
            race_id:str = kwargs.get('race_id')
            
            # getterインスタンス取得
            self.bc:getter_trn_race_result = kwargs.get('getter')
            
            # スクレイピング結果から改行ｺｰﾄﾞを除去
            [tag.extract() for tag in soup(string='\n')]

            # レース結果class取得
            raceTables = soup.find(class_="race_table_01").find_all('tr')
            
            # レース情報class取得
            dataIntro = soup.find(class_="data_intro")
            
            # 払戻情報class取得
            raceNum = soup.find(class_="race_num")
    
            if dataIntro:
                
                # raceData取得
                raceData = dataIntro.find(class_="racedata")
                if raceData:
    
                    # レース番号
                    race_no = raceData.find('dt').text.replace('\n','').replace('R','').rstrip()
                    
                    # レース名
                    race_nm = raceData.find('h1').text
                    
                    # グレード
                    grade = self.bc.getGrade(race_nm)
                    
                # diary_snap_cut取得
                diarySnapCut = dataIntro.find_all('diary_snap_cut')
                if diarySnapCut:
                    
                    # コース概要
                    course_summarys = str(diarySnapCut[0].find('span').text)
                    
                    diary = course_summarys.split('\xa0/\xa0')
                    if len(diary) > 0:
                        
                        # コース概要
                        course_summary = diary[0]
                        # 向き 
                        direction = self.bc.getDirection(diary[0])
                        # 距離
                        distance = self.bc.getDistance(diary[0])
                        # 芝/ダート
                        ground_kbn = self.bc.getGroundKbn(diary[0])
                        # 天候
                        weather = self.bc.getWeather(diary[1])
                        # 馬場状態
                        ground_cond, ground_cond_d = self.bc.getGroundCond(diary[2])
                        # 発送時刻
                        race_time = self.bc.getRaceTime(diary[3])

                # 払戻ID
                refund_id = self.bc.getRefundId(raceNum)

                # レース概要取得
                # 取得例)2021年12月12日 6回阪神4日目 2歳オープン&nbsp;&nbsp;(国際) 牝(指)(馬齢)
                # [0]:日付
                # [1]:開催情報
                # [2]:クラス
                # [3]:馬名記号
                raceInfoSummaryString = str(dataIntro.find_all('p')[1].text)
                raceInfoSummary = raceInfoSummaryString.split(' ')
                
                # 日付
                race_date = self.bc.getRaceDate(raceInfoSummary[0])

                # 開催情報
                open_info = self.bc.getOpenInfo(raceInfoSummary[1])

                # クラス名、馬名記号
                class_nm, horse_sign = self.bc.getRaceClass(raceInfoSummary[2])

                # レース情報model用意
                raceInfo = recset[trn_race_info](trn_race_info)
                
                # Modelに追加
                raceInfo.newRow()
                raceInfo.fields(trn_race_info.race_id.key).value = race_id
                raceInfo.fields(trn_race_info.race_no.key).value = race_no
                raceInfo.fields(trn_race_info.race_nm.key).value = race_nm
                raceInfo.fields(trn_race_info.grade.key).value = grade
                raceInfo.fields(trn_race_info.course_summary.key).value = course_summary
                raceInfo.fields(trn_race_info.direction.key).value = direction
                raceInfo.fields(trn_race_info.distance.key).value = distance
                raceInfo.fields(trn_race_info.ground_kbn.key).value = ground_kbn
                raceInfo.fields(trn_race_info.weather.key).value = weather
                raceInfo.fields(trn_race_info.ground_cond.key).value = ground_cond
                raceInfo.fields(trn_race_info.ground_cond_d.key).value = ground_cond_d
                raceInfo.fields(trn_race_info.race_date.key).value = race_date
                raceInfo.fields(trn_race_info.race_time.key).value = race_time
                raceInfo.fields(trn_race_info.open_info.key).value = open_info
                raceInfo.fields(trn_race_info.class_nm.key).value = class_nm
                raceInfo.fields(trn_race_info.horse_sign.key).value = horse_sign
                raceInfo.fields(trn_race_info.head_count.key).value = len(raceTables) - 1
                raceInfo.fields(trn_race_info.racecourse_id.key).value = race_id[4:6]
                raceInfo.fields(trn_race_info.refund_id.key).value = refund_id
                raceInfo.fields(trn_race_info.updinfo.key).value = self.bc.getUpdInfo()
                
            if raceTables:
                
                # 先着馬のタイム
                bef_time_second = 0
                # 1着馬との着差
                tarr_diff_num = 0

                # レース結果model用意 
                raceResult = recset[trn_race_result](trn_race_result)

                # 競走馬マスタmodel用意
                mstHorse = recset[mst_horse](mst_horse)

                # 騎手マスタmodel用意
                mstJokey = recset[mst_jockey](mst_jockey)

                # 調教師マスタmodel用意
                mstTrainer = recset[mst_trainer](mst_trainer)

                # 馬主マスタmodel用意
                mstHowner = recset[mst_howner](mst_howner)
                
                for index in range(len(raceTables)):
                    if index == 0 : continue
                    try:
                        dataTbl:Tag = raceTables[index]
                        row:ResultSet = dataTbl.find_all('td')
                        drow = self.getRow(row)
                        # 着順
                        arrival_order, incommingFlg = self.bc.getArrivalOrder(drow[self.raceResultCol.arrival_order.value].text)
                        # 枠番
                        frameNo = Decimal(drow[self.raceResultCol.frameNo.value].text)
                        # 馬番
                        horseNo = Decimal(drow[self.raceResultCol.horseNo.value].text)
                        # 馬ID
                        horseId = str(drow[self.raceResultCol.horseId.value].find_all('a')[0].get('href')).split('/')[2]
                        # 馬名
                        horseNm = drow[self.raceResultCol.horseId.value].text
                        # 性齢
                        sexAge = drow[self.raceResultCol.sexAge.value].text
                        # 斤量
                        weight = Decimal(drow[self.raceResultCol.weight.value].text)
                        # 騎手ID
                        jockey_id = str(drow[self.raceResultCol.jockey_id.value].find_all('a')[0].get('href')).split('/')[4]
                        # 騎手名
                        jockey_nm = drow[self.raceResultCol.jockey_id.value].text
                        # タイム
                        time = drow[self.raceResultCol.time.value].text
                        # タイム(数値)
                        time_second = self.bc.getTimeSecond(time)
                        # 着差
                        arr_diff = drow[self.raceResultCol.arr_diff.value].text
                        # 着差(秒)
                        barr_diff_num = time_second - bef_time_second if arr_diff != '' else 0
                        # 着差(累計)
                        tarr_diff_num += barr_diff_num
                        # 通過順
                        corners = self.bc.getCorner(drow[self.raceResultCol.corners.value].text)
                        # 上がり3ハロン
                        last3furlong = self.bc.getLast3furlong(drow[self.raceResultCol.last3furlong.value].find_all('span')[0].contents)
                        # 単勝オッズ
                        win_odds = self.bc.getWinOdds(drow[self.raceResultCol.win_odds.value].text)
                        # 人気
                        popular = self.bc.getPopular(drow[self.raceResultCol.popular.value].find_all('span')[0].contents)
                        # 馬体重
                        horse_weight = self.bc.getHorseWeight(drow[self.raceResultCol.horse_weight.value].text)
                        # 馬体重増減
                        weight_diff = self.bc.getWeightDiff(drow[self.raceResultCol.weight.value].text)
                        # 調教師ID
                        trainer_id = str(drow[self.raceResultCol.trainer_id.value].find_all('a')[0].get('href')).split('/')[4]
                        # 調教師名
                        trainer_nm = drow[self.raceResultCol.trainer_id.value].text
                        trainer_nm = trainer_nm.replace('\n','')
                        # 馬主ID
                        howner_id = str(drow[self.raceResultCol.howner_id.value].find_all('a')[0].get('href')).split('/')[4]
                        # 馬主名
                        howner_nm = drow[self.raceResultCol.howner_id.value].text
                        howner_nm = howner_nm.replace('\n','')
                        # 賞金
                        prize_money = self.bc.getPrizeMoney(drow[self.raceResultCol.prize_money.value].text)
                        
                        # Modelに追加
                        raceResult.newRow()
                        raceResult.fields(trn_race_result.race_id.key).value = race_id
                        raceResult.fields(trn_race_result.horse_no.key).value = horseNo
                        raceResult.fields(trn_race_result.arrival_order.key).value = arrival_order
                        raceResult.fields(trn_race_result.incoming_flg.key).value = incommingFlg
                        raceResult.fields(trn_race_result.horse_id.key).value = horseId
                        raceResult.fields(trn_race_result.horse_nm_en.key).value = horseNm if horseId == '' else ''
                        raceResult.fields(trn_race_result.frame_no.key).value = frameNo
                        raceResult.fields(trn_race_result.sex_age.key).value = sexAge
                        raceResult.fields(trn_race_result.weight.key).value = weight
                        raceResult.fields(trn_race_result.jockey_id.key).value = jockey_id
                        raceResult.fields(trn_race_result.time.key).value = time
                        raceResult.fields(trn_race_result.time_second.key).value = time_second
                        raceResult.fields(trn_race_result.arr_diff.key).value = arr_diff
                        raceResult.fields(trn_race_result.barr_diff_num.key).value = barr_diff_num
                        raceResult.fields(trn_race_result.tarr_diff_num.key).value = tarr_diff_num
                        raceResult.fields(trn_race_result.corner1.key).value = corners[0] if len(corners) >= 1 else Null()
                        raceResult.fields(trn_race_result.corner2.key).value = corners[1] if len(corners) >= 2 else Null()
                        raceResult.fields(trn_race_result.corner3.key).value = corners[2] if len(corners) >= 3 else Null()
                        raceResult.fields(trn_race_result.corner4.key).value = corners[3] if len(corners) >= 4 else Null()
                        raceResult.fields(trn_race_result.last3furlong.key).value = last3furlong
                        raceResult.fields(trn_race_result.win_odds.key).value = win_odds
                        raceResult.fields(trn_race_result.popular.key).value = popular
                        raceResult.fields(trn_race_result.horse_weight.key).value = horse_weight
                        raceResult.fields(trn_race_result.weight_diff.key).value = weight_diff
                        raceResult.fields(trn_race_result.trainer_id.key).value = trainer_id
                        raceResult.fields(trn_race_result.howner_id.key).value = howner_id
                        raceResult.fields(trn_race_result.prize_money.key).value = prize_money
                        raceResult.fields(trn_race_result.updinfo.key).value = self.bc.getUpdInfo()

                        # 競争馬マスタ追加
                        mstHorse.newRow()
                        mstHorse.fields(mst_horse.horse_id.key).value = horseId
                        mstHorse.fields(mst_horse.horse_nm.key).value = horseNm
                        mstHorse.fields(mst_horse.birthday.key).value = Null()
                        mstHorse.fields(mst_horse.updinfo.key).value = self.bc.getUpdInfo()

                        # 騎手マスタ追加
                        mstJokey.newRow()
                        mstJokey.fields(mst_jockey.jockey_id.key).value = jockey_id
                        mstJokey.fields(mst_jockey.jockey_nm.key).value = jockey_nm
                        mstJokey.fields(mst_jockey.birthday.key).value = Null()
                        mstJokey.fields(mst_jockey.updinfo.key).value = self.bc.getUpdInfo()

                        # 調教師マスタ追加
                        mstTrainer.newRow()
                        mstTrainer.fields(mst_trainer.trainer_id.key).value = trainer_id
                        mstTrainer.fields(mst_trainer.trainer_nm.key).value = trainer_nm
                        mstTrainer.fields(mst_trainer.birthday.key).value = Null()
                        mstTrainer.fields(mst_trainer.updinfo.key).value = self.bc.getUpdInfo()

                        # 馬主マスタ追加
                        mstHowner.newRow()
                        mstHowner.fields(mst_howner.howner_id.key).value = howner_id
                        mstHowner.fields(mst_howner.howner_nm.key).value = howner_nm
                        mstHowner.fields(mst_howner.updinfo.key).value = self.bc.getUpdInfo()
                        
                        # コンソール出力
                        print('着順={0}'.format(str(arrival_order)))
                        print('枠番={0}'.format(str(frameNo)))
                        print('馬番={0}'.format(str(horseNo)))
                        print('馬ID={0}'.format(horseId))
                        print('馬名={0}'.format(horseNm))

                        # 当該馬のタイム退避
                        bef_time_second = time_second
                        
                    except arrivalOrderValueError as aoException: # 着順例外
                        Logger.logging.error(str(aoException))
                        raise 
                    except gettingValueError as gvException: # 値例外
                        Logger.logging.error(str(gvException))
                        raise 
                    except Exception as e: # その他例外
                        Logger.logging.error(str(e))
                        raise 
                
                # レコードセットマージ
                self.bc.rsRaceResult.merge(raceResult)
                self.bc.rsRaceInfo.merge(raceInfo)
                self.bc.rsMstHourse.merge(mstHorse)
                self.bc.rsMstJockey.merge(mstJokey)
                self.bc.rsMstTrainer.merge(mstTrainer)
                self.bc.rsMstHowner.merge(mstHowner)
                
                # 戻り値を返す
                return raceResult.getDataFrame()
                