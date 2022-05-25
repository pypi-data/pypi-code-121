import os
from ftplib import FTP
import traceback

class MyFtp:

    ftp = FTP()

    def __init__(self,host,port=21,debugLevel=2):
        self.ftp.connect(host,port)
        self.ftp.set_debuglevel(debugLevel)  # 打开调试级别2，显示详细信息

    def login(self,username,pwd):
        
        self.ftp.login(username,pwd)
#         print(self.ftp.welcome)

    def downloadFile(self,localpath,remotepath,filename,isOverwrite=True):
        dstPath = os.path.join(localpath, filename)
        if os.path.exists(dstPath):
            if not isOverwrite:
                print(dstPath, "exists")
            else:
                self.ftp.cwd(remotepath) 
                if filename in self.ftp.nlst():
                    file_handle = open(dstPath,"wb").write
                    self.ftp.retrbinary('RETR %s' % os.path.basename(filename),file_handle,blocksize=1024)
                else:
                    print("%s in ftp missing"%filename)
        else:
            self.ftp.cwd(remotepath) 
            if filename in self.ftp.nlst():
                file_handle = open(dstPath, "wb").write  # 以写模式在本地打开文件
                self.ftp.retrbinary('RETR %s' % os.path.basename(filename), file_handle, blocksize=1024) 
            else:
                print("%s in ftp missing" % filename)

    def upload_file(self,src_file, des_file):
        try:
            des_dirs = self.get_dirs(des_file)
            print(des_dirs)
            for d in des_dirs:
                if d not in self.ftp.nlst():
                    self.ftp.mkd(d)
                self.ftp.cwd(d)
            bufsize = 1024
            f = open(src_file, 'rb')
            des_file_name = os.path.basename(des_file)
            self.ftp.storbinary('STOR '+des_file_name, f, bufsize)
            print('upload %s success! '% des_file)
        except Exception as e:
            print('upload %s failed! ' % des_file)
            print(traceback.format_exc())
    def upload_fileTQW(self,src_file, des_path,fileName,reletive_path=""):
        try:
            self.ftp.cwd(des_path)
            for d in reletive_path.split(os.path.sep):
                if d not in self.ftp.nlst():
                    self.ftp.mkd(d)
                self.ftp.cwd(d)            
            bufsize = 1024
            f = open(src_file, 'rb')
            des_file_name = os.path.basename(fileName)
            self.ftp.storbinary('STOR '+des_file_name, f, bufsize)
            print('upload %s success! '% des_file_name)
        except Exception as e:
            print('upload %s failed! ' % des_file_name)
            print(traceback.format_exc())

    def get_dirs(self,filepath, isFile=True):

        dirs = filepath.strip("/").split(os.path.sep)
        if isFile:
            return dirs[:-1]
        else:
            return dirs

    def close(self):
        self.ftp.set_debuglevel(0)  # 关闭调试
        self.ftp.quit()

