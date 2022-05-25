"""
TFdata client package
www.topfintech.org

TFdata client package manages the communicaton between TFdata servers and user-side client application.
User acct and user_pw are required for communicating with the data server. Check www.topfintech.org for details
"""

__author__ = "Dr.EdwC  (ed@topfintech.org)"
__copyright__ = "Copyright (c) 2020-2021 ed@topfintech.org by the MIT license"
__license__ = "MIT"
__verson__ = '0.2.8'

from tfdata.menu_text.menu_text0 import menu_basic_cn
from tfdata.menu_text.att_list import get_1d_att,get_daily_pro_att,get_tick_att,get_hf5_att #dict key->note text for each att current supported 
from tfdata.utils.network_utils import tryrq  
from tfdata.utils.comm_utils import timenow,pro_ts,get_codetype
from cryptography.fernet import Fernet 
import pandas as pd
import requests

class TFclient():
    def __init__ (self,acct='',pw='',slient=False,offline_path=None):
        if acct=='' or pw =='':
            raise NameError ('需用户名密码,(acct,pw),搜索添加微信公众号TFquant,对话栏输入"入会"可申请免费账户')
        self.__version = __verson__ 
        self.__acct = acct
        self.__pw = pw #acct and pw are set by user at topfintel's user portal 
        self.__offline_path = offline_path #this is used to saved data-specified offline data
        self.__akey = 'qB3tKFsWxHjv-lK-fzHrixRQMxWR64UfeKdYYXuml3I=' #for communicating pw with TFdata servers
        self.__aens = Fernet(self.__akey.encode())
        self.__dkey = None #a common dkey for communicating with TF server, this will be filled after sucessful login to web server
        self.__ds_url = None
        self.__login_time = None
        self.__notebook=None #do not modidy the use of these variables of server may refuse to respond
        self.__menu = menu_basic_cn #user menu
        self.__att_menu = {'get_1d_att':get_1d_att,'get_daily_pro_att':get_daily_pro_att,'get_tick':get_tick_att,'get_hf5':get_hf5_att}

        self.report_usage=False #if True, program will print out data usage after successful request
        self.__current_usage=0 #store usage only in current instance
        if not slient:
            print (menu_basic_cn['intro'])
    
    def nb(self):
        return self.__notebook
    
    
    def __init_doc(self):
        """
        initilize document dictionary for users
        
        """
        self._doc = {}
        self._doc['get_1d']="获取列表数据，列表数据指用户指定的非时间序列集合，例如所有A股代码，今日IPO股票代码等。\
            函数要求输入单个数据特征，返回列表、字典或错误说明文本。\
                具体支持的数据特征可通过 self.menu['1d']查看。函数支持timeout可选参数，用于设定等待服务器返回数据最长时间。"
    @property
    def version(self):
        return self.__version
    
    @property
    def menu(self):
        return self.__menu
    
    @property
    def att_menu(self):
        return self.__att_menu

    @property
    def acct_info(self):
        return [self.__acct,self.__pw]
    
    @property
    def current_usage(self):
        return self.__current_usage
        
    @property
    def ens_info(self):
        return [self.__dkey,self.__ds_url]
    
    def _request_dkey(self,server_url=None):
        """
        This sends user acc and pw info to TFdata public server. 
        If acc info is valid, the public server will process user info and send back a data server's access info
        raw return data are stored in self.__notebook
        self.__dkey(server ens key) and self.__ds_url are filled with return info about the particular data server for the user
        
        Parameters
        ----------
        server_url : str, optional,default=None
            url for the public server, usually should be topfintel.com

        Returns
        -------
        None or error str message
        """
        if server_url is None:
            server_url = 'http://www.topfintech.org:80/clientupdate'
        re = tryrq(url = server_url,retry=1,timeout=30,wait=1,request_type='post',
                   data={'yyhh':self.__acct,'apw':self.__aens.encrypt(self.__pw.encode())})

        if isinstance(re,str):
            return f'服务器不接受用户{self.__acct}登录请求:{re}'
        else:
            if isinstance(re,requests.models.Response):
                try:
                    if re.status_code==200:
                        try:
                            redict = re.json()
                        except:
                            return f'服务器返回错误信息: {re.text}'
                        self.__notebook = redict
                        smes = redict['mes']
                        if 'version' in redict.keys() and redict['version'] != self.version: 
                            print (f'TFclient更新版本{redict["version"]}已经发布，请通过pip update TFclient升级，继续使用旧版本可能产生各种错误！')
                        self.__dkey = smes[:smes.index('%$!2a')]  #key for communicating with data server
                        if self.__dkey =='beta':
                            self.__dkey = self.__akey
                        self.__ds_url = smes[smes.index('http://'):]
                    else:
                        return f'服务器错误代码{re.status_code}'
                except Exception as e:
                    return f'连接数据服务器失败:{e}'
            else:
                return  f'连接数据服务器失败 bad request:{str(re)}'
        
        if self.__dkey is not None:
            #print (self.__dkey)
            self.__ens = Fernet(self.__dkey.encode())
            self.__ens_pw = self.__ens.encrypt(self.__pw.encode()).decode('utf-8')            
    
    def login(self):
        """
        send login request to public server
        
        Returns
        -------
        None or error str message
        """
        dre = self._request_dkey() #this connect to main web portal for a dataAPI server assignment 
        if dre is not None:
            return f'无法获取数据服务器信息:{dre}'
        else:
            re = tryrq(url = self.__ds_url+'/userlogin',retry=1,timeout=30,wait=1,request_type='post',data={'yyhh':self.__acct,'dpw':self.__ens_pw})
            self.temp=re
            if isinstance(re,str):
                return f'数据服务器不接受登录请求：{re}'
            else:
                if isinstance(re,requests.exceptions.ConnectionError):
                    return '数据服务器无响应'
                else:
                    if re.status_code==200:
                        if re.text[:2]=='欢迎':
                            print (re.text)
                            self.__login_time = timenow()
                        else:
                            return re.text
                    else:
                       return '数据服务器不接受登录'

    def islogin(self):
        """
        return local login state of the client, the server-side state may not be the same
        """
        if self.__dkey is not None and self.__login_time is not None:
            return True
        else:
            return False
    
    def get_menu(self,keyword=None,printout=True):
        """
        return user menu subtext assoicated with a keyword
        Parameters
        ----------
        keyword : optional,str
        a search keyword for the request text in user manual
        if the default value None is provided, return self.__menu
        
        printout: optional,bool,when True menu text is not returned but printed out
        
        Returns
        -------
        requested text or error str message
        
        """ 
        
        if keyword is None:
            return self.__menu
        rt = None
        if self.__dkey is None or self.__login_time is None:
            return '客户端未登录'
        else:
            if keyword in self.__menu.keys():
                rt = self.__menu[keyword]             
            elif keyword in self.__att_menu:
                rt = self.__att_menu[keyword]   
            else:
                def dse(di,kw,re={},st=''):
                    for k in di.keys():
                        if k == kw:
                            if st=='':
                                re[k] = di[k]
                            else:
                                re[st+'->'+k] = di[k]
                        else:
                            if isinstance(di[k],dict):
                                if st=='':
                                    re.update(dse(di[k],kw,re,k))
                                else:
                                    re.update(dse(di[k],kw,re,st+'->'+k))
                    return re
                cw = dse(self.att_menu,keyword)
                if len(cw)>0:
                    rt = cw
        if rt is None:
            return f'暂无关于{keyword}的用户手册说明'
        else:
            if printout:
                print (rt)
            else:
                return rt
    
    def _get_hf(self,code,hf_type,date,timeout=200):
        """
        provide intraday data

        Parameters
        ----------
        code : str
            valid postfix code 
        date: str
             only one request per date,user may need to make mutiple request for a series of dates
        sample_size, int
            when either start_date or end_date is None but not both, sample_size specify the length of the resulting time index
        timeout: int
            wait time for return from data API before timeout break             
        Returns
             a pd.DataFrame or error str
        """        
        if hf_type not in ['hf_tick','hf5','hf_min']:
            return '非法参数'
        if '.' not in code:
            return '请输入正确的带后缀代码'
        code_type = get_codetype(code)
        if code_type not in ['ETF_CN','stock_A','ETFO_CN','CB_CN']:
            return '暂不提供该类别代码日内数据'
        try:
            date = pro_ts(pd.Timestamp(date))
        except:
            return '日期格式不正确'
        
        if self.__ens_pw is not None:
            arg = {'yyhh':self.__acct,'dpw':self.__ens_pw,'rt':hf_type,'code':code,'date':date,'at':code_type}  
            re = tryrq(url = self.__ds_url+'/datarequest',retry=1,timeout=timeout,wait=1,request_type='post',json=arg)
            self.temp=re
            if isinstance(re,str):
                return f'服务器不接受数据请求:{re}'
            else:
                if re.status_code==200:
                    try:
                        js = re.json()
                        self.__current_usage += int(js['usage'])
                        if self.report_usage:
                            print (f"数据用量: {js['usage']}")
                    except:
                        return f'数据服务器返回错误信息:{re.text}'
                    try:
                        df = pd.read_json(js['data']).set_index('time')
                        df.index = pd.DatetimeIndex(df.index)
                        if hf_type=='hf5':
                            df['pre_close_I'] = df['pre_close_I'].fillna(method='ffill')
                    except Exception as e:
                        return f'无法读取数据服务器返回JSON表格:{e}'
                    return df
    
    def get_tick(self,code,date):
        """
        provide intraday tick(summary of trades in every 3 second) data
        check self._get_hf for detail
        
        """   
        return self._get_hf(code=code,date=date,hf_type='hf_tick')   
    
    
    def get_min(self,code,date):
        """
        provide intraday min_by_min data
        check self._get_hf for detail
        """           
        return self._get_hf(code=code,date=date,hf_type='hf_min')          
        
        
    def get_hf5(self,code,date):
        """
        provide intraday hf5, ie. level 1 quote data
        check self._get_hf for detail
        """   
        return self._get_hf(code=code,date=date,hf_type='hf5')           
    
    
    def get_1d(self,att,timeout=200,get_doc=False):
        """
        1d data are list or dictionary data without the the time index and columns

        Parameters
        ----------
        att : str,default is None
             name of the attribute data under request. Available att name may be found in self.menu
        timeout: int
             request timeout setting
        Returns
             request result dict
        """
            
        if att not in self.get_menu('get_1d_att',printout=False).keys():
            return f'目前不支持1D数据标签{att},请查阅用户手册'
        if self.__ens_pw is not None:
            arg = {'yyhh':self.__acct,'dpw':self.__ens_pw,'rt':'1d','att':att}
            re = tryrq(url = self.__ds_url+'/datarequest',retry=1,timeout=timeout,wait=1,request_type='post',json=arg)
            if isinstance(re,str):
                return f'服务器不接受数据请求:{re}'
            else:
                try:
                    js = re.json()
                except:
                    return f'无法读取返回数据: {re.text}'
                try:
                    df =js['data']
                except Exception as e:
                    return f'数据服务器返回JSON格式不正确: {e}'
                self.__current_usage+= int(js['usage'])
                if self.report_usage:
                    print (f"数据用量: {js['usage']}")        
                return df
    
    def get_daily_pro(self,code,att,start_date=None,end_date=None,sample_size=None,timeout=200):
        """
        Parameters
        ----------
        code : str
            valid postfix code, if a non-postfix code is provided the system may try to match 
        start_date : str, optional,default is None
            required format yyyy-mm-dd, if it is None, start_date will be auto-filled on server site, the particular value is case-specific
        end_date : str, optional,default is None
            required format yyyy-mm-dd, if it is None, end_date will be auto-filled on server site, the particular value is case-specific
        sample_size, int
            when either start_date or end_date is None but not both, sample_size specify the length of the resulting time index
        timeout: int
            wait time for return from data API before timeout break
        Returns
        -------
        pd.DataFrame of daily OHLC price,vol,amount assoicted with the input code
        or
        error string

        """   
        return self._get_tstable(code=code,att=att,start_date=start_date,end_date=end_date,sample_size=sample_size,timeout=timeout)
            
    def get_daily(self,code,start_date=None,end_date=None,sample_size=None,timeout=200,adj_price=None):
        """
        Parameters
        ----------
        code : str
            valid postfix code, if a non-postfix code is provided the system may try to match 
        start_date : str, optional,default is None
            required format yyyy-mm-dd, if it is None, start_date will be auto-filled on server site, the particular value is case-specific
        end_date : str, optional,default is None
            required format yyyy-mm-dd, if it is None, end_date will be auto-filled on server site, the particular value is case-specific
        sample_size, int
            when either start_date or end_date is None but not both, sample_size specify the length of the resulting time index
        timeout: int
            wait time for return from data API before timeout break
        adj_price: None or str
            specify the adjustment scheme for OHLC price, q - backward adjusted, h - forward adjusted, or point-adjusted if a date text is provided
        Returns
        -------
        pd.DataFrame of daily OHLC price,vol,amount assoicted with the input code
        or
        error string

        """   
        ct = get_codetype(code)
        if ct =='NA':
            return '代码格式不正确，请查阅"self.get_menu("code")'
        if ct in ['stock_A','ETF_CN','ETFO_CN','CB_CN','index_CN']:
            att_daily_list = ['open','high','low','close','pct_chg','vol','amount']
            if adj_price is not None and ct in ['stock_A','ETF_CN']:
                att_daily_list.append('pindex')
            df =  self._get_tstable(code=code,att=att_daily_list,\
                                    start_date=start_date,end_date=end_date,sample_size=sample_size,timeout=timeout)
        if isinstance(df,str):
            return df
        if ct in ['stock_A','ETF_CN'] and adj_price is not None:
            if code[0] in ['1','5'] and ('SH' in code or 'SZ' in code):
                rsize = 3
            else:
                rsize = 2
            if adj_price == 'q':
                for i in range(2,df.shape[0]+1):
                    df.loc[df.index[-i],['open','high','low','close']] = round(df.loc[df.index[-i+1],['open','high','low','close']]*(df.at[df.index[-i],'pindex']/df.at[df.index[-i+1],'pindex']),rsize)
            elif adj_price == 'h':
                for i in range(1,df.shape[0]):
                    df.loc[df.index[i],['open','high','low','close']] = round(df.loc[df.index[i-1],['open','high','low','close']]*(df.at[df.index[i],'pindex']/df.at[df.index[i-1],'pindex']),rsize)            
            else:
                try:
                    adate = pd.Timestamp(adj_price)
                except:
                    adate = None
                if adate is not None and adate in df.index:
                    loc = df.index.get_loc(adate)
                    for i in range(1,loc+1):
                        df.loc[df.index[loc-i],['open','high','low','close']] = round(df.loc[df.index[loc-i+1],['open','high','low','close']]*(df.at[df.index[loc-i],'pindex']/df.at[df.index[loc-i+1],'pindex']),rsize)             
                    for i in range(1,df.shape[0]-loc):
                        df.loc[df.index[loc+i],['open','high','low','close']] = round(df.loc[df.index[loc+i-1],['open','high','low','close']]*(df.at[df.index[loc+i],'pindex']/df.at[df.index[loc+i-1],'pindex']),rsize)
            df.drop('pindex',axis=1)
        return df
        
    def _get_tstable(self,code,att,start_date=None,end_date=None,sample_size=None,timeout=200):
        """
        Parameters
        ----------
        code : str
            valid postfix code, if a non-postfix code is provided the system may try to match 
        att : str or list of str att name 
            if a str of a attribute is provide - > return a time series or a list of str attribute -> return a time series dataframe
        start_date : str, optional,default is None
            required format yyyy-mm-dd, if it is None, start_date will be auto-filled on server site, the particular value is case-specific
        end_date : str, optional,default is None
            required format yyyy-mm-dd, if it is None, end_date will be auto-filled on server site, the particular value is case-specific
        sample_size, int
            when either start_date or end_date is None but not both, sample_size specify the length of the resulting time index
        timeout: int
            wait time for return from data API before timeout break
        Returns
        -------
        time series pd.Series or pd.DataFrame, or error str message

        """
        if isinstance(att,str):
            att = [att]
        if not isinstance(att,list):
            return 'att 参数输入错误,请查阅用户手册'
        if '.' not in code:
            return '证券代码不符合规范,请查阅self。menu["code"]'
        asset_type = get_codetype(code)
        if asset_type == 'NA':
            return f'无法识别代码{code},请查阅self。menu["code"]'
        if self.menu is None or self.__notebook is None:
            return '数据服务器目录信息缺失,请尝试重新登录'
            
        if start_date is not None:
            try:
                start_date = pro_ts(pd.Timestamp(start_date))
            except Exception as e:
                return f'起始日输入错误：{e}'

        if end_date is not None:
            try:
                end_date = pro_ts(pd.Timestamp(end_date))
            except Exception as e:
                return f'结束日输入错误：{e}'
            
        if sample_size is not None:
            if not isinstance(sample_size,int) or sample_size <0:
                return 'sample_size输入错误'
            else:
                if sample_size>7000:
                    sample_size=7000
        if pd.Timestamp(start_date)>pd.Timestamp(end_date):
            return '结束日早于起始日'
        
        if self.__ens_pw is not None:
            arg = {'code':code,'yyhh':self.__acct,'dpw':self.__ens_pw,'rt':'tstable','start_date':start_date,'end_date':end_date,'sample_size':sample_size}
            dff = list(set(att) - set(self.att_menu['get_daily_pro_att'][asset_type].keys()))
            if len(dff)>0:
                return f'无效的数据标签{dff},详见self.get_menu("get_daily_pro_att")'               
            arg['at'] = asset_type
            arg['att'] = att
            re = tryrq(url = self.__ds_url+'/datarequest',retry=1,timeout=timeout,wait=1,request_type='post',json=arg)
            self.temp=re
            if isinstance(re,str):
                return f'数据服务器不接受数据请求:{re}'
            else:
                try:
                    js = re.json()
                except Exception as e:
                    try:
                        return re.text
                    except:
                        return f'数据服务器不接受数据请求:{e}'
                try:
                    df = pd.read_json(js['data'])
                except:
                    return '数据服务器返回JSON格式不正确'
                if 'time' in df.columns:
                    df.set_index('time',drop=True,inplace=True)
                self.__current_usage+= int(js['usage'])
                if self.report_usage:
                    print (f"数据用量: {js['usage']}")        
                return df
        else:
            return '服务服务器登录信息缺失,请重新登录'
