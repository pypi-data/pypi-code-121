from Scrapinger.Library.scrapingConfig import scrapingConfig

class netkeiberConfig(scrapingConfig):
    
    """
    netkeiber共通設定クラス(netkeiberConfig)
    """ 
    
    class settingValueStruct(scrapingConfig.settingValueStruct):

        """
        設定値構造体
        """ 

        class SearchKeyword:
            
            """
            SearchKeyword
            """ 
            
            race = 'race/'
            """ レース検索 """

            horse = 'horse/'
            """ 競走馬検索 """

            jockey = 'jockey/'
            """ 騎手検索 """

            trainer = 'trainer/'
            """ 調教師検索 """
            
            howner = 'howner/'
            """ 馬主検索 """
            
            open = 'race/sum/'
            """ 開催情報検索 """

            refund = 'race/pay/'
            """ 払戻情報検索 """
            
            race_id_cal = 'top/calendar.html?year={0}&month={1}'
            """ レースID情報検索(カレンダー) """

            race_id_kaisai_date = 'top/race_list.html?kaisai_date={0}'
            """ レースID情報検索(開催日) """
            
            def __init__(self):
                
                """ 
                コンストラクタ
                """ 

                # メンバ変数初期化
                self.race = ''
                self.horse = ''
                self.jockey = ''
                self.trainer = ''
                self.howner = ''
                self.open = ''
                self.refund = ''
                self.race_id_cal = ''
                self.race_id_kaisai_date = ''

        class ArrivalOrder:
            
            """
            ArrivalOrder(着順)
            """ 

            raceCancel = 96
            """ レース発走中止 """
            raceCancelJp = ''
            """ レース発走中止(日本語) """
            
            exclusion = 97
            """ 除外 """
            exclusionJp = '除'
            """ 除外(日本語) """

            disqualification = 98
            """ 失格 """
            disqualificationJp = '失'
            """ 失格(日本語) """

            stop_competition = 99
            """ 競争中止 """
            stop_competitionJp = '中'
            """ 競争中止(日本語) """
            
        class InCommingFlg:
            
            """
            InCommingFlg(入線フラグ)
            """ 
            
            defaultInLine = 0
            """ 通常入線 """

            accretion = 1
            """ 降着 """
            accretionJp = '降'
            """ 降着(日本語名) """

            exclusion = 2
            """ 除外 """

            disqualification = 3
            """ 失格 """

            stop_competition = 4
            """ 競争中止 """

            cancel_race = 5
            """ レース発走中止 """

        class Grade:
            
            """
            Grade(グレード)
            """ 

            defaultGrade = 0
            """ 平場 """

            g1Grade = 1
            """ G1 """

            g2Grade = 2
            """ G1 """

            g3Grade = 3
            """ G3 """
        
        class Direction:
        
            Steeplechase = '障'
            """ 障害 """
            
            left = '左'
            """ 左回り """
            
            right = '右'
            """ 右回り """
        
        class GroundKbn:
            
            Turf = 0
            """ 芝 """
            
            Dirt = 1
            """ ダート """

            Steeplechase_Turf = 2
            """ 障害(芝) """
        
            Steeplechase_TurfAndDirt = 3
            """ 障害(芝+ダート) """

            Steeplechase_Dirt = 4
            """ 障害(ダート) """

            TurfAbbr = '芝'
            """ 芝(略称) """
            
            DirtAbbr = 'ダ'
            """ ダート(略称) """
            
            SteeplechaseAbbr = '障'
            """ 障害(略称) """
        
        class PayInfoClass:
            
            win = 'tan'
            """ 単勝 """
            
            dwin = 'fuku'
            """ 複勝 """

            fcwin = 'waku'
            """ 枠連 """

            hcwin = 'uren'
            """ 馬連 """

            wdwin = 'wide'
            """ ワイド """

            hswin = 'utan'
            """ 馬単 """

            tdwin = 'sanfuku'
            """ 三連複 """

            tswin = 'santan'
            """ 三連単 """
            
    def __init__(self):
        
        """
        コンストラクタ
        """
        
        # 基底側コンストラクタ
        super().__init__()

        self.netkeibaUrl = 'https://db.netkeiba.com/'
        """ netkeibaURL """

        self.netkeibaUrl_race = 'https://race.netkeiba.com/'
        """ netkeibaURL(race) """
        
        self.netkeibaUrlSearchKeyword = self.settingValueStruct.SearchKeyword()
        """ netkeiba URL Search Keyword """

        self.netkeibaUrlSearchKeyword.race = 'race/'
        """ netkeiba URL Search Keyword - race """

        self.netkeibaUrlSearchKeyword.horse = 'horse/'
        """ netkeiba URL Search Keyword - horse """

        self.netkeibaUrlSearchKeyword.jockey = 'jockey/'
        """ netkeiba URL Search Keyword - jockey """

        self.netkeibaUrlSearchKeyword.trainer = 'trainer/'
        """ netkeiba URL Search Keyword - trainer """

        self.netkeibaUrlSearchKeyword.howner = 'howner/'
        """ netkeiba URL Search Keyword - howner """

        self.netkeibaUrlSearchKeyword.open = 'race/sum/'
        """ netkeiba URL Search Keyword - open """

        self.netkeibaUrlSearchKeyword.refund = 'race/pay/'
        """ netkeiba URL Search Keyword - pay """
        
        self.courseList:dict = {'札幌': '01',
                                '函館': '02',
                                '福島': '03',
                                '新潟': '04',
                                '東京': '05',
                                '中山': '06',
                                '中京': '07',
                                '京都': '08',
                                '阪神': '09',
                                '小倉': '10'}
        """ 競馬場リスト """
        
    def getConfigFileName(self):
        
        """ 
        設定ファイル名 
        """

        return 'netkeiber.ini'
    
    def setInstanceMemberValues(self):
        
        """ 
        インスタンス変数に読み取った設定値をセットする
        """
        
        # 基底側実行
        super().setInstanceMemberValues()
        
        # netkeibaURL
        super().setConfigValue('netkeibaUrl',self.config_ini,'SITE','NETKEIBA_URL',str)

        # netkeibaURL(race)
        super().setConfigValue('netkeibaUrl_race',self.config_ini,'SITE','NETKEIBA_URL_RACE',str)

        # netkeibaURL Search Keyword - race
        super().setConfigValue('netkeibaUrlSearchKeyword.race',self.config_ini,'SEARCH_KEYWORD','RACE',str)

        # netkeibaURL Search Keyword - horse
        super().setConfigValue('netkeibaUrlSearchKeyword.horse',self.config_ini,'SEARCH_KEYWORD','HORSE',str)

        # netkeibaURL Search Keyword - jockey
        super().setConfigValue('netkeibaUrlSearchKeyword.jockey',self.config_ini,'SEARCH_KEYWORD','JOCKEY',str)

        # netkeibaURL Search Keyword - trainer
        super().setConfigValue('netkeibaUrlSearchKeyword.trainer',self.config_ini,'SEARCH_KEYWORD','TRAINER',str)

        # netkeibaURL Search Keyword - howner
        super().setConfigValue('netkeibaUrlSearchKeyword.howner',self.config_ini,'SEARCH_KEYWORD','HOWNER',str)

        # netkeibaURL Search Keyword - open
        super().setConfigValue('netkeibaUrlSearchKeyword.open',self.config_ini,'SEARCH_KEYWORD','OPEN',str)

        # netkeibaURL Search Keyword - refund
        super().setConfigValue('netkeibaUrlSearchKeyword.refund',self.config_ini,'SEARCH_KEYWORD','REFUND',str)

        # netkeibaURL Search Keyword - race_id_cal
        super().setConfigValue('netkeibaUrlSearchKeyword.race_id_cal',self.config_ini,'SEARCH_KEYWORD','RACE_ID_CAL',str)

        # netkeibaURL Search Keyword - race_id_kaisai_date
        super().setConfigValue('netkeibaUrlSearchKeyword.race_id_kaisai_date',self.config_ini,'SEARCH_KEYWORD','RACE_ID_KAISAI_DATE',str)
