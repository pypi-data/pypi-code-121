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
from netkeiber.Library.netkeiberException import gettingValueError
from netkeiber.Models.trn_horse_result import trn_horse_result
from netkeiber.Getter.Base.baseGetter import baseGetter

class getter_trn_horse_result(baseGetter):
    
    """
    競走馬成績取得クラス
    (trn_horse_result)
    """
    
    def __init__(self) -> None:
        
        """
        コンストラクタ
        """
        
        # 基底側コンストラクタ
        super().__init__()

        # レコードセット初期化
        self.rsHorseResult = recset[trn_horse_result](trn_horse_result)
    
    @Logger.loggerDecorator("getData",['horse_id'])
    def getData(self, *args, **kwargs):
        
        """
        競争馬成績取得
        
        Parameters
        ----------
        kwargs : dict
            @horse_id
                取得対象競走馬ID
        """
        
        # 競争馬成績をDataFrameで取得
        try:
            kwargs['getter'] = self
            result = self.getHorseDataToDataFrame(**kwargs)
        except:
            raise getterError
        return result

    @Logger.loggerDecorator("getHorseDataToDataFrame")
    def getHorseDataToDataFrame(self, *args, **kwargs) -> baseGetter.getterResult:

        """
        競争馬成績取得
        
        Parameters
        ----------
        kwargs : dict
            @horse_id
                取得対象競走馬ID
        """
        
        # 検索url(ルート)
        rootUrl = urlParse.urljoin(gv.netkeiberConfig.netkeibaUrl, gv.netkeiberConfig.netkeibaUrlSearchKeyword.horse)
        # 検索url(競走馬成績)
        horseUrl = urlParse.urljoin(rootUrl, kwargs.get('horse_id'))

        # スクレイピング準備
        if self.wdc.browserCtl is None:
            self.wdc.settingScrape()
        
        # ページロード
        self.wdc.browserCtl.loadPage(horseUrl)
        
        # pandasデータを返却する
        self.wdc.browserCtl.createSearchResultDataFrame(**kwargs)

        # 処理結果追加
        return self.addResult(trn_horse_result.__tablename__, self.rsHorseResult.recordCount, self.rsHorseResult)
        
    def getPace(self, paceString:str):
        
        """
        ペース取得
        
        Parameters
        ----------
            paceString : str
                ペース文字列
        """
        
        paces = paceString.split('-') if paceString.replace('\xa0','') != '' else []
        return paces

    class beautifulSoup(browserContainer.beautifulSoup):
        
        """
        ブラウザコンテナ:beautifulSoup
        """

        class horseResultCol(Enum):
            
            """
            競走馬成績列インデックス
            """
            
            racecourseId = 1
            """ 競馬場(開催)ID """
            
            raceId = 4
            """ レースID"""

            horseNo = 8
            """ 馬番 """
            
            paces = 21
            """ ペース """
            
            winHorseId = 26
            """ 勝馬ID """

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
            競走馬成績をDataFrameで返す(By BeutifulSoup)
            
            Parameters
            ----------
            soup : BeautifulSoup
                BeautifulSoupオブジェクト
            
            kwargs : dict
                @horse_id
                    取得対象競走馬ID
                @race_id
                    取得対象レースID
            """

            # 競走馬ID取得
            horse_id:str = kwargs.get('horse_id')
            
            # getterインスタンス取得
            self.bc:getter_trn_horse_result = kwargs.get('getter')

            # スクレイピング結果から改行ｺｰﾄﾞを除去
            [tag.extract() for tag in soup(string='\n')]
            
            # class取得
            horseResultTables = soup.find(class_="db_h_race_results").find_all('tr')
            if horseResultTables:
                
                # 競走馬成績model用意
                horseResult = recset[trn_horse_result](trn_horse_result)
                
                for index in range(len(horseResultTables)):
                    if index == 0 : continue
                    try:
                        dataTbl:Tag = horseResultTables[index]
                        row:ResultSet = dataTbl.find_all('td')
                        drow = self.getRow(row)
                        # レースID
                        race_id = str(drow[self.horseResultCol.raceId.value].find_all('a')[0].get('href')).split('/')[2]
                        # 競馬場ID
                        racecourse_id = str(drow[self.horseResultCol.racecourseId.value].find_all('a')[0].get('href')).split('/')[3]
                        # 開催ID
                        open_id = str(drow[self.horseResultCol.racecourseId.value].find_all('a')[0].get('href')).split('/')[4]
                        # 開催名称
                        open_nm = drow[self.horseResultCol.racecourseId.value].text
                        # 馬番
                        horse_no = Decimal(drow[self.horseResultCol.horseNo.value].text)
                        # ペース
                        paces = self.bc.getPace(drow[self.horseResultCol.paces.value].text)
                        # 勝ち馬ID
                        win_horse_ids = drow[self.horseResultCol.winHorseId.value].find_all('a')
                        win_horse_id = str(win_horse_ids[0].get('href')).split('/')[2] if len(win_horse_ids) > 0 else ''
                            
                        # Modelに追加
                        horseResult.newRow()
                        horseResult.fields(trn_horse_result.horse_id.key).value = horse_id
                        horseResult.fields(trn_horse_result.race_id.key).value = race_id
                        horseResult.fields(trn_horse_result.horse_no.key).value = horse_no
                        horseResult.fields(trn_horse_result.racecourse_id.key).value = racecourse_id
                        horseResult.fields(trn_horse_result.open_id.key).value = open_id
                        horseResult.fields(trn_horse_result.open_nm.key).value = open_nm
                        horseResult.fields(trn_horse_result.pace_firsth.key).value = paces[0] if len(paces) >= 1 else Null()
                        horseResult.fields(trn_horse_result.pace_latterh.key).value = paces[1] if len(paces) >= 2 else Null()
                        horseResult.fields(trn_horse_result.win_horse_id.key).value = win_horse_id
                        horseResult.fields(trn_horse_result.updinfo.key).value = self.bc.getUpdInfo()
                        
                        # コンソール出力
                        print('競走馬ID={0}'.format(horse_id))
                        print('レースID={0}'.format(race_id))
                        print('馬番={0}'.format(horse_no))
                        
                    except gettingValueError as gvException: # 値例外
                        Logger.logging.error(str(gvException))
                        raise 
                    except Exception as e: # その他例外
                        Logger.logging.error(str(e))
                        raise 
                
                # レコードセットマージ
                self.bc.rsHorseResult.merge(horseResult)
                
                # 戻り値を返す
                return horseResult.getDataFrame()