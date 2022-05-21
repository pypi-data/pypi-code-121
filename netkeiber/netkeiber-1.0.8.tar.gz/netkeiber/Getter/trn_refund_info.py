import urllib.parse as urlParse
import LibHanger.Library.uwLogger as Logger
from pandas.core.frame import DataFrame
from bs4 import BeautifulSoup, ResultSet, Tag
from LibHanger.Models.recset import recset
from Scrapinger.Library.browserContainer import browserContainer
from netkeiber.Library.netkeiberConfig import netkeiberConfig
from netkeiber.Library.netkeiberDeclare import netkeiberDeclare as nd
from netkeiber.Library.netkeiberGlobals import *
from netkeiber.Library.netkeiberException import getterError
from netkeiber.Library.netkeiberException import gettingValueError
from netkeiber.Models.trn_refund_info import trn_refund_info
from netkeiber.Getter.Base.baseGetter import baseGetter

class getter_trn_refund_info(baseGetter):
    
    """
    払戻情報取得クラス
    (trn_refund_info)
    """
    
    class payInfo():
        
        """
        払戻情報
        """
        
        seq:int = 0
        """ 連番 """

        horse_no:str = ''
        """ 馬番 """

        pay:int = 0
        """ 払戻金 """
        
        pop:int = 0
        """ 人気 """
        
    def __init__(self) -> None:
        
        """
        コンストラクタ
        """
        
        super().__init__()

        # レコードセット初期化
        self.rsRefundInfo = recset[trn_refund_info](trn_refund_info)
    
    @Logger.loggerDecorator("getData",['refund_id','racecourse_id'])
    def getData(self, *args, **kwargs):
        
        """
        払戻情報取得
        
        Parameters
        ----------
        kwargs : dict
            @refund_id
                払戻ID
        """
        
        # 払戻情報をDataFrameで取得
        try:
            kwargs['getter'] = self
            result = self.getRefundInfoDataToDataFrame(**kwargs)
        except:
            raise getterError
        return result
    
    @Logger.loggerDecorator("getRefundInfoDataToDataFrame")
    def getRefundInfoDataToDataFrame(self, *args, **kwargs):

        """
        払戻情報取得
        
        Parameters
        ----------
        kwargs : dict
            @refund_id
                払戻ID
        """
        
        # 検索url(ルート)
        rootUrl = urlParse.urljoin(gv.netkeiberConfig.netkeibaUrl, gv.netkeiberConfig.netkeibaUrlSearchKeyword.refund)
        # 検索url(払戻情報)
        refundInfoUrl = urlParse.urljoin(rootUrl, kwargs.get('racecourse_id') + '/' + kwargs.get('refund_id'))

        # スクレイピング準備
        self.wdc.settingScrape()

        # ページロード
        self.wdc.browserCtl.loadPage(refundInfoUrl)

        # pandasデータを返却する
        return self.wdc.browserCtl.createSearchResultDataFrame(**kwargs)
    
    def getHorseNo(self, horseNoString:str) -> str:
        
        """
        馬番取得
        
        Parameters
        ----------
        horseNoString : str
            馬番(文字列)
        """
        
        return horseNoString.replace(' ','')
    
    def getPay(self, payString:str) -> int:
        
        """
        払戻金取得

        Parameters
        ----------
        payString : str
            払戻金(文字列)
        """
        
        pay = 0
        
        try:
            pay = int(payString.replace(',','')) if payString != '' else 0
        except:
            raise gettingValueError
    
        return pay
    
    def getPop(self, popString:str) -> int:
        
        """
        人気取得
        
        Parameters
        ----------
        popString : str
            人気(文字列)
        """
        
        pop = 0
        
        try:
            pop = int(popString.replace(' ','')) if popString != '' else 0
        except:
            raise gettingValueError

        return pop
    
    def addRecsetPayInfo(self, 
                         refund_id,
                         racecourse_id,
                         race_no,
                         refund_kbn,
                         piList:list[payInfo], 
                         refundInfo:recset):
        
        """
        払戻情報をレコードセットに追加

        Parameters
        ----------
        refund_id : str
            払戻ID
        racecourse_id : str
            競馬場ID
        race_no : int
            レース番号
        refund_kbn : str
            払戻区分
        piList : list[payInfo]
            払戻情報リスト
        refundInfo : recset
            払戻情報レコードセット

        """
        
        for pi in piList:
            refundInfo.newRow()
            refundInfo.fields(trn_refund_info.refund_id.key).value = refund_id
            refundInfo.fields(trn_refund_info.racecourse_id.key).value = racecourse_id
            refundInfo.fields(trn_refund_info.race_no.key).value = race_no
            refundInfo.fields(trn_refund_info.refund_kbn.key).value = refund_kbn
            refundInfo.fields(trn_refund_info.refund_seq.key).value = pi.seq
            refundInfo.fields(trn_refund_info.horse_no.key).value = pi.horse_no
            refundInfo.fields(trn_refund_info.pay.key).value = pi.pay
            refundInfo.fields(trn_refund_info.pop.key).value = pi.pop
            refundInfo.fields(trn_refund_info.updinfo.key).value = self.getUpdInfo()
    
    def getPayInfoSingle(self, payInfoTable):
        
        """
        払戻情報取得(単)
        """
        
        # 払戻情報初期化
        payInfoSingle = [self.payInfo]
        payInfoSingle.clear()
        
        # 払戻テーブルのループ回数取得
        loopCount = len(payInfoTable[0].contents)
        
        # 連番初期化
        seq = 0
        for contents_idx in range(0,loopCount,1):
            
            if payInfoTable[0].contents[contents_idx].name == 'br': continue
            
            pi = self.payInfo()

            # 連番
            seq += 1
            pi.seq = seq
            # 馬番
            pi.horse_no = self.getHorseNo(str(payInfoTable[0].contents[contents_idx]))
            # 払戻
            pi.pay = self.getPay(str(payInfoTable[1].contents[contents_idx]))
            # 人気
            pi.pop = self.getPop(str(payInfoTable[2].contents[contents_idx]))
            
            # 払戻情報をリストに追加
            payInfoSingle.append(pi)
            
        # 戻り値を返す
        return payInfoSingle
    
    def getPayInfoDouble(self, payInfoTable):
        
        """
        払戻情報取得(複)
        """
        
        # 1組目
        horse_no1:str = self.getHorseNo(str(payInfoTable[0].contents[0]))
        pay1:int = self.getPay(str(payInfoTable[1].contents[0]))
        pop1:int = self.getPop(str(payInfoTable[2].contents[0]))

        # 2組目
        horse_no2:str = self.getHorseNo(str(payInfoTable[0].contents[2]))
        pay2:int = self.getPay(str(payInfoTable[1].contents[2]))
        pop2:int = self.getPop(str(payInfoTable[2].contents[2]))

        # 3組目
        horse_no3:str = self.getHorseNo(str(payInfoTable[0].contents[4]) if len(payInfoTable[0].contents) > 4 else '')
        pay3:int = self.getPay(str(payInfoTable[1].contents[4]) if len(payInfoTable[1].contents) > 4 else '')
        pop3:int = self.getPop(str(payInfoTable[2].contents[4]) if len(payInfoTable[2].contents) > 4 else '')
        
        # 戻り値を返す
        return horse_no1, pay1, pop1, horse_no2, pay2, pop2, horse_no3, pay3, pop3
    
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
            払戻情報をDataFrameで返す(By BeutifulSoup)
            
            Parameters
            ----------
            soup : BeautifulSoup
                BeautifulSoupオブジェクト
            
            kwargs : dict
                @refund_id
                    取得対象払戻ID
            """

            # 払戻テーブル項目名
            pil = gv.netkeiberConfig.settingValueStruct.PayInfoClass
            
            # 払戻ID取得
            refund_id:str = kwargs.get('refund_id')
            # 競馬場ID取得
            racecourse_id:str = kwargs.get('racecourse_id')

            # getterインスタンス取得
            self.bc:getter_trn_refund_info = kwargs.get('getter')
            
            # スクレイピング結果から改行ｺｰﾄﾞを除去
            [tag.extract() for tag in soup(string='\n')]
            
            # class取得
            tables = soup.find_all(class_="race_payback_info")

            if tables:
                
                # 払戻情報model用意
                refundInfo = recset[trn_refund_info](trn_refund_info)
                
                # WebBrowzerController取得
                bc = self.bc
                
                for tables_idx in range(len(tables)):
                    
                    try:
                        
                        # 払戻情報テーブルクラス取得
                        refundInfoTbl:Tag = tables[tables_idx]

                        # dtタグ検索
                        dt = refundInfoTbl.find('dt')
                        # レース番号取得
                        race_no = 0
                        if len(dt.contents) > 0:
                            race_no = int(dt.contents[0].text.replace('R',''))
                        else:
                            raise gettingValueError
                            
                        # 払戻情報テーブルクラス取得
                        payInfo = refundInfoTbl.find_all(class_="pay_table_01")
                        
                        # 払戻情報テーブルには[pay_table_01]クラスが2つ存在する(1つの場合もある)ので
                        # ループしてそれぞれの払戻種類を取得する
                        for payInfo_idx in range(len(payInfo)):
                            
                            # trタグ取得
                            payInfoTbl:Tag = payInfo[payInfo_idx]
                            payInfoTables = payInfoTbl.find_all('tr')
                            for tableIndex in range(len(payInfoTables)):
                                
                                # 払戻情報テーブル取得
                                payInfoRow:Tag = payInfoTables[tableIndex]
                                payInfoTable = payInfoRow.find_all('td')
                                
                                # 単勝
                                tan = payInfoRow.find(class_=pil.win)
                                if tan:
                                    
                                    # 馬番,払戻,人気
                                    piList = bc.getPayInfoSingle(payInfoTable)
                                    
                                    # レコードセットに追加
                                    bc.addRecsetPayInfo(refund_id, 
                                                        racecourse_id, 
                                                        race_no, 
                                                        nd.refundKbn.win.value, 
                                                        piList, 
                                                        refundInfo)
                                    
                                # 複勝
                                fuku = payInfoRow.find(class_=pil.dwin)
                                if fuku:
                                    
                                    # 馬番,払戻,人気
                                    piList = bc.getPayInfoSingle(payInfoTable)
                                    
                                    # レコードセットに追加
                                    bc.addRecsetPayInfo(refund_id, 
                                                        racecourse_id, 
                                                        race_no, 
                                                        nd.refundKbn.dwin.value, 
                                                        piList, 
                                                        refundInfo)
                                # 枠連
                                waku = payInfoRow.find(class_=pil.fcwin)
                                if waku:
                                    
                                    # 馬番,払戻,人気
                                    piList = bc.getPayInfoSingle(payInfoTable)
                                    
                                    # レコードセットに追加
                                    bc.addRecsetPayInfo(refund_id, 
                                                        racecourse_id, 
                                                        race_no, 
                                                        nd.refundKbn.fcwin.value, 
                                                        piList, 
                                                        refundInfo)
                                
                                # 馬連
                                uren = payInfoRow.find(class_=pil.hcwin)
                                if uren:
                                    
                                    # 馬番,払戻,人気
                                    piList = bc.getPayInfoSingle(payInfoTable)
                                    
                                    # レコードセットに追加
                                    bc.addRecsetPayInfo(refund_id, 
                                                        racecourse_id, 
                                                        race_no,
                                                        nd.refundKbn.hcwin.value, 
                                                        piList, 
                                                        refundInfo)
                                    
                                # ワイド
                                wide = payInfoRow.find(class_=pil.wdwin)
                                if wide:
                                    
                                    # 馬番,払戻,人気
                                    piList = bc.getPayInfoSingle(payInfoTable)
                                    
                                    # レコードセットに追加
                                    bc.addRecsetPayInfo(refund_id, 
                                                        racecourse_id, 
                                                        race_no, 
                                                        nd.refundKbn.wdwin.value, 
                                                        piList, 
                                                        refundInfo)
                                
                                # 馬単
                                utan = payInfoRow.find(class_=pil.hswin)
                                if utan:
                                    
                                    # 馬番,払戻,人気
                                    piList = bc.getPayInfoSingle(payInfoTable)
                                    
                                    # レコードセットに追加
                                    bc.addRecsetPayInfo(refund_id, 
                                                        racecourse_id, 
                                                        race_no, 
                                                        nd.refundKbn.hswin.value, 
                                                        piList, 
                                                        refundInfo)
                                
                                # 三連複
                                sanfuku = payInfoRow.find(class_=pil.tdwin)
                                if sanfuku:
                                    
                                    # 馬番,払戻,人気
                                    piList = bc.getPayInfoSingle(payInfoTable)
                                    
                                    # レコードセットに追加
                                    bc.addRecsetPayInfo(refund_id, 
                                                        racecourse_id, 
                                                        race_no, 
                                                        nd.refundKbn.tdwin.value, 
                                                        piList, 
                                                        refundInfo)
                                
                                # 三連単
                                santan = payInfoRow.find(class_=pil.tswin)
                                if santan:
                                    
                                    # 馬番,払戻,人気
                                    piList = bc.getPayInfoSingle(payInfoTable)

                                    # レコードセットに追加
                                    bc.addRecsetPayInfo(refund_id, 
                                                        racecourse_id, 
                                                        race_no, 
                                                        nd.refundKbn.tswin.value, 
                                                        piList, 
                                                        refundInfo)

                    except gettingValueError as gvException: # 値例外
                        Logger.logging.error(str(gvException))
                        raise 
                    except Exception as e: # その他例外
                        Logger.logging.error(str(e))
                        raise 

            # コンソール出力
            print('払戻ID={0}'.format(refund_id))
            
            # レコードセットマージ
            self.bc.rsRefundInfo.merge(refundInfo)

            # 戻り値を返す
            return refundInfo.getDataFrame()
            