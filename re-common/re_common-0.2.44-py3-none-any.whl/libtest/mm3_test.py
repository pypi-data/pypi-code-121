import platform
import traceback

import win32file

from re_common.baselibrary.utils.basefile import BaseFile


# aa = r"F:\cnipa_ftp\SIPO\CN-PA-IMGS-10-A 中国发明专利申请公布标准化全文图像数据\20211109\20211109-1-002.ZIP"
# aa = r"F:\cnipa_ftp\SIPO\CN-PA-IMGS-10-A 中国发明专利申请公布标准化全文图像数据\20211109\20211109-1-001.ZIP"
def is_used(file_name):
    if "Windows" == platform.system():
        import win32file
        try:
            vHandle = win32file.CreateFile(file_name, win32file.GENERIC_READ, 0, None, win32file.OPEN_EXISTING,
                                           win32file.FILE_ATTRIBUTE_NORMAL, None)
            return int(vHandle) == win32file.INVALID_HANDLE_VALUE
        except:
            if "另一个程序正在使用此文件，进程无法访问。" in traceback.format_exc():
                return True
            else:
                return False
        finally:
            try:
                win32file.CloseHandle(vHandle)
            except:
                pass
    else:
        raise Exception("不是windows系统，请不要调用该函数判断文件是否被打开")

aa = is_used(r"\\192.168.31.171\caiji\test.txt")
print(aa)