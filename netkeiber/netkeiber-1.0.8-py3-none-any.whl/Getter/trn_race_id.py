import urllib.parse as urlParse
import LibHanger.Library.uwLogger as Logger
from pandas.core.frame import DataFrame
from bs4 import BeautifulSoup
from LibHanger.Models.recset import recset
from Scrapinger.Library.browserContainer import browserContainer
from netkeiber.Library.netkeiberConfig import netkeiberConfig
from netkeiber.Library.netkeiberGlobals import *
from netkeiber.Library.netkeiberException import racdIdCheckError
from netkeiber.Library.netkeiberDeclare import netkeiberDeclare as nd
from netkeiber.Models.trn_race_id import trn_race_id
from netkeiber.Getter.Base.baseGetter import baseGetter

class getter_trn_race_id(baseGetter):
    
    """
    レースID情報取得クラス
    (trn_race_id)
    """

    def __init__(self) -> None:
        
        """
        コンストラクタ
        """
        
        super().__init__()

        # レコードセット初期化
        self.rsRaceId = recset[trn_race_id](trn_race_id)

    @Logger.loggerDecorator("getData",['year'])
    def getData(self, *args, **kwargs):
        
        """
        開催情報取得
        
        Parameters
        ----------
        kwargs : dict
            @year
                開催年
            @month
                開催月
        """
        
        # 開催日情報をDataFrameで取得
        kwargs['getter'] = self
        dfRaceIdCal = self.getRaceIdCalToDataFrame(**kwargs)

        # 取得した開催日をループして1つずつRaceIdを取り出す
        for index, item in dfRaceIdCal.iterrows():
            kwargs['open_id'] = item[trn_race_id.open_id.name]
            kwargs['racecourse_id'] = item[trn_race_id.racecourse_id.name]
            self.getRaceIdToDataFrame(**kwargs)
    
    @Logger.loggerDecorator("getRaceIdDataToDataFrame")
    def getRaceIdCalToDataFrame(self, *args, **kwargs):

        """
        レースID情報取得(カレンダー取得)
        
        Parameters
        ----------
        kwargs : dict
            @year
                開催年度
            @month
                開催月
        """
        
        # 検索url(ルート)
        rootUrl = urlParse.urljoin(gv.netkeiberConfig.netkeibaUrl_race, gv.netkeiberConfig.netkeibaUrlSearchKeyword.race_id_cal)
        # 検索url(レースID情報[カレンダー])
        raceIdCalUrl = rootUrl.format(kwargs.get('year'), kwargs.get('month'))

        # スクレイピング準備
        self.wdc.settingScrape()

        # ページロード
        self.wdc.browserCtl.loadPage(raceIdCalUrl)

        # pandasデータを返却する
        return self.wdc.browserCtl.createSearchResultDataFrame(**kwargs)

    @Logger.loggerDecorator("getRaceIdToDataFrame")
    def getRaceIdToDataFrame(self, *args, **kwargs):

        """
        レースID情報取得
        
        Parameters
        ----------
        kwargs : dict
            @racecourse_id
                競馬場ID
            @open_id
                開催ID
        """
        
        # 検索url(ルート)
        rootUrl = urlParse.urljoin(gv.netkeiberConfig.netkeibaUrl, gv.netkeiberConfig.netkeibaUrlSearchKeyword.open)
        # 検索url(開催情報)
        raceIdUrl = urlParse.urljoin(rootUrl, kwargs.get('racecourse_id') + '/' + kwargs.get('open_id'))

        # スクレイピング準備
        self.wdc.settingScrape()

        # ページロード
        self.wdc.browserCtl.loadPage(raceIdUrl)

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
        
        def getOpenCal(self, soup:BeautifulSoup, *args, **kwargs):
            
            """
            開催日カレンダー情報を取得する
            
            Parameters
            ----------
            soup : BeautifulSoup
                BeautifulSoupオブジェクト
            
            kwargs : dict
                @year
                    開催年度
            """

            # getterインスタンス取得
            self.bc:getter_trn_race_id = kwargs.get('getter')

            # スクレイピング結果から改行ｺｰﾄﾞを除去
            [tag.extract() for tag in soup(string='\n')]
            
            # class取得
            tables = soup.find(class_="Calendar_Table").find_all(class_='RaceCellBox')

            if tables:
                
                # レースIDカレンダー情報model用意
                raceIdCalInfo = recset[trn_race_id](trn_race_id)
                
                for index in range(len(tables)):
                    try:
                        # 開催ID
                        open_id_a = tables[index].find_all('a')
                        if open_id_a:
                            open_id_href = open_id_a[0].get('href')
                            open_id = str(open_id_href).split('=')[1]
                        else:
                            continue
                        
                        jyo_name = tables[index].find_all(class_="JyoName")
                        for index in range(len(jyo_name)):
                            
                            # 競馬場名
                            course_nm = jyo_name[index].text
                            # 競馬場ID
                            racecourse_id = gv.netkeiberConfig.courseList[course_nm]
                            
                            # Modelに追加
                            raceIdCalInfo.newRow()
                            raceIdCalInfo.fields(trn_race_id.race_id.key).value = '*'
                            raceIdCalInfo.fields(trn_race_id.racecourse_id.key).value = racecourse_id
                            raceIdCalInfo.fields(trn_race_id.open_id.key).value = open_id
                            raceIdCalInfo.fields(trn_race_id.updinfo.key).value = self.bc.getUpdInfo()

                            # コンソール出力
                            print('競馬場ID={0}'.format(racecourse_id))
                            print('開催ID={0}'.format(open_id))
                        
                    except Exception as e: # その他例外
                        Logger.logging.error(str(e))
                
                return raceIdCalInfo.getDataFrame()

        def getRaceId(self, soup:BeautifulSoup, *args, **kwargs):
            
            """
            レースID情報を取得する
            
            Parameters
            ----------
            soup : BeautifulSoup
                BeautifulSoupオブジェクト
            
            kwargs : dict
                @open_id
                    開催ID
                @racecourse_id
                    競馬場ID
            """

            # getterインスタンス取得
            self.bc:getter_trn_race_id = kwargs.get('getter')
            
            # 開催ID取得
            open_id:str = kwargs.get('open_id')

            # 競馬場ID取得
            racecourse_id:str = kwargs.get('racecourse_id')
            
            # スクレイピング結果から改行ｺｰﾄﾞを除去
            [tag.extract() for tag in soup(string='\n')]
            
            # class取得
            tables = soup.find(class_="race_table_01").find_all('tr')

            if tables:
                
                # レースID情報model用意
                raceIdInfo = recset[trn_race_id](trn_race_id)
                
                for index in range(len(tables)):
                    if index == 0 : continue
                    try:
                        # tdタグ取得
                        row = tables[index].find_all('td')

                        # レースID
                        race_id = str(row[1].find_all('a')[0].get('href')).split('/')[2]

                        # レースIDが数値で構成されていなければ例外を発生させる
                        if not race_id.isdigit():
                            raise racdIdCheckError
                        
                        # Modelに追加
                        raceIdInfo.newRow()
                        raceIdInfo.fields(trn_race_id.race_id.key).value = race_id
                        raceIdInfo.fields(trn_race_id.racecourse_id.key).value = racecourse_id
                        raceIdInfo.fields(trn_race_id.open_id.key).value = open_id
                        raceIdInfo.fields(trn_race_id.scraping_count.key).value = 0
                        raceIdInfo.fields(trn_race_id.get_time.key).value = 0
                        raceIdInfo.fields(trn_race_id.get_status.key).value = nd.getStatus.unacquired.value
                        raceIdInfo.fields(trn_race_id.updinfo.key).value = self.bc.getUpdInfo()
                        
                        # コンソール出力
                        print('レースID={0}'.format(race_id))
                        print('競馬場ID={0}'.format(racecourse_id))
                        print('開催日={0}'.format(open_id))
                    
                    except racdIdCheckError as e:
                        Logger.logging.error(str(e))
                        Logger.logging.error('race_id Value={0}'.format(race_id))
                        Logger.logging.error('open_id Value={0}'.format(open_id))

                    except Exception as e: # その他例外
                        Logger.logging.error(str(e))
                
                # レコードセットマージ
                self.bc.rsRaceId.merge(raceIdInfo)
                
                # 戻り値をDataFrameで返却
                return raceIdInfo.getDataFrame()
                    
        def createSearchResultDataFrameByBeutifulSoup(self, soup:BeautifulSoup, *args, **kwargs) -> DataFrame:
            
            """
            レースID情報をDataFrameで返す(By BeutifulSoup)
            
            Parameters
            ----------
            soup : BeautifulSoup
                BeautifulSoupオブジェクト
            
            kwargs : dict
                @year
                    開催年度
                @month
                    開催月
                @kaisai_date
                    開催日
            """

            if kwargs.get('open_id') == None:
                return self.getOpenCal(soup, *args, **kwargs)
            else:
                return self.getRaceId(soup, *args, **kwargs)
