#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-
'''
@File    :   m3u8.py
@Time    :   2020/04/23 10:12:13
@Author  :   Tang Jing
@Version :   1.0.0
@Contact :   yeihizhi@163.com
@License :   (C)Copyright 2020
@Desc    :   None
'''

# here put the import lib
import re
import os
import io
import shutil
import time
# from Crypto.Cipher import AES 解密后CKPLAYER播放有问题.
from threading import Thread
from threading import Lock
from threading import Event as ThreadEvent
from urllib.parse import urlparse
from io import StringIO, BytesIO
from TDhelper.Cache.pools import pools
from TDhelper.network.http.http_helper import m_http
from TDhelper.network.http.status.M3U8_STATUS import M3U8_STATUS
# code start
m3u8Cfg = {
    "cfg": {
        'timeout': 5,
        'reconnect': 5
    },
    "ismerge": False,  # 是否合并ts文件
    "tmpfolder": "tmp\\ts",  # 临时文件件
    "download-poolsize": 20,  # 下载线程
    "buffer-index": 5  # 下载多少文件后生成索引文件
}


class m3u8: # DEMO
    def __init__(self, setting=None):
        '''
        params:
            setting: meu8Cfg(dict)
        '''
        if not setting:
            setting = m3u8Cfg
        try:
            self._http = m_http()
            self._state= True # 状态
            # requests 连接失败重连次数
            self._reconnect = setting['cfg']['reconnect']
            # requests超时时间
            self._timeout = setting['cfg']['timeout']
            # 临时文件夹
            self._tmp_folder = setting['tmpfolder']
            self._m3u8_file_hash = None
            self._create_m3u8_index_file = False  # 是否已经建立M3U8播放索引
            # 密钥
            self._m3u8_key = None
            # 下载文件线程池配置
            self._lock__ = Lock()  # 线程锁
            self._event__ = ThreadEvent()  # 线程事件
            self._download_event__ = ThreadEvent()  # 下载线程同步
            self._complete_event__ = ThreadEvent() # 下载完成通知事件
            self._event_create_m3u8_file__ = ThreadEvent()  # 生成m3u8索引文件事件
            self._is_merge__ = setting['ismerge']  # 是否合并TS文件
            self._download_thread_active_ = 0  # 下载线程活跃数,用于判断文件是否下载完成.
            self._downlaod_buffer_length = 0  # 下载缓存长度, 用于计算快偏移量
            self._download_pool_size = setting['download-poolsize']
            self._download_pool = pools(
                self._download_pool_size)
            for i in range(0, self._download_pool_size):
                self._download_pool.push(m_http())

            # 检查临时文件夹路径是否完整
            if not re.search(r':\\', self._tmp_folder, re.I | re.M):
                self._tmp_folder = os.path.join(os.getcwd(), self._tmp_folder)

            self._stream = None  # 最终文件句柄
            self._ts_tmp_stream = None  # TS缓存文件句柄

            # 下载缓存索引，下载索引到达这个值时才生成播放索引文件
            self._m3u8_buffer_index = setting['buffer-index']
            self._current_m3u8_file = None
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

        except Exception as e:
            raise e

    def get(self, m3u8_path, download_start_offset=0):
        '''
        开始下载
        '''
        self._state=True
        self._EXT_X_M3U8_PLAY_LIST_INDEX__ = download_start_offset
        self._m3u8_file_hash = None
        self._create_m3u8_index_file = False
        self._download_event__.clear()
        self._complete_event__.clear()
        self._event__.clear()
        # 判断下载文件夹是否存在
        if not os.path.exists(self._tmp_folder):
            os.mkdir(self._tmp_folder)
        else:
            # 清空目录
            if download_start_offset == 0:
                shutil.rmtree(self._tmp_folder)
                self._createTmpFolder(self._tmp_folder)
        if self._is_merge__:
            # 建立TS临时文件
            self._ts_tmp_stream = open(os.path.join(
                self._tmp_folder, 'tmp.ts'), mode="wb") if self._is_merge__ else None
            # 建立播放临时文件
            self._stream = self.__tmp_stream__() if self._is_merge__ else None

        if m3u8_path:
            self._EXTINF__ = []
            self._EXT_X_STREAM_INF__ = None
            ret, status = self.__download_m3u8_files(m3u8_path)
            if status == M3U8_STATUS.GET_M3U8_PLAYLIST:
                ret, status = self.__download_m3u8_files(ret)
            elif status== M3U8_STATUS.SUCCESS:
                self._event_create_m3u8_file__.set()
                self._complete_event__.set()
            else:
                self._event_create_m3u8_file__.set()
                self._complete_event__.set()
                self._state=False
            return ret, status
        else:
            return "url为空, 请设置m3u8地址.", M3U8_STATUS.ERROR

    def _createTmpFolder(self, folder):
        '''
        建立临时文件夹，解决某些时候拒绝访问错误问题
        '''
        try:
            os.mkdir(folder)
        except Exception as e:
            self._createTmpFolder(folder)

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

    def getM3U8PlayIndex(self):
        '''
        获取m3u8索引文件
        '''
        self._event_create_m3u8_file__.wait()
        return 'index.m3u8'  # 返回索引文件文件夹以及地址.

    def onComplete(self, func, *args, **wargs):
        '''
           完成调用. 
        '''
        self._complete_event__.wait()
        args= (self._state,)
        func(*args,**wargs)
        self._complete_event__.clear()

    def __download_m3u8_files(self, m3u8_path):
        '''
        下载m3u8文件
        '''
        self._prefix_url = m3u8_path.rsplit('/', 1)[0]
        self._current_m3u8_file = m3u8_path
        while True:
            self._download_event__.clear()
            m_index = 0
            self._create_m3u8_index_file = False
            self._EXTINF__ = []
            self._EXT_X_M3U8_PLAY_LIST__ = []
            self._EXT_X_M3U8_PLAY_LIST_INDEX__ = 0
            response, status = self.__request__(self._current_m3u8_file)
            # 完善重试机制.
            if status == 200:
                if response == self._m3u8_file_hash:
                    time.sleep(1)  # 如果M3U8索引没有改变则等待一秒再请求.
                    continue
                self._m3u8_file_hash = response
                self.__analysis__(response)
                if self._EXT_X_STREAM_INF__:
                    self._EXT_X_STREAM_INF__ = None  # 重置STREAM_INF属性
                    # 下载正式M3U8.
                    for m3_file in self._EXT_X_M3U8_FILE_LIST__:
                        if not re.match(r"^(http|https)://", m3_file, re.I | re.M):
                            # 拼接m3u8下载地址.
                            tmp_m3u8 = self._prefix_url
                            for item in m3_file.split('/'):
                                if not re.search(item,self._prefix_url,re.M|re.I):
                                    tmp_m3u8+='/'+item
                            m3_file= tmp_m3u8
                        return m3_file, M3U8_STATUS.GET_M3U8_PLAYLIST
                else:
                    if self._EXT_X_KEY__:
                        # 获取文件密钥
                        with StringIO(self._EXT_X_KEY__.replace(',', "\r\n")) as f:
                            self._m3u8_key = {
                                'method': None, 'key': '', 'iv': None}
                            while True:
                                line = f.readline()
                                if line:
                                    line = re.sub(
                                        '\"|\'|\\r|\\n', '', line, count=0, flags=0)
                                    line = line.split('=')
                                    if len(line) == 2:
                                        if line[0].lower() == 'method':
                                            self._m3u8_key['method'] = line[1]
                                        elif line[0].lower() == 'uri':
                                            key_url = ''
                                            if not re.match("http://|https://", line[1], re.I | re.M):
                                                key_url = self._prefix_url
                                                for item in line[1].split('/'):
                                                    if not re.search(item, key_url,re.M|re.I):
                                                        key_url+= '/'+ item
                                            else:
                                                key_url = line[1]
                                            state = False
                                            content = ''
                                            download_count=0
                                            while True:
                                                content, state = self.__request__(
                                                    key_url)
                                                download_count+=1
                                                if download_count> self._reconnect or state == 200:
                                                    break
                                            if state == 200:
                                                self._m3u8_key['key'] = content
                                                with open(os.path.join(self._tmp_folder, 'key.key'), mode='wb') as keyStream:
                                                    keyStream.write(
                                                        bytes(content, encoding='utf-8'))
                                                    keyStream.flush()
                                        elif line[0].lower() == 'iv':
                                            self._m3u8_key['iv'] = line[1]
                                else:
                                    break
                    # 下载TS文件.(还需要解决主播多M3U8文件下载文件辨别问题)
                    # self._EXT_X_M3U8_PLAY_LIST_INDEX__ = 0
                    # self._ts_tmp_stream = None
                    for item in self._EXTINF__:
                        m_file = item.split(',')[1]
                        duration = item.split(',')[0]
                        if not re.match(r"^(http|https)://", m_file, re.I | re.M):
                            download_uri = self._prefix_url
                            for item in m_file.split('/'):
                                if not re.search(item, download_uri, re.M|re.I):
                                    download_uri+= '/'+item
                        else:
                            download_uri = m_file
                        local_file_name = m_file.rsplit('/', 1)
                        if len(local_file_name) == 1:
                            local_file_name = local_file_name[0]
                        else:
                            local_file_name = local_file_name[1]
                        m_download_struct = {
                            'index': m_index, 'url': download_uri, 'offset': None, 'duration': duration, 'filename': local_file_name, 'state': False}
                        self._EXT_X_M3U8_PLAY_LIST__.append(m_download_struct)
                        m_index += 1
                    if self._EXTINF__:
                        self.__download__()
                    else:
                        print('EXTINF IS NONE.')
                    if not self._EXT_X_ENDLIST__:
                        continue
                return "success.", M3U8_STATUS.SUCCESS
            else:
                self._event_create_m3u8_file__.set()
                self._complete_event__.set()
                return "m3u8 download error.", M3U8_STATUS.ERROR

    def __request__(self, url):
        if self._http:
            try:
                response, status = self._http.getcontent(
                    url, p_timeout=self._timeout)
                if status == 200:
                    return response, status
                elif status == 'ERROR':
                    return response, status
                else:
                    for i in range(0, self._reconnect):
                        response, status = self._http.getcontent(
                            url, p_timeout=self._timeout)
                        if status == 200:
                            return response, status
                    if i+1 >= self._reconnect:
                        return 'timeout', 408
            except Exception as e:
                return e, -1
        else:
            self._complete_event__.set()
            self._download_event__.set()
            return 'http is none.', -1

    def __download__(self):
        '''
        启动TS文件下结线程，文件合并线程
        '''
        for i in range(0, self._download_pool_size):
            Thread(target=self.__download_thread__).start()
        if self._is_merge__:
            Thread(target=self.__create_merge_file).start()
        self._download_event__.wait()

    def __download_thread__(self):
        '''
        TS文件下载
        '''
        self._lock__.acquire()
        if self._download_thread_active_ < self._download_pool_size:
            self._download_thread_active_ += 1
        thiread_id = self._download_thread_active_
        self._lock__.release()
        m_http_control = None
        m_http_control = self._download_pool.pop()
        m_index = 0
        if m_http_control:
            while True:
                ts_struct = None

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
                    if os.path.exists(os.path.join(self._tmp_folder, ts_struct['filename'])):
                        continue
                    '''print(
                        '{0}-download:{1}'.format(str(thiread_id), ts_struct['url']))'''
                    print('\rdownload:{2} ({0}/{1})'.format(self._EXT_X_M3U8_PLAY_LIST_INDEX__+1,len(self._EXT_X_M3U8_PLAY_LIST__),self._current_m3u8_file),end='')
                    file_bytes, status = m_http_control.download(
                        ts_struct['url'])
                    if status != 200:
                        i = 0
                        while True:
                            file_bytes, status = m_http_control.download(
                                ts_struct['url'])
                            i += 1
                            if status==200:#if i > self._reconnect or status == 200:
                                break
                    self._EXT_X_M3U8_PLAY_LIST__[m_index]['state'] = True
                    self._lock__.acquire()
                    ts_struct['offset'] = (
                        self._downlaod_buffer_length, len(file_bytes))
                    self._downlaod_buffer_length += len(file_bytes)
                    self._lock__.release()
                    self._EXT_X_M3U8_PLAY_LIST__[
                        ts_struct['index']] = ts_struct
                    # 用索引号替代原TS文件名称 ts_struct['url'].rsplit('/', 1)[1]
                    tmp_file_name = str(ts_struct['filename']).split('?')[0]
                    '''if self._m3u8_key:
                        # 解密视频文件(CKPlayer播放器解密后的TS不能连续下载)
                        cryptor = AES.new(bytes(self._m3u8_key['key'], encoding='utf-8'), AES.MODE_CBC, bytes(
                            self._m3u8_key['key'], encoding='utf-8'))
                        file_bytes = cryptor.decrypt(file_bytes)'''
                    if self._is_merge__:
                        self._ts_tmp_stream.write(file_bytes)
                        self._ts_tmp_stream.flush()
                    else:
                        with open(os.path.join(
                                self._tmp_folder, tmp_file_name), mode="wb") as tmp_stream:
                            tmp_stream.write(file_bytes)
                            tmp_stream.flush()
                            tmp_stream.close()

                        # 直播类，删除已经超时文件.
                        self._lock__.acquire()
                        if not self._EXT_X_ENDLIST__:
                            if len(self._LIVE_DOWNLOAD_FILE) < len(self._EXTINF__)*4:
                                self._LIVE_DOWNLOAD_FILE.append(tmp_file_name)
                            else:
                                count = 0
                                size = int((len(self._EXTINF__)*4)/2)
                                while True:
                                    if count < size:
                                        try:
                                            os.remove(os.path.join(
                                                self._tmp_folder, self._LIVE_DOWNLOAD_FILE[0]))
                                            del self._LIVE_DOWNLOAD_FILE[0]
                                        except Exception as e:
                                            pass
                                    else:
                                        break
                                    count += 1
                                self._LIVE_DOWNLOAD_FILE.append(tmp_file_name)
                        self._lock__.release()
                    self._event__.set()
                    if ts_struct['index'] == self._m3u8_buffer_index or not self._EXT_X_ENDLIST__:
                        # todo create playlist.m3u8 file.
                        if self._create_m3u8_index_file:
                            continue
                        with open(os.path.join(self._tmp_folder, 'index.m3u8'), mode='wb') as f:
                            f.writelines(
                                [bytes('#EXTM3U\n', encoding='utf-8')])
                            f.writelines(
                                [bytes('#EXT-X-ALLOW-CACHE:YES\n', encoding='utf-8')])
                            for item in self.__dict__:
                                if self.__dict__[item]:
                                    if re.match('_EXT_X_VERSION', item, re.I | re.M):
                                        if self._EXT_X_VERSION__:
                                            m_line = "#EXT-X-VERSION:"+self._EXT_X_VERSION__+"\n"
                                            f.writelines(
                                                [bytes(m_line, encoding='utf-8')])
                                    elif re.match('_EXT_X_KEY__', item, re.I | re.M):
                                        m_line = "#EXT-X-KEY:METHOD={0},URI=\"key.key\"\n".format(
                                            self._m3u8_key['method'])
                                        f.writelines(
                                            [bytes(m_line, encoding='utf-8')])
                                    elif re.match('_EXT_X_MEDIA_SEQUENCE', item, re.I | re.M):
                                        m_line = ''
                                        if self._EXT_X_MEDIA_SEQUENCE__:
                                            m_line = "#EXT-X-MEDIA-SEQUENCE:"+self._EXT_X_MEDIA_SEQUENCE__+"\n"
                                        else:
                                            m_line = "#EXT-X-MEDIA-SEQUENCE:0\n"
                                        f.writelines(
                                            [bytes(m_line, encoding='utf-8')])
                                    elif re.match('_EXT_X_ALLOW_CACHE', item, re.I | re.M):
                                        pass
                                    elif re.match('_EXT_X_TARGETDURATION', item, re.I | re.M):
                                        if self._EXT_X_TARGETDURATION__:
                                            m_line = '#EXT-X-TARGETDURATION:'+self._EXT_X_TARGETDURATION__+"\n"
                                            f.writelines(
                                                [bytes(m_line, encoding='utf-8')])
                                    elif re.match('_EXT_X_M3U8_PLAY_LIST__', item, re.I | re.M):
                                        for extinf in self._EXT_X_M3U8_PLAY_LIST__:
                                            m_line = '#EXTINF:' + \
                                                extinf['duration']+',\n' + \
                                                str(extinf['filename'].split(
                                                    '?')[0])+"\n"
                                            f.writelines(
                                                [bytes(m_line, encoding='utf-8')])
                            if self._EXT_X_ENDLIST__:
                                m_line = '#EXT-X-ENDLIST\n'
                                f.writelines([bytes(m_line, encoding='utf-8')])
                            f.flush()
                            f.close()
                        self._create_m3u8_index_file = True
                        # 同步M3U8索引文件生成成功事件.
                        self._event_create_m3u8_file__.set()
            self._lock__.acquire()
            self._download_thread_active_ -= 1
            event_state = False
            if self._download_thread_active_ == 0:
                event_state = True
            if (not self._EXT_X_ENDLIST__) and event_state:
                self._download_event__.set()
            if self._EXT_X_ENDLIST__ and event_state:
                self._download_event__.set()
                self._complete_event__.set()
            self._lock__.release()
        else:
            print('httpContent none')

    def __create_merge_file(self):
        '''
        合并文件线程
        '''
        i = 0
        with open(os.path.join(
                self._tmp_folder, 'tmp.ts'), mode="rb") as fd:
            while True:
                if i >= len(self._EXT_X_M3U8_PLAY_LIST__):
                    break
                if self._EXT_X_M3U8_PLAY_LIST__[i]['offset']:
                    fd.seek(self._EXT_X_M3U8_PLAY_LIST__[i]['offset'][0])
                    self._stream.write(
                        fd.read(self._EXT_X_M3U8_PLAY_LIST__[i]['offset'][1]))
                    self._stream.flush()
                    i += 1
                else:
                    self._event__.clear()
                    self._event__.wait()
            fd.close()
        self._stream.close()
        self._ts_tmp_stream.close()

    def __tmp_stream__(self, file_name='tmp.mp4'):
        # 缓存文件对象
        try:
            if not os.path.exists(self._tmp_folder):
                os.mkdir(self._tmp_folder)
            # 仅是改了扩展名，可以让播放器识别.并没有将视频编码更改为MP4
            return open(os.path.join(self._tmp_folder, file_name), mode="wb")
        except:
            raise Exception("缓存文件初始化.")

    def __analysis__(self, content):
        # 分析M3U8文件
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
            if re.search(r"\.m3u8", content):
                self._EXT_X_M3U8_FILE_LIST__.append(content)

    def __match__(self, regex, content):
        m_result = re.match(regex, content, re.I | re.M)
        if m_result:
            return True
        return False
