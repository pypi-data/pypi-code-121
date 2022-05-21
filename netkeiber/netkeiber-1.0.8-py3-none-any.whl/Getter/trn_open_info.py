import urllib.parse as urlParse
import LibHanger.Library.uwLogger as Logger
from pandas.core.frame import DataFrame
from bs4 import BeautifulSoup
from LibHanger.Models.recset import recset
from Scrapinger.Library.browserContainer import browserContainer
from netkeiber.Library.netkeiberConfig import netkeiberConfig
from netkeiber.Library.netkeiberGlobals import *
from netkeiber.Library.netkeiberException import getterError
from netkeiber.Models.trn_open_info import trn_open_info
from netkeiber.Getter.Base.baseGetter import baseGetter

class getter_trn_open_info(baseGetter):
    
    """
    開催情報取得クラス
    (trn_open_info)
    """
    
    def __init__(self) -> None:
        
        """
        コンストラクタ
        """
        
        super().__init__()

        # レコードセット初期化
        self.rsOpenInfo = recset[trn_open_info](trn_open_info)
    
    @Logger.loggerDecorator("getData",['open_id'])
    def getData(self, *args, **kwargs):
        
        """
        開催情報取得
        
        Parameters
        ----------
        kwargs : dict
            @open_id
                開催ID
        """
        
        # 開催情報をDataFrameで取得
        try:
            kwargs['getter'] = self
            result = self.getOpenInfoDataToDataFrame(**kwargs)
        except Exception as e:
            raise getterError(e)
        return result
    
    @Logger.loggerDecorator("getOpenInfoDataToDataFrame")
    def getOpenInfoDataToDataFrame(self, *args, **kwargs):

        """
        開催情報取得
        
        Parameters
        ----------
        kwargs : dict
            @open_id
                開催ID
        """
        
        # 検索url(ルート)
        rootUrl = urlParse.urljoin(gv.netkeiberConfig.netkeibaUrl, gv.netkeiberConfig.netkeibaUrlSearchKeyword.open)
        # 検索url(開催情報)
        openInfoUrl = urlParse.urljoin(rootUrl, kwargs.get('racecourse_id') + '/' + kwargs.get('open_id'))

        # スクレイピング準備
        self.wdc.settingScrape()

        # ページロード
        self.wdc.browserCtl.loadPage(openInfoUrl)

        # pandasデータを返却する
        return self.wdc.browserCtl.createSearchResultDataFrame(**kwargs)
    
    class beautifulSoup(browserContainer.beautifulSoup):
        
        """
        ブラウザコンテナ:beautifulSoup
        """

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
            開催情報をDataFrameで返す(By BeutifulSoup)
            
            Parameters
            ----------
            soup : BeautifulSoup
                BeautifulSoupオブジェクト
            
            kwargs : dict
                @open_id
                    取得対象開催ID
            """

            # 開催ID取得
            open_id:str = kwargs.get('open_id')

            # getterインスタンス取得
            self.bc:getter_trn_open_info = kwargs.get('getter')
            
            # 競馬場ID取得
            racecourse_id:str = kwargs.get('racecourse_id')
            
            # スクレイピング結果から改行ｺｰﾄﾞを除去
            [tag.extract() for tag in soup(string='\n')]
            
            # class取得
            tables = soup.find(class_="race_table_01").find_all('tr')

            if tables:
                
                # 開催情報model用意
                openInfo = recset[trn_open_info](trn_open_info)
                
                for index in range(len(tables)):
                    if index == 0 : continue
                    try:
                        row = tables[index].find_all('td')
                        # レースNO
                        race_no = row[0].text
                        # レースID
                        race_id = str(row[1].find_all('a')[0].get('href')).split('/')[2]
                        # 勝ち馬ID
                        win_horse = str(row[3].find_all('a')[0].get('href')).split('/')[2]
                        # 勝ち馬騎手ID
                        win_jockey = str(row[3].find_all('a')[1].get('href')).split('/')[2]
                        # 2着馬ID
                        snd_horse = str(row[4].find_all('a')[0].get('href')).split('/')[2]
                        # 2着馬騎手ID
                        snd_jockey = str(row[4].find_all('a')[1].get('href')).split('/')[2]
                        # 3着馬ID
                        trd_horse = str(row[5].find_all('a')[0].get('href')).split('/')[2]
                        # 3着馬騎手ID
                        trd_jockey = str(row[5].find_all('a')[1].get('href')).split('/')[2]

                        # Modelに追加
                        openInfo.newRow()
                        openInfo.fields(trn_open_info.open_id.key).value = open_id
                        openInfo.fields(trn_open_info.racecourse_id.key).value = racecourse_id
                        openInfo.fields(trn_open_info.race_no.key).value = race_no
                        openInfo.fields(trn_open_info.race_id.key).value = race_id
                        openInfo.fields(trn_open_info.win_horse.key).value = win_horse
                        openInfo.fields(trn_open_info.win_jockey.key).value = win_jockey
                        openInfo.fields(trn_open_info.snd_horse.key).value = snd_horse
                        openInfo.fields(trn_open_info.snd_jockey.key).value = snd_jockey
                        openInfo.fields(trn_open_info.trd_horse.key).value = trd_horse
                        openInfo.fields(trn_open_info.trd_jockey.key).value = trd_jockey
                        openInfo.fields(trn_open_info.updinfo.key).value = self.bc.getUpdInfo()
                        
                        # コンソール出力
                        print('開催ID={0}'.format(open_id), end='レースNo={0}'.format(race_no))
                        
                    except Exception as e: # その他例外
                        Logger.logging.error(str(e))
                        raise 

                # レコードセットマージ
                self.bc.rsOpenInfo.merge(openInfo)

                # 戻り値を返す
                return openInfo.getDataFrame()