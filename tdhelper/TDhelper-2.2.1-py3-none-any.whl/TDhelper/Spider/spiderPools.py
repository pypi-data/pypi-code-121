import datetime
from enum import Enum
from TDhelper.Event.Event import Event
from TDhelper.Spider.regex import Analysis
from TDhelper.Spider.models.spider_event import event as Analysis_Event
from TDhelper.Spider.models.status import STATUS as SPIDER_STATUS
from TDhelper.Spider.models.fingerprint import fingerprint
from TDhelper.Cache.pools import pools
from TDhelper.Spider.models.Cache_L1 import L1, event as L1_EVENT, L2
from TDhelper.Spider.models.BadRequestModel import BadRequest
from threading import Thread

import copy


class event(Enum):
    onListen = 'onlisten'


class spiderPools(pools):
    def __init__(self, rulesConfig, pool_length=10, cache_size=50, fingerprint=True):
        super(spiderPools, self).__init__(pool_length)
        self._fingerprint = fingerprint  # 重复检查开关
        self._rulesConfig= rulesConfig
        self._cache = L1(cache_size)
        self._exclude_url = {}
        self._cache.registerEvent(L1_EVENT.onPush, self.onPush)
        self._debug = False
        self._thread_state= False
        # 初始化爬虫线程池
        for i in range(0, pool_length):
            m_spider = Analysis(rulesConfig)
            m_spider.registerEvent(
                Analysis_Event.onIndexComplete, self.onIndexComplete)
            m_spider.registerEvent(
                Analysis_Event.onListComplete, self.onListComplete)
            m_spider.registerEvent(Analysis_Event.onDebug, self.onDebug)
            m_spider.registerEvent(
                Analysis_Event.onDetailComplete, self.onDetailComplete)
            m_spider.registerEvent(Analysis_Event.onError, self.onError)
            m_spider.registerEvent(
                Analysis_Event.onFingerprintComplete, self.onFingerprintComplete)
            self.push(m_spider)

    def serach(self,key=None):
        if key:
            m_search = Analysis(self._rulesConfig)
            m_search.registerEvent(
                Analysis_Event.onIndexComplete, self.onIndexComplete)
            m_search.registerEvent(
                Analysis_Event.onListComplete, self.onListComplete)
            m_search.registerEvent(Analysis_Event.onDebug, self.onDebug)
            m_search.registerEvent(
                Analysis_Event.onDetailComplete, self.onDetailComplete)
            m_search.registerEvent(Analysis_Event.onError, self.onError)
            m_search.registerEvent(
                Analysis_Event.onFingerprintComplete, self.onFingerprintComplete)
            m_search.search([key])

    def pushCache(self, value):
        self._cache.push(value[0], value[2], value[1])

    @property
    def State(self):
        return self._thread_state
    @property
    def ExcludeUrl(self):
        return self._exclude_url

    @ExcludeUrl.setter
    def ExcludeUrl(self,value):
        self._exclude_url= value

    def getCache(self):
        return self._cache.getCache()

    def onPush(self, *args, **kwargs):
        self._lock.acquire()
        if self.available_resources > 0:
            self._thread_state= True
            self.__startSpiderThread()
        self._lock.release()

    def __startSpiderThread(self):
        thread_spider = Thread(target=self.__process)
        thread_spider.start()

    def listen(self, *args, **kwargs):
        '''向外部抛出监听事件'''
        return self.on(event.onListen, *args, **kwargs)

    def __process(self):
        # 爬虫线程
        process_spider = self.pop()
        if process_spider:
            m_state = True
            while m_state:
                m_url = self._cache.pop()
                if m_url:
                    if m_url[0]:
                        # 如果内容未更改则跳过；并认为后续翻页内容均为未更改内容,并同时跳过后续翻页爬取.
                        if m_url[1]:
                            if m_url[1] in self._exclude_url:
                                continue
                        try:
                            self._debug= False
                            process_spider.start(m_url[2], m_url[0])
                        except Exception as e:
                            pass
                        if process_spider.getStatus == SPIDER_STATUS.SPIDER_FINGERPRINT_IS_REPEAT:
                            if m_url[1]:
                                self._exclude_url[m_url[1]
                                                ] = process_spider.getCurrentUrl
                    else:
                        m_state = False
                else:
                    self._thread_state= False
                    m_state = False
            self.push(process_spider)
        else:
            pass

    # 事件监听
    def onIndexComplete(self, *args, **kwargs):
        if len(args) > 0:
            m_analysis = args[0]
            if m_analysis.getStatus == SPIDER_STATUS.SPIDER_SUCCESS:
                data = m_analysis.getData
                if data:
                    for item in data['data']:
                        self.pushCache(
                            [item['url'], m_analysis.getNextUrl, data['analysis_key']])
                    try:
                        if not self._debug:
                            self._lock.acquire()
                            self.on(event.onListen, *args, **kwargs)
                    except Exception as e:
                        pass
                    finally:
                        if not self._debug:
                            self._lock.release()

    def onListComplete(self, *args, **kwargs):
        if len(args) > 0:
            m_analysis = args[0]
            if m_analysis.getStatus == SPIDER_STATUS.SPIDER_SUCCESS:
                m_data = m_analysis.getData
                if m_data['data']:
                    # TODO
                    for item in m_data['data']:
                        # 为了解决自动判断页面抓取重复取消下一页，此处存的来源为下一页
                        self.pushCache(
                            [item['url'], m_analysis.getNextUrl, m_data['analysis_key']])
                    try:
                        if not self._debug:
                            self._lock.acquire()
                            self.on(event.onListen, *args, **kwargs)
                    except Exception as e:
                        pass
                    finally:
                        if not self._debug:
                            self._lock.release()

            if m_analysis.getNextUrl:
                self.pushCache(
                    [m_analysis.getNextUrl, m_analysis.getCurrentUrl, m_data['analysis_key']])

    def onDetailComplete(self, *args, **kwargs):
        if len(args) > 0:
            m_analysis = args[0]
            if m_analysis.getStatus == SPIDER_STATUS.SPIDER_SUCCESS:
                m_data = m_analysis.getData
                try:
                    if not self._debug:
                        self._lock.acquire()                    
                        self.on(event.onListen, *args, **kwargs)
                except Exception as e:
                    pass
                finally:
                    if not self._debug:
                        self._lock.release()

    def onDebug(self, *args, **kwargs):
        try:
            self._lock.acquire()
            self._debug = args[0].debug
            if kwargs['event'] == Analysis_Event.onFingerprintComplete:
                pass #调试模式不检查重复 self.onFingerprintComplete(*args, **kwargs)
            elif kwargs['event'] == Analysis_Event.onDetailComplete:
                self.onDetailComplete(*args, **kwargs)
            elif kwargs['event'] == Analysis_Event.onListComplete:
                self.onListComplete(*args, **kwargs)
            elif kwargs['event'] == Analysis_Event.onIndexComplete:
                self.onIndexComplete(*args, **kwargs)
            return self.on(event.onListen, *args, **kwargs)
        except Exception as e:
            pass
        finally:
            self._lock.release()

    def onError(self, *args, **kwargs):
        try:
            self._lock.acquire()
            if len(args)>0:
                if args[0].getStatus== SPIDER_STATUS.HTTP_GATEWAY_TIME_OUT or args[0].getStatus== SPIDER_STATUS.HTTP_REQUEST_TIME:
                    # 如果访问超时缓存地址.
                    m_badRequest= BadRequest()
                    m_badRequest.Url= args[0].getCurrentUrl
                    m_badRequest.Source= None
                    m_badRequest.Key= args[0].getData['analysis_key']
                    m_badRequest.UpdateTime= datetime.datetime.now()
                    m_badRequest.toSave()
            return self.on(event.onListen, *args, **kwargs)
        except Exception as e:
            pass
        finally:
            self._lock.release()

    def onFingerprintComplete(self, *args, **kwargs):
        m_status = False
        if len(args) > 0:
            m_analysis = args[0]
            page_fingerprint = m_analysis.getFingerprint
            result = fingerprint().findOne(
                query={'url': m_analysis.getCurrentUrl})
            if result:
                if page_fingerprint == result['fingerprint']:
                    # 删除爬虫库数据
                    if self._fingerprint:
                        repeat_url = result['url']
                        m_L2 = L2()
                        m_L2.remove(
                            {'$or': [{'url': repeat_url}, {'sources': repeat_url}]})
                        m_L2 = None
                        # self._exclude_url[m_analysis.getNextUrl] =repeat_url
                        m_status = True
                    else:
                        # 当设置为不检查重复时
                        m_status = False
                else:
                    m_fingerprint = fingerprint()
                    m_fingerprint.update(
                        {
                            'url': m_analysis.getCurrentUrl
                        },
                        {
                            'fingerprint': page_fingerprint,
                            'lastupdatetime': datetime.datetime.now()
                        }
                    )
                    m_status = False
            else:
                m_fingerprint = fingerprint()
                m_fingerprint.Fingerprint = page_fingerprint
                m_fingerprint.Url = m_analysis.getCurrentUrl
                m_fingerprint.LastUpdateTime = datetime.datetime.now()
                m_fingerprint.toSave()
                m_status = False
        try:
            if not self._debug:
                self._lock.acquire()        
                self.on(event.onListen, *args, **kwargs)
        except Exception as e:
            pass
        finally:
            if not self._debug:
                self._lock.release()
        return m_status
