#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-
'''
@File    :   m3u8b.py
@Time    :   2020/04/23 12:54:28
@Author  :   Tang Jing 
@Version :   1.0.0
@Contact :   yeihizhi@163.com
@License :   (C)Copyright 2020
@Desc    :   None
'''

# here put the import lib
import re
import os
import time
# from Crypto.Cipher import AES 解密后CKPLAYER播放有问题.
from decimal import *
from threading import Thread
from threading import Lock
from threading import Event as ThreadEvent
from urllib.parse import urlparse
from io import StringIO, BytesIO
from TDhelper.cache.pools import pools
from TDhelper.network.http.http_helper import m_http
from TDhelper.network.http.status.M3U8_STATUS import M3U8_STATUS

# code start
cfg = {
    "cfg": {
        'timeout': 5,  # 超时(秒)
        'reconnect': 5  # 连接重试次数
    },
    "save-folder": "tmp\\ts",  # 临时文件件
    "download-poolsize": 20,  # 下载线程
    "buffer-index": 5  # 下载多少文件后生成索引文件
}


class m3u8:
    def __init__(self, m3u8Cfg: dict = None):
        self.setting = m3u8Cfg if m3u8Cfg else cfg  # 如果不传配置参数，则使用默认参数.
        self._state = True  # 运行状态
        self._http = m_http()
        # requests 连接失败重连次数
        self._reconnect = self.setting['cfg']['reconnect']
        # requests超时时间
        self._timeout = self.setting['cfg']['timeout']
        # 文件保存文件夹
        self._save_folder = self.setting['save-folder']
        self._m3u8_file_hash = None
        self._create_m3u8_index_file = False  # 是否已经建立M3U8播放索引
        self._del_state = False  # 是否正在删除过期文件,LIVE模式需要使用.
        # 密钥
        self._m3u8_key = None
        # 下载文件线程池配置
        self._lock__ = Lock()  # 线程锁
        self._download_event__ = ThreadEvent()  # 下载线程同步
        self._complete_event__ = ThreadEvent()  # 下载完成通知事件
        self._event_create_m3u8_file__ = ThreadEvent()  # 生成m3u8索引文件事件
        self._download_complate_total__ = 0  # 统计下载完成数量
        self._download_thread_active_ = 0  # 下载线程活跃数,用于判断文件是否下载完成.
        self._downlaod_buffer_length = 0  # 下载缓存长度, 用于计算快偏移量
        self._download_pool_size = self.setting['download-poolsize']
        self._download_pool = pools(self._download_pool_size)

        # 初始化下载线程池
        for i in range(0, self._download_pool_size):
            self._download_pool.push(m_http())
        self._save_folder = self.__checkfolder__(self._save_folder)

        # 下载缓存索引，下载索引到达这个值时才生成播放索引文件
        self._ts_save_folder = None
        self._m3u8_buffer_index = self.setting['buffer-index']
        self._current_m3u8_file = None
        # live:直播(需要连续多次下载M3U8文件),whole:完整播放(点播不需要多次下载M3U8文件)
        self._play_mode__ = 'whole'
        # M3U8 TAGS
        self._prefix_url = None
        self._EXT_X_TARGETDURATION__ = None
        self._EXTINF__ = []
        self._EXT_X_VERSION__ = None
        self._EXT_X_BYTERANGE__ = None
        self._EXT_X_KEY__ = None
        self._EXT_X_MAP__ = None
        self._EXT_X_PROGRAM_DATE_TIME__ = None
        self._EXT_X_DATERANGE__ = None
        self._EXT_X_MEDIA_SEQUENCE__ = None
        self._EXT_X_DISCONTINUITY_SEQUENCE__ = None
        self._EXT_X_PLAYLIST_TYPE__ = None
        self._EXT_X_MEDIA__ = None
        self._EXT_X_STREAM_INF__ = None
        self._EXT_X_I_FRAME_STREAM_INF__ = None
        self._EXT_X_SESSION_DATA__ = None
        self._EXT_X_SESSION_KEY__ = None
        self._EXT_X_START__ = None
        self._EXT_X_DISCONTINUITY__ = None
        self._EXT_X_ENDLIST__ = None
        self._EXT_X_I_FRAMES_ONLY__ = None
        self._EXT_X_INDEPENDENT_SEGMENTS__ = None

        # 自己定义M3U8 处理属性
        self._EXT_X_M3U8_FILE_LIST__ = []  # 直播类有m3u8有多个m3u8文件地址
        self._EXT_X_M3U8_PLAY_LIST__ = []  # m3u8播放列表TS文件列表
        self._EXT_X_M3U8_PLAY_LIST_INDEX__ = 0  # 下载m3u8播放列表TS文件列表索引
        self._LIVE_DOWNLOAD_FILE = []  # 直播下载文件

    def __resetVar__(self):
        '''
            重置变量
        '''
        self._ts_save_folder = None
        self._EXT_X_KEY__ = None
        self._download_event__.clear()
        self._complete_event__.clear()
        self._event_create_m3u8_file__.clear()
        self._download_complate_total__ = 0
        self._create_m3u8_index_file = False
        self._EXT_X_M3U8_FILE_LIST__ = []
        self._EXT_X_M3U8_PLAY_LIST__ = []
        self._EXT_X_M3U8_PLAY_LIST_INDEX__ = 0
        self._EXTINF__ = []
        self._download_complate_total__ = 0
        self._download_thread_active_ = 0
        self._downlaod_buffer_length = 0
        self._del_state = False
        if self._play_mode__ == "whole":
            self._LIVE_DOWNLOAD_FILE = []
            self._m3u8_file_hash = None

    def Get(self, m3u8_url, ts_save_path: str = None, download_start_offset: int = 0):
        try:
            self._EXT_X_M3U8_PLAY_LIST_INDEX__ = download_start_offset
            m_count = 0
            while True:
                if not self._state:
                    self._event_create_m3u8_file__.set()
                    self._download_event__.set()
                    self._complete_event__.set()
                    break
                self.__resetVar__()
                if ts_save_path:
                    self._ts_save_folder = ts_save_path
                else:
                    return 'ts save folder is none.', M3U8_STATUS.ERROR
                ret, status = self.__getM3U8file__(m3u8_url)
                if status == M3U8_STATUS.WAIT:
                    time.sleep(1)
                elif status == M3U8_STATUS.SUCCESS:
                    if self._play_mode__ == 'live':
                        self._ts_save_folder = 'live'
                        if m_count == 0:
                            m_count += 1
                            if os.path.exists(os.path.join(self._save_folder, self._ts_save_folder)):
                                for item in os.listdir(os.path.join(self._save_folder, self._ts_save_folder)):
                                    os.remove(os.path.join(self._save_folder, *(self._ts_save_folder,item))) #直播类，删除已下载TS文件.
                    self.__get_key__()  # 下载KEY文件.模块内有判断是否需要下载.
                    ret, status = self.__download_ts__()
                    if self._play_mode__ == 'live':
                        continue
                    else:
                        if status == M3U8_STATUS.SUCCESS:
                            return 'SUCCESS', M3U8_STATUS.SUCCESS
                        return ret, status
                elif status == M3U8_STATUS.ERROR:
                    return ret, M3U8_STATUS.ERROR
                else:
                    return 'Unknow error.', M3U8_STATUS.ERROR
        finally:
            self._event_create_m3u8_file__.set()
            self._complete_event__.set()
            self._download_event__.set()

    def getComplate(self, func):
        self._complete_event__.wait()
        func((), {})
        self._complete_event__.clear()

    def GetM3U8File(self):
        '''
            获取生成的M3U8索引文件
        '''
        self._event_create_m3u8_file__.wait()  # 阻塞等待生成播放索引.
        self._event_create_m3u8_file__.clear()  # 重置状态.
        return os.path.join(self._save_folder, *(self._ts_save_folder, 'index.m3u8',)), M3U8_STATUS.SUCCESS

    def close(self):
        self._state = False
        self._event_create_m3u8_file__.set()
        self._complete_event__.set()
        self._download_event__.set()

    def seek(self, time):
        ''''
        寻道时间定位
        '''
        total_time = 0
        index = 0
        for item in self._EXT_X_M3U8_PLAY_LIST__:
            total_time += float(item['duration'])
            if total_time >= time:
                self._EXT_X_M3U8_PLAY_LIST_INDEX__ = index
                break
            index += 1

    def __checkfolder__(self, folder):
        # 检查临时文件夹路径是否完整
        self._lock__.acquire()
        try:
            if not re.search(r':\\', folder, re.I | re.M):
                folder = os.path.join(os.getcwd(), folder)
            # 如果文件夹不存在则建立文件夹
            if not os.path.exists(folder):
                os.mkdir(folder)
        except OSError as e:
            raise e
        self._lock__.release()
        return folder

    def __getM3U8file__(self, uri: str):
        '''
            下载m3u8文件
        '''
        self._prefix_url = uri.rsplit('/', 1)[0]  # 获取URI前缀
        self._current_m3u8_file = uri  # 当前下载M3U8 URI
        print('download:%s'% uri)
        response, status = self.__request__(uri)
        if status == 200:
            print('download:%s Ok'% uri)
            if response == self._m3u8_file_hash:
                return uri, M3U8_STATUS.WAIT  # m3u8文件没有变化.返回等待状态.
            self._m3u8_file_hash = response
            self.__analysis__(response)
            if self._EXT_X_STREAM_INF__:
                self._EXT_X_STREAM_INF__ = None  # 重置STREAM_INF属性
                # 下载下一层M3U8.
                return self.__getM3U8file__(self.__spell_uri__(
                    self._EXT_X_M3U8_FILE_LIST__[0]))
            else:
                if self._EXT_X_ENDLIST__:
                    self._play_mode__ = 'whole'
                    self._m3u8_buffer_index = self.setting['buffer-index']
                else:
                    self._play_mode__ = 'live'
                    self._m3u8_buffer_index = 1
                return uri, M3U8_STATUS.SUCCESS
        else:
            print('download:%s Error'% uri)
            self._complete_event__.set()
            self._event_create_m3u8_file__.set()
            return uri, M3U8_STATUS.ERROR

    def __download_ts__(self):
        if self._EXTINF__:
            # 生成ts文件下载列表.
            m_index = 0
            for item in self._EXTINF__:
                m_file = item.split(',')[1]
                duration = item.split(',')[0]
                if not re.match(r"^(http|https)://", m_file, re.I | re.M):
                    download_uri = self.__spell_uri__(m_file)
                else:
                    download_uri = m_file
                local_file_name = m_file.rsplit('/', 1)
                if len(local_file_name) == 1:
                    local_file_name = local_file_name[0]
                else:
                    local_file_name = local_file_name[1]
                m_download_struct = {'index': m_index, 'url': download_uri, 'offset': None,
                                     'duration': duration, 'filename': local_file_name, 'state': False}
                self._EXT_X_M3U8_PLAY_LIST__.append(m_download_struct)
                m_index += 1
            # 开始下载
            for i in range(0, self._download_pool_size):
                Thread(target=self.__get_ts_thread__).start()
            self._download_event__.wait()  # 阻塞，等待下载线程完成下载
            self._download_event__.clear()
            self._complete_event__.set()
            return 'SUCCESS', M3U8_STATUS.SUCCESS
        else:
            return 'EXTINF IS NONE.', -1

    def __get_ts_thread__(self):
        '''
        TS文件下载
        '''
        self._lock__.acquire()
        if self._download_thread_active_ < self._download_pool_size:
            self._download_thread_active_ += 1
        else:
            raise Exception('download thread error: thread active total count({0}) Over length ({1}).'.format(
                self._download_thread_active_, self._download_pool_size))
        # thiread_id = self._download_thread_active_
        self._lock__.release()
        m_http_control = None
        m_http_control = self._download_pool.pop()
        m_index = 0
        if m_http_control:
            while True:
                if not self._state:
                    # 调用close方法，退出下载线程
                    self._download_pool.push(m_http_control)
                    break
                ts_struct = None  # TS文件下载信息结构体
                # 从播放列表取TS文件地址
                if self._EXT_X_M3U8_PLAY_LIST_INDEX__ < len(self._EXT_X_M3U8_PLAY_LIST__):
                    ts_struct = self._EXT_X_M3U8_PLAY_LIST__[
                        self._EXT_X_M3U8_PLAY_LIST_INDEX__]
                    m_index = self._EXT_X_M3U8_PLAY_LIST_INDEX__
                    self._lock__.acquire()
                    self._EXT_X_M3U8_PLAY_LIST_INDEX__ += 1
                    self._lock__.release()
                else:
                    # 下载完毕跳出下载线程
                    self._download_pool.push(m_http_control)
                    break
                if ts_struct:
                    if ts_struct['state']:
                        continue
                    if os.path.exists(os.path.join(self._save_folder, *(self._ts_save_folder, ts_struct['filename']))):
                        continue
                    file_bytes, status = m_http_control.download(
                        ts_struct['url'])
                    if status != 200:
                        i = 0
                        while True:
                            file_bytes, status = m_http_control.download(
                                ts_struct['url'])
                            i += 1
                            if i > self._reconnect or status == 200:  # if status==200:
                                break
                    if status == 200:
                        total_download_rate=self._EXT_X_M3U8_PLAY_LIST_INDEX__/len(
                            self._EXT_X_M3U8_PLAY_LIST__)*100
                        if total_download_rate>100.00:
                            total_download_rate= 100.00
                        total_download_rate=Decimal(str(total_download_rate)).quantize(Decimal('0.00'))
                        print('\rdownload:{1}({0}%)'.format(total_download_rate, self._current_m3u8_file), end='')
                        # 建立播放索引.
                        if ts_struct['index'] >= self._m3u8_buffer_index:
                            self.__create_m3u8_play_file__()
                        self._lock__.acquire()
                        ts_struct['state']=True # 更改TS下载列表对应文件下载状态.#self._EXT_X_M3U8_PLAY_LIST__[m_index]['state'] = True
                        ts_struct['offset'] = (
                            self._downlaod_buffer_length, len(file_bytes))
                        self._downlaod_buffer_length += len(file_bytes)
                        self._EXT_X_M3U8_PLAY_LIST__[
                            ts_struct['index']] = ts_struct
                        self._lock__.release()
                        # 用索引号替代原TS文件名称 ts_struct['url'].rsplit('/', 1)[1]
                        tmp_file_name = str(
                            ts_struct['filename']).split('?')[0]
                        # 直播类过期TS文件删除，模块内判断是否是直播.
                        self.__del_live_ts__(tmp_file_name)
                        '''if self._m3u8_key:
                        # 解密视频文件(CKPlayer播放器解密后的TS不能连续下载)不知道原因
                        cryptor = AES.new(bytes(self._m3u8_key['key'], encoding='utf-8'), AES.MODE_CBC, bytes(
                            self._m3u8_key['key'], encoding='utf-8'))
                        file_bytes = cryptor.decrypt(file_bytes)'''
                        # 生成TS文件.
                        m_saveTsPath = os.path.join(
                            self._save_folder, self._ts_save_folder)
                        self.__checkfolder__(m_saveTsPath)
                        with open(os.path.join(m_saveTsPath, tmp_file_name), mode="wb") as tmp_stream:
                            tmp_stream.write(file_bytes)
                            tmp_stream.flush()
                            tmp_stream.close()

                else:
                    continue  # 下载信息为空则进入下个下载循环.
            # 下载完成退出逻辑.
            self._lock__.acquire()
            self._download_thread_active_ -= 1
            event_state = False
            if self._download_thread_active_ == 0:
                event_state = True
            if event_state:
                self._download_event__.set()
            self._lock__.release()
        else:
            raise Exception('httpContent is none.')

    def __del_live_ts__(self, ts_file_name):
        '''
            删除直播过期文件.
        '''
        self._lock__.acquire()
        if self._del_state:
            return None
        self._del_state = True
        if self._play_mode__ == 'live':
            if len(self._LIVE_DOWNLOAD_FILE) < len(self._EXTINF__)*4:
                self._LIVE_DOWNLOAD_FILE.append(ts_file_name)
            else:
                count = 0
                size = int((len(self._EXTINF__)*4)/2)
                while True:
                    if count < size:
                        try:
                            os.remove(os.path.join(
                                self._save_folder, *(self._ts_save_folder, self._LIVE_DOWNLOAD_FILE[0])))
                            del self._LIVE_DOWNLOAD_FILE[0]
                        except Exception as e:
                            raise e
                    else:
                        break
                    count += 1
                self._LIVE_DOWNLOAD_FILE.append(ts_file_name)
        self._del_state = False
        self._lock__.release()

    def __create_m3u8_play_file__(self):
        '''
            建立.m3u8播放索引文件
        '''
        if self._create_m3u8_index_file:
            return None
        tmp_saveTsPath = os.path.join(self._save_folder, self._ts_save_folder)
        self.__checkfolder__(tmp_saveTsPath)
        with open(os.path.join(tmp_saveTsPath, 'index.m3u8'), mode='wb') as f:
            f.writelines([bytes('#EXTM3U\n', encoding='utf-8')])
            f.writelines([bytes('#EXT-X-ALLOW-CACHE:YES\n', encoding='utf-8')])
            for item in self.__dict__:
                if self.__dict__[item]:
                    if re.match('_EXT_X_VERSION', item, re.I | re.M):
                        if self._EXT_X_VERSION__:
                            m_line = "#EXT-X-VERSION:"+self._EXT_X_VERSION__+"\n"
                            f.writelines([bytes(m_line, encoding='utf-8')])
                    elif re.match('_EXT_X_KEY__', item, re.I | re.M):
                        m_line = "#EXT-X-KEY:METHOD={0},URI=\"key.key\"\n".format(
                            self._m3u8_key['method'])
                        f.writelines([bytes(m_line, encoding='utf-8')])
                    elif re.match('_EXT_X_MEDIA_SEQUENCE', item, re.I | re.M):
                        m_line = ''
                        if self._EXT_X_MEDIA_SEQUENCE__:
                            m_line = "#EXT-X-MEDIA-SEQUENCE:"+self._EXT_X_MEDIA_SEQUENCE__+"\n"
                        else:
                            m_line = "#EXT-X-MEDIA-SEQUENCE:0\n"
                        f.writelines([bytes(m_line, encoding='utf-8')])
                    elif re.match('_EXT_X_ALLOW_CACHE', item, re.I | re.M):
                        pass
                    elif re.match('_EXT_X_TARGETDURATION', item, re.I | re.M):
                        if self._EXT_X_TARGETDURATION__:
                            m_line = '#EXT-X-TARGETDURATION:'+self._EXT_X_TARGETDURATION__+"\n"
                            f.writelines([bytes(m_line, encoding='utf-8')])
                    elif re.match('_EXT_X_M3U8_PLAY_LIST__', item, re.I | re.M):
                        for extinf in self._EXT_X_M3U8_PLAY_LIST__:
                            m_line = '#EXTINF:' + \
                                extinf['duration']+',\n' + \
                                str(extinf['filename'].split('?')[0])+"\n"
                            f.writelines([bytes(m_line, encoding='utf-8')])
                        if self._EXT_X_ENDLIST__:
                            m_line = '#EXT-X-ENDLIST\n'
                            f.writelines([bytes(m_line, encoding='utf-8')])
            f.flush()
            f.close()
        self._create_m3u8_index_file = True
        self._event_create_m3u8_file__.set()  # 解锁M3U8文件生成成功锁

    def __get_key__(self):
        '''
            获取密钥文件
        '''
        if self._EXT_X_KEY__:
            with StringIO(self._EXT_X_KEY__.replace(',', "\r\n")) as f:
                self._m3u8_key = {'method': None, 'key': '', 'iv': None}
                while True:
                    line = f.readline()
                    if line:
                        line = re.sub('\"|\'|\\r|\\n', '',
                                      line, count=0, flags=0)
                        line = line.split('=')
                        if len(line) == 2:
                            if line[0].lower() == 'method':
                                self._m3u8_key['method'] = line[1]
                            elif line[0].lower() == 'uri':
                                key_url = ''
                                if not re.match("http://|https://", line[1], re.I | re.M):
                                    key_url = self.__spell_uri__(line[1])
                                    state = False
                                    content = ''
                                    download_count = 0
                                    while True:
                                        content, state = self.__request__(
                                            key_url)
                                        download_count += 1
                                        if download_count > self._reconnect:
                                            break
                                        if state == 200:
                                            self._m3u8_key['key'] = content
                                            self.__checkfolder__(os.path.join(self._save_folder,self._ts_save_folder))
                                            with open(os.path.join(self._save_folder, *(self._ts_save_folder, 'key.key')), mode='wb') as keyStream:
                                                keyStream.write(
                                                    bytes(content, encoding='utf-8'))
                                                keyStream.flush()
                                            break
                            elif line[0].lower() == 'iv':
                                self._m3u8_key['iv'] = line[1]
                    else:
                        break
        else:
            return None

    def __spell_uri__(self, uri):
        '''
            拼接资源URI
        '''
        ret= ''
        if uri[0]=='/':
            if re.search(r'http:',self._prefix_url, re.M|re.I):
                m_offset= self._prefix_url.find('/',7)
                if m_offset>0:
                    ret= self._prefix_url[0:m_offset]
            elif re.search(r'https:',self._prefix_url, re.M|re.I):
                m_offset= self._prefix_url.find('/',8)
                if m_offset>0:
                    ret= self._prefix_url[0:m_offset]
            else:
                ret= self._prefix_url.rsplit('/',1)[0]
        else:
            ret = self._prefix_url
        for item in uri.split('/'):
            if not re.search(item, self._prefix_url, re.M | re.I):
                ret += '/'+item
        return ret

    def __analysis__(self, content):
        '''
            分析M3U8文件
        '''
        m_result = self.__match__(r"^#EXTM3U", content)
        if m_result:
            content = re.sub(r",(\r\n|\r|\n)", ",", content, count=0, flags=0)
            for line in StringIO(content):
                self.__m3u8_attr__(line)
        else:
            return '', M3U8_STATUS.TYPE_ERROR

    def __m3u8_attr__(self, content):
        '''
            设置M3U8 TAG值
        '''
        content = re.sub(r"^\r\n|\r|\n", "", content, count=0, flags=0)
        m_result = re.match(r"^#.*", content)
        if m_result:
            m_data = content.split(":", 1)
            m_key = None
            if len(m_data) == 2:
                m_key = m_data[0]
            else:
                m_key = content
            m_key += "__"
            m_key = re.sub(r"#|-", "_", m_key, count=0, flags=0)
            m_key = m_key.replace(" ", "")
            if len(m_data) == 2:
                if m_key == "_EXTINF__":
                    self._EXTINF__.append(m_data[1])
                else:
                    self.__setattr__(m_key, m_data[1])
            else:
                self.__setattr__(m_key, True)
        else:
            m_stream= StringIO(content)
            m_line= m_stream.readline()
            while m_line:
                if re.search(r'/|.m3u8', content):
                    self._EXT_X_M3U8_FILE_LIST__.append(m_line)
                m_line= m_stream.readline()
            m_stream= None

    def __match__(self, regex, content):
        '''
            验证字符串是否存在
        '''
        m_result = re.match(regex, content, re.I | re.M)
        if m_result:
            return True
        return False

    def __request__(self, url):
        '''
            requests
        '''
        if self._http:
            try:
                for i in range(0, self._reconnect+1):
                    response, status = self._http.getcontent(
                        url, p_timeout=self._timeout)
                    if status == 200:
                        return response, status
                if i+1 >= self._reconnect:
                    return 'timeout', 408
            except Exception as e:
                return e, -1
        else:
            return 'http is none.', -1
