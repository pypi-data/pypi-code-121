#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'chinese_chromedriver_installer.py'
__create_time__ = '2020/7/17 1:04'

from typing import Optional
from urllib.request import urlretrieve, urlopen
from urllib.error import URLError
try:
    # windows os
    from winreg import *
except ImportError as e:
    # *unix/mac and so on
    pass
from re import findall, IGNORECASE
from zipfile import ZipFile
from os import remove, path, popen, rename
import platform, sys, subprocess, ssl, tarfile, ctypes

ssl._create_default_https_context = ssl._create_unverified_context

download_filename = ''

def back(a,b,c):
    '''''回调函数
    @a:已经下载的数据块
    @b:数据块的大小
    @c:远程文件的大小
    '''
    per = 100.0*a*b/c
    if per > 100:
        per = 100
    print(end='\r')
    print(f'{download_filename}已下载%.2f%%' % per, end='')

def get_osname():
    ''' 判断当前系统 : windows/mac/ubuntu/centos '''
    if sys.platform == 'win32':
        ''' windows '''
        return 'windows'
    elif sys.platform == 'darwin':
        ''' Mac OS '''
        return 'mac'
    elif sys.platform == 'linux2':
        if 'ubuntu' in platform.platform().lower():
            ''' ubuntu '''
            return 'ubuntu'
        elif 'redhat' in platform.platform().lower():
            ''' redhat/centos '''
            return 'centos'
        else:
            return 'other'
    else:
        return 'other'

def is_admin():
    ''' 适用于windwos 判断当前是否为管理员 return True/False '''
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def unZip(filename: Optional[str] = None, newfilename: Optional[str] = None,
          newdirname: Optional[str] = None, dst_path: Optional[str] = '.', **kwargs):
    '''
    解压文件 支持：*.zip *.tar.gz
    :param filename:        待解压文件
    :param newfilename:    解压后的文件名（适应与单文件）
    :param newdirname:     解压后文件夹名(重命名文件夹)
    :param dst_path:    解压的目录
    :param kwargs       扩展参数
    :return:
    样例：
        unZip(filename='chromedriver.zip', dst_path='C:/Windows')
        unZip(filename='chromedriver.tar.gz', newfilename='chromedriver.exe')
    '''
    if dst_path not in [None, ''] and newfilename in [None, '']:
        if '.zip' == filename[-4:]:
            first_name = ZipFile(f"{path.abspath(path.curdir)}/{download_filename}").namelist()[0].replace('/', '')
            ZipFile(filename).extractall(path=dst_path)
        elif '.tar.gz' == filename[-7:]:
            first_name = tarfile.open(f"{path.abspath(path.curdir)}/{download_filename}").getnames()[0].replace('/', '')
            tarfile.open(filename).extractall(path=dst_path)
        else:
            first_name = tarfile.open(f"{path.abspath(path.curdir)}/{download_filename}").getnames()[0].replace('/', '')
            tarfile.open(filename).extractall(path=dst_path)
        if path.isdir(f'{path.abspath(dst_path)}/{first_name}'):
            rename(src=f'{path.abspath(dst_path)}/{first_name}', dst=f'{path.abspath(dst_path)}/{newdirname}')
    elif path in [None, ''] and newfilename not in [None, '']:
        if '.zip' == filename[-4:]:
            ZipFile(filename).extract(newfilename)
        elif '.tar.gz' == filename[-7:]:
            tarfile.open(filename).extract(newfilename)

def download(url: Optional[str] = None, **kwargs):
    '''
    下载文件
    :param url:          下载链接
    :param filename:     下载文件名
    :param newfilename:  解压后文件名
    :param newdirname:   解压后文件夹名
    :param dst_path:     (解压)/(移动)的目录
    :param unzip:        是否解压
    :param del_src:      是否删除下载文件
    :param kwargs:
    :return:
    样例：
        download(url='https://api.xiaobai.com/adb.zip', filename='adb.zip', dst_path='D:/adb', unzip=True, del_src=True)
    '''
    global download_filename
    if 'filename' in kwargs.keys():
        download_filename = kwargs.get('filename')
    else:
        download_filename = ''
    if url not in [None, '']:
        try:
            if 'unzip' not in kwargs.keys() and 'dst_path' in kwargs.keys():
                urlretrieve(url, kwargs.get('dst_path') + '/' + download_filename, back)
            else:
                urlretrieve(url, download_filename, back)
        except URLError as e:
            print('您的文件下载失败，请确认后重试！')
            exit(0)
        except ConnectionResetError as e:
            print('您的文件下载失败，网络连接重试失败！')
            exit(0)
        except KeyboardInterrupt as e:
            print('您已主动取消了下载！')
            exit(0)
        if 'unzip' in kwargs.keys() and kwargs.get('unzip'):
            if 'newfilename' in kwargs.keys():
                unZip(filename=download_filename, newfilename=kwargs.get('newfilename'))
            elif 'dst_path' in kwargs.keys() and 'newdirname' in kwargs.keys():
                unZip(filename=download_filename, newdirname=kwargs.get('newdirname'), dst_path=kwargs.get('dst_path'))
            else:
                unZip(filename=download_filename, dst_path=kwargs.get('dst_path'))
        if 'del_src' in kwargs.keys() and kwargs.get('del_src'):
            remove(download_filename)

def _shell(cmd: Optional[str] = '', isSubprocess: Optional[bool] = True, powershell: Optional[bool] = False):
    ''' subprocess '''
    name = get_osname()
    if isSubprocess:
        if powershell:
            if cmd == '' and name == 'windows' and powershell:
                args = ["powershell",
                        "Set-ExecutionPolicy RemoteSigned -scope CurrentUser",
                        "iex (new-object net.webclient).downloadstring('https://get.scoop.sh')",
                        "iwr -useb get.scoop.sh | iex"]
            else:
                args = ['powershell', cmd]
        else:
            cmd_list = cmd.split(' ')
            args = [cmd_list[0], ' '.join(cmd_list[1:])]
        try:
            sp = subprocess.Popen(args, stdout=subprocess.PIPE)
            return sp.stdout.read()
        except Exception as e:
            return False
    else:
        try:
            popen(cmd)
        except Exception as e:
            exit(0)

def setEnv(name: Optional[str] = None, value: Optional[str] = None,
           addPath: Optional[bool] = True, endPath: Optional[str] = '/bin'):
    '''
    添加(系统)环境变量
    :param name:        环境变量名
    :param value:       环境变量值
    :param addPath:     是否添加到PATH
    :param endPath:     追加的路径
    :return:
    样例：
        setEnv(JAVA_HOME, 'D:/JDK', True, '/bin')
        setEnv(JAVA_HOME, 'D:/JDK')
    '''
    if name is None or value is None: return None
    os = get_osname()
    if os == 'windows':
        value = value.replace('/', '\\')
        endPath = endPath.replace('/', '\\')
        if is_admin():
            env = '系统'
            read_env_key = OpenKey(HKEY_LOCAL_MACHINE, 'SYSTEM\ControlSet001\Control\Session Manager\Environment')
            write_env_key = OpenKey(HKEY_LOCAL_MACHINE, 'SYSTEM\ControlSet001\Control\Session Manager\Environment',
                              access=KEY_WRITE)
        else:
            env = '用户'
            read_env_key = OpenKey(HKEY_CURRENT_USER, 'Environment')
            write_env_key = OpenKey(HKEY_CURRENT_USER, 'Environment', access=KEY_WRITE)
        path_env = QueryValueEx(read_env_key, 'path')[0]
        # add key
        SetValueEx(write_env_key, name, 0, REG_SZ, value)
        if addPath:
            SetValueEx(write_env_key, 'path', 0, REG_EXPAND_SZ, f'%{name}%{endPath};{path_env}')
        # FlushKey(write_env_key)
        write_env_key.Close()
        print(f'\n{env}环境变量{name}已经设置完毕！')
    else:
        cmd = f'\nexport {name}={value}'
        if addPath:
            cmd += f'\nexport PATH=$PATH:${name}{endPath}'
        try:
            with open('/etc/profile', 'a') as f:
                f.write(cmd)
                f.flush()
                f.close()
            _shell('source /etc/profile')
            print(f'\n环境变量 {name} 已经设置完毕！')
        except PermissionError as e:
            print('\n未使用管理员权限')
            try:
                _shell('cd ~')
                if not path.isfile('.bash_profile'):
                    _shell('touch .bash_profile')
                with open('.bash_profile', 'a') as f:
                    f.write(cmd)
                    f.flush()
                    f.close()
                _shell('source /etc/profile')
                print(f'\n用户环境变量 {name} 已经设置完毕！')
            except Exception as e:
                print('\n环境变量设置失败！')

def getWebList(url: Optional[str] = None, match: Optional[str] = None, flags: Optional[int] = IGNORECASE):
    '''
    获取网页中指定规则的所有值，存储到列表中，默认
    :param url:     链接地址
    :param match:   匹配规则
    :param flags:   匹配模式 默认(IGNORECASE)忽略大小写
    :return:
    样例：
        getWebList('https://www.baidu.com', 'href="(.+?)"')
    '''
    if url is not None and match is not None:
        try:
            res = urlopen(url=url).read().decode('utf-8')
            return findall(match, res, flags)
        except URLError as e:
            print(e)
            exit(0)
    else:
        return []

def chromedriver_download(version: Optional[str] = '100', dest_dir: Optional[str] = '.'):
    '''
    自动下载chromedriver驱动文件
    :param version: 87,88等chrome浏览器版本号（整数）
    :return:
    '''
    TAOBAO_MIRROR_DOWNLOAD_URL = 'https://npm.taobao.org/mirrors/chromedriver/'
    name = get_osname()
    if name == 'windows':
        try:
            if version == '':
                chrome_current_version = EnumValue(OpenKey(HKEY_CURRENT_USER, 'Software\Google\Chrome\BLBeacon'), 0)[1]
                cur_version = chrome_current_version.split('.')[0]
            else:
                cur_version = version
            LAST_VERSION = getWebList(TAOBAO_MIRROR_DOWNLOAD_URL, f'/mirrors/chromedriver/{cur_version}([0-9\.]+)/">')[0]
            DOWNLOAD_URL = f'{TAOBAO_MIRROR_DOWNLOAD_URL}{cur_version}{LAST_VERSION}/chromedriver_win32.zip'
            download(DOWNLOAD_URL, filename='chromedriver_win32.zip', dst_path=dest_dir, unzip=True, del_src=True)
        except Exception as e:
            raise ('是不是没安装Chrome浏览器呢？' + str(e))
    elif name == 'mac':
        if version == '':
            cur_version = ''
        else:
            cur_version = version
        try:
            LAST_VERSION = getWebList(TAOBAO_MIRROR_DOWNLOAD_URL, f'/mirrors/chromedriver/{cur_version}([0-9\.]+)/">')[0]
            DOWNLOAD_URL = f'{TAOBAO_MIRROR_DOWNLOAD_URL}{LAST_VERSION}/chromedriver_linux64.zip'
            download(DOWNLOAD_URL, filename='chromedriver_linux64.zip', dst_path='/usr/local/bin', unzip=True, del_src=True)
        except Exception as e:
            pass
    else:
        if version == '':
            cur_version = ''
        else:
            cur_version = version
        try:
            LAST_VERSION = getWebList(TAOBAO_MIRROR_DOWNLOAD_URL, f'/mirrors/chromedriver/{cur_version}([0-9\.]+)/">')[0]
            DOWNLOAD_URL = f'{TAOBAO_MIRROR_DOWNLOAD_URL}{LAST_VERSION}/chromedriver_mac64.zip'
            download(DOWNLOAD_URL, filename='chromedriver_mac64.zip', dst_path='/usr/local/bin', unzip=True, del_src=True)
        except Exception as e:
            pass

def tesseract_download():
    TESSERACT_DOWNLOAD_URL = 'https://api.256file.com/download/56476_tesseract.exe'
    download(url=TESSERACT_DOWNLOAD_URL, filename='tesseract.exe', unzip=False)

def update_keyword_db():
    KEYWORD_DB_DOWNLOAD_URL = ''
    urlretrieve(KEYWORD_DB_DOWNLOAD_URL, 'xiaobaiauto2.db', back)
    # popen('xiaobaiauto2.db', )

def jdk_install(version: Optional[str] = 'latest', dest_dir: Optional[str] = '.'):
    '''
    下载并安装openjdk
    windows: scoop install oraclejdk{version}
    mac os: brew cask install adoptopenjdk{version}
    ubuntu: apt install openjdk-{version}-jre
    centos: yum install java-1.{version}.0-openjdk
    mirror: https://mirrors.tuna.tsinghua.edu.cn/AdoptOpenJDK/{version}/jdk/x64/{os}/
    '''
    latest = getWebList(url='https://mirrors.tuna.tsinghua.edu.cn/AdoptOpenJDK/', match='title="[0-9]+"')
    version = latest[0] if len(latest)>0 and version == 'latest' else version
    os = get_osname()
    if os == 'windows':
        url = f'https://mirrors.tuna.tsinghua.edu.cn/AdoptOpenJDK/{version}/jdk/x64/{os}/'
        filename = getWebList(url, match='href="OpenJDK(.+?).zip"', flags=0)
        if len(filename) > 0:
            url = f'{url}OpenJDK{filename[0]}.zip'
            download(url=url, filename=f'jdk{version}_{os}_64.zip', newdirname=f'jdk{version}_{os}_64', dst_path=dest_dir, unzip=True, del_src=True)
        setEnv('JAVA_HOME', f'{path.abspath(dest_dir)}/jdk{version}_{os}_64')
    elif os == 'mac':
        ''' Mac OS '''
        try:
            _shell(cmd='/bin/zsh -c "$(curl -fsSL https://gitee.com/cunkai/HomebrewCN/raw/master/Homebrew.sh)"')
        except Exception as e:
            pass
        url = f'https://mirrors.tuna.tsinghua.edu.cn/AdoptOpenJDK/{version}/jdk/x64/{os}/'
        filename = getWebList(url, match='href="OpenJDK(.+?).tar.gz"', flags=0)
        if len(filename) > 0:
            url = f'{url}OpenJDK{filename[0]}.tar.gz'
            download(url=url, filename=f'jdk{version}_{os}_64.tar.gz', newdirname=f'jdk{version}_{os}_64', dst_path=dest_dir, unzip=True, del_src=True)
        setEnv('JAVA_HOME', f'{path.abspath(dest_dir)}/jdk{version}_{os}_64/Contents/Home')
    else:
        url = f'https://mirrors.tuna.tsinghua.edu.cn/AdoptOpenJDK/{version}/jdk/x64/linux/'
        filename = getWebList(url, match='href="OpenJDK(.+?).tar.gz"', flags=0)
        if len(filename) > 0:
            url = f'{url}OpenJDK{filename[0]}.tar.gz'
            download(url=url, filename=f'jdk{version}_{os}_64.tar.gz', newdirname=f'jdk{version}_{os}_64', dst_path=dest_dir, unzip=True, del_src=True)
        setEnv('JAVA_HOME', f'{path.abspath(dest_dir)}/jdk{version}_{os}_64/Contents/Home')

def maven_install(version: Optional[str] = 'latest', dest_dir: Optional[str] = '.'):
    '''
    下载并安装maven
    '''
    latest = getWebList(url='http://maven.apache.org/download.cgi', match='apache-maven-(.+?)-bin.zip')
    version = latest[0] if len(latest)>0 and version == 'latest' else version
    os = get_osname()
    url = f'https://mirrors.tuna.tsinghua.edu.cn/apache/maven/maven-{version.split(".")[0]}/{version}/binaries/apache-maven-{version}-bin.zip'
    download(url=url, filename=f'maven{version}_{os}_64.zip', newdirname=f'maven{version}_{os}_64', dst_path=dest_dir, unzip=True, del_src=True)
    setEnv('MAVEN_HOME', f'{path.abspath(dest_dir)}/maven{version}_{os}_64')

def jmeter_install(version: Optional[str] = 'latest', dest_dir: Optional[str] = '.'):
    ''' 下载并配置环境变量 '''
    src_list = [
        'https://mirror.bit.edu.cn/apache/jmeter/binaries/',
        'https://mirrors.bfsu.edu.cn/apache/jmeter/binaries/',
        'https://mirrors.tuna.tsinghua.edu.cn/apache/jmeter/binaries/'
    ]
    latest = getWebList(url='https://mirrors.tuna.tsinghua.edu.cn/apache/jmeter/binaries/HEADER.html', match='Apache JMeter (.+?) requires')
    version = latest[0] if len(latest) > 0 and version == 'latest' else version
    filename = f'apache-jmeter-{version}.zip'
    download(src_list[2] + filename, filename=filename, newdirname=f'apache-jmeter-{version}', dst_path=dest_dir, unzip=True, del_src=True)
    setEnv('JMETER_HOME', f'{path.abspath(dest_dir)}/apache-jmeter-{version}')
    # add plugin manager
    plugin_latest = getWebList(url='https://repo1.maven.org/maven2/kg/apc/jmeter-plugins-manager/maven-metadata.xml',
                               match='<latest>(.+?)</latest>')
    download(url=f'https://repo1.maven.org/maven2/kg/apc/jmeter-plugins-manager/{plugin_latest[0]}/jmeter-plugins-manager-{plugin_latest[0]}.jar',
             filename=f'jmeter-plugins-manager-{plugin_latest[0]}.jar',
             dst_path=f'{path.abspath(dest_dir)}/apache-jmeter-{version}/lib/ext')
    # set Chinese
    with open(path.abspath(dest_dir) + f'/apache-jmeter-{version}/bin/jmeter.properties', 'a', encoding='utf-8') as fw:
        fw.write('\r\n\r\nlanguage=zh_CN')
        fw.write('\r\nsampleresult.default.encoding=UTF-8')
        fw.flush()
        fw.close()
    # print('JMeter已设置中文，请求结果编码已设置为UTF-8')

def tomcat_install(version: Optional[str] = 'latest', dest_dir: Optional[str] = '.'):
    if 'latest' == version:
        latest0 = getWebList(url='https://mirrors.tuna.tsinghua.edu.cn/apache/tomcat/', match='tomcat-(\d+)/')
        V = str(max([int(i) for i in latest0]))
    elif '.' not in version:
        V = version
    else:
        V = version.split(".")[0]
    latest = getWebList(url=f'https://mirrors.tuna.tsinghua.edu.cn/apache/tomcat/tomcat-{V}/',
                        match=f'v([0-9a-zA-Z\-\.]+)/')
    version = latest[-1] if len(latest) > 0 and version.split(".")[0] == V else version
    url = f'https://mirrors.tuna.tsinghua.edu.cn/apache/tomcat/tomcat-{version.split(".")[0]}/v{version}/bin/apache-tomcat-{version}.zip'
    download(url=url, filename=f'tomcat_{version}.zip', dst_path=dest_dir, unzip=True, del_src=True)
    setEnv(name='CATALINA_HOME', value=f'{path.abspath(dest_dir)}/tomcat_{version}',
           endPath='\lib;%CATALINA_HOME%\lib\servlet-api.jar;%CATALINA_HOME%\lib\jsp-api.jar')

def jenkins_war_install(version: Optional[str] = 'latest', dest_dir: Optional[str] = '.'):
    url = f'https://mirrors.tuna.tsinghua.edu.cn/jenkins/war-stable/{version}/jenkins.war'
    download(url=url, filename='jenkins.war', dst_path=dest_dir)

def git_windows_install(version: Optional[str] = 'latest', dest_dir: Optional[str] = '.'):
    if version == 'latest':
        if get_osname() == 'windows':
            url = 'https://mirrors.tuna.tsinghua.edu.cn/github-release/git-for-windows/git/LatestRelease/'
            files = getWebList(url=url, match='href="Git-(.+?)-64-bit.exe"')
            download(url=f'{url}Git-{files[0]}-64-bit.exe', filename=f'Git-{files[0]}-64-bit.exe', dst_path=dest_dir)
        else:
            print('非windows系统可以使用命令自行安装哦！')
    else:
        print('该程序暂不持支选择版本哦！')

def node_install(version: Optional[str] = 'latest', dest_dir: Optional[str] = '.'):
    name = get_osname()
    res = urlopen(url='https://npm.taobao.org/mirrors/node/index.tab').read().decode('utf-8')
    all_lines = res.split('\n')
    if len(all_lines) > 1:
        if version == 'latest':
            version = all_lines[1].split('\t')[0][1:]
        else:
            version = [v.split('\t')[0][1:] for v in all_lines if f'v{version}' in v.split('\t')[0]]
            if len(version) == 0:
                version = all_lines[1].split('\t')[0][1:]
        if name == 'windows':
            url = f'https://npm.taobao.org/mirrors/node/v{version}/node-v{version}-win-x64.zip'
            download(url=url, filename=f'node-v{version}-win-x64.zip', dst_path=dest_dir, unzip=True, del_src=True)
            setEnv(name='NODE_HOME', value=f'{path.abspath(dest_dir)}/node-v{version}-win-x64', endPath='')
        elif name == 'mac':
            url = f'https://npm.taobao.org/mirrors/node/v{version}/node-v{version}-darwin-x64.tar.gz'
            download(url=url, filename=f'node-v{version}-darwin-x64.tar.gz', dst_path=dest_dir, unzip=True, del_src=True)
            setEnv(name='NODE_HOME', value=f'{path.abspath(dest_dir)}/node-v{version}-darwin-x64', endPath='')
        else:
            url = f'https://npm.taobao.org/mirrors/node/v{version}/node-v{version}-linux-x64.tar.gz'
            download(url=url, filename=f'node-v{version}-linux-x64.tar.gz', dst_path=dest_dir, unzip=True, del_src=True)
            setEnv(name='NODE_HOME', value=f'{path.abspath(dest_dir)}/node-v{version}-linux-x64', endPath='')

def allure_install(version: Optional[str] = 'latest', dest_dir: Optional[str] = '.'):
    ''' 默认安装开源版 '''
    url = 'https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/maven-metadata.xml'
    # url = 'https://github.com/allure-framework/allure2/releases'
    latest = getWebList(url=url, match='<latest>(.+?)</latest>')
    version = latest[0] if version == 'latest' and len(latest) > 0 else version
    name = get_osname()
    if name == 'windows':
        download(url=f'https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/{version}/allure-commandline-{version}.zip',
                 filename=f'allure-{version}.zip', dst_dir=dest_dir, unzip=True, del_src=False)
    else:
        download(url=f'https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/{version}/allure-commandline-{version}.tgz',
                 filename=f'allure-{version}.tgz', dst_dir=dest_dir, unzip=True, del_src=False)
    setEnv(name='ALLURE_HOME', value=f'{path.abspath(dest_dir)}/allure-{version}', addPath=True)

def svn_install(version: Optional[str] = 'latest', dest_dir: Optional[str] = '.'):
    ''' SVN安装 '''
    if version == 'latest':
        url = 'https://mirrors.tuna.tsinghua.edu.cn/apache/subversion'
        latest = getWebList(url=url,
                            match='href="https://osdn.net/projects/tortoisesvn/storage/(.+?)/Application/TortoiseSVN-(.+?)-x64-svn-(.+?).msi/"')
        if len(latest) > 0:
            download(
                url=f'https://osdn.net/projects/tortoisesvn/storage/{latest[0][0]}/Application/TortoiseSVN-{latest[0][1]}-x64-svn-{latest[0][2]}.msi"',
                dst_dir=dest_dir
            )
    else:
        url = f'https://osdn.net/projects/tortoisesvn/storage/{version}/Application/'
        latest = getWebList(url=url, match=f'href="/projects/tortoisesvn/storage/1.14.0/Application/TortoiseSVN-(.+?)-x64-svn-{version}.msi"')
        if len(latest) > 0:
            download(
                url=f'https://osdn.net/projects/tortoisesvn/storage/{version}/Application/TortoiseSVN-{latest[0]}-x64-svn-{version}.msi/"',
                dst_path=dest_dir
            )

def adb_install(version: Optional[str] = 'latest', dest_dir: Optional[str] = '.'):
    if version != 'latest': return
    name = get_osname()
    if name == 'windows':
        try:
            download(url='https://dl.google.com/android/repository/platform-tools-latest-windows.zip',
                     filename=f'platform-tools-latest-windows.zip', newdirname='platform-tools',
                     dst_path=dest_dir, unzip=True, del_src=True)
        except Exception as e:
            download(url='https://dl.adbdriver.com/upload/ADBDriverInstaller.exe', filename='ADBDriverInstaller.exe',
                     dst_path=dest_dir)
    elif name == 'mac':
        download(url='https://dl.google.com/android/repository/platform-tools-latest-darwin.zip',
                 filename=f'platform-tools-latest-darwin.zip', newdirname='platform-tools',
                 dst_path=dest_dir, unzip=True, del_src=True)
    else:
        download(url='https://dl.google.com/android/repository/platform-tools-latest-linux.zip',
                 filename=f'platform-tools-latest-linux.zip', newdirname='platform-tools',
                 dst_path=dest_dir, unzip=True, del_src=True)
    setEnv(name='ADB_HOME', value=f'{path.abspath(dest_dir)}/platform-tools', addPath=True)

def fiddler_install(version: Optional[str] = 'latest', dest_dir: Optional[str] = '.'):
    name = get_osname()
    if version != 'latest': return
    if name == 'windows':
        download(url='https://telerik-fiddler.s3.amazonaws.com/fiddler/FiddlerSetup.exe', filename='FiddlerSetup.exe',
                 dst_path=dest_dir)
        download(url='https://www.telerik.com/download/fiddler/fiddler-everywhere-windows', filename='fiddler-everywhere.exe',
                 dst_path=dest_dir)
    elif name == 'mac':
        download(url='https://www.telerik.com/download/fiddler/fiddler-everywhere-osx', filename='fiddler-everywhere.dmg',
                 dst_path=dest_dir)
    else:
        download(url='https://www.telerik.com/download/fiddler/fiddler-everywhere-linux', filename='fiddler-everywhere.AppImage',
                 dst_path=dest_dir)

def postman_install(version: Optional[str] = 'latest', dest_dir: Optional[str] = '.'):
    if version != 'latest': return
    name = get_osname()
    if name == 'windows':
        download(url='https://dl.pstmn.io/download/latest/win64', filename='postman-latest-win64.exe', dst_path=dest_dir)
    elif name == 'mac':
        download(url='https://dl.pstmn.io/download/latest/osx', filename='postman-osx-latest.zip', dst_path=dest_dir,
                 unzip=True, del_src=True)
    else:
        download(url='https://dl.pstmn.io/download/latest/linux64', filename='postman-linux64-latest.tar.gz',
                 dst_path=dest_dir, unzip=True, del_src=True)

def install(download_url: Optional[str] = None, **kwargs):
    '''
    指定开源软件
    :param download_url:    str,下载地址或多版本下载页
    :param version:         str,指定版本，默认最新版
    :param match_version:   str,模糊匹配版本，正则匹配，默认匹配指定版本或最大版本
    :param unzip:           bool,是否解压缩包，默认解压
    :param filename:        str,下载文件名
    :param newfilename:     str,解压后文件名
    :param newdirname:      str,解压后文件夹名
    :param env_name:        str,设置环境变量名
    :param env_value:       str,设置环境变量值
    :param addPath:         bool,是否添加到path变量中
    :param kwargs:          待扩展功能
    :return:
    '''
    if 'version' in kwargs.keys():
        version = kwargs.get('version')
    else:
        version = 'latest'
    if 'match_version' in kwargs.keys():
        match_version = kwargs.get('match_version')
    else:
        match_version = None
    if 'unzip' in kwargs.keys():
        unzip = kwargs.get('unzip')
    else:
        unzip = False
    if 'env_name' in kwargs.keys():
        env_name = kwargs.get('env_name')
    else:
        env_name = None
    if 'env_value' in kwargs.keys():
        env_value = kwargs.get('env_value')
    else:
        env_value = None
    if 'addPath' in kwargs.keys():
        addPath = kwargs.get('addPath')
    else:
        addPath = False