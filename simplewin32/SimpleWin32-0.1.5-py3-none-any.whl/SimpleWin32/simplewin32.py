import time
import win32api, win32con, win32gui, win32clipboard, win32print, win32com.client
from typing import *
import os
import json
import winsound


class KeyCode:
    # 字母按键
    A = 65
    B = 66
    C = 67
    D = 68
    E = 69
    F = 70
    G = 71
    H = 72
    I = 73
    J = 74
    K = 75
    L = 76
    M = 77
    N = 78
    O = 79
    P = 80
    Q = 81
    R = 82
    S = 83
    T = 84
    U = 85
    V = 86
    W = 87
    X = 88
    Y = 89
    Z = 90
    # 字母键盘上方数字
    ZERO = 48
    ONE = 49
    TWO = 50
    THREE = 51
    FOUR = 52
    FIVE = 53
    SIX = 54
    SEVEN = 55
    EIGHT = 56
    NINE = 57
    # 小键盘按键
    Number_0 = 96
    Number_1 = 97
    Number_2 = 98
    Number_3 = 99
    Number_4 = 100
    Number_5 = 101
    Number_6 = 102
    Number_7 = 103
    Number_8 = 104
    Number_9 = 105
    MUL = 106
    ADD = 107
    Number_Enter = 108
    SUB = 109
    DecimalPoint = 110      # 小数点
    DIV = 111
    # 字母上方F数字键
    F1 = 112
    F2 = 113
    F3 = 114
    F4 = 115
    F5 = 116
    F6 = 117
    F7 = 118
    F8 = 119
    F9 = 120
    F10 = 121
    F11 = 122
    F12 = 123
    # 功能按键
    BackSpace = 8
    Tab = 9
    Clear = 12
    Enter = 13
    Shift = 16
    Control = 17
    Alt = 18
    CapeLock = 20
    Esc = 27
    SpaceBar = 32
    PageUp = 33
    PageDown = 34
    End = 35
    Home = 36
    LeftArrow = 37
    UpArrow = 38
    RightArrow = 39
    DownArrow = 40
    Insert = 45
    Delete = 46
    NumLock = 144
    SemicolonOrColon = 186      # 分号和引号";:"
    EqSignOrPluSign = 187       # 等于号和加号"=+"
    Comma = 188                 # 逗号和小于号",<"
    FullStop = 190              # 句号和大于号">."
    Dash = 189                  # 短横线破折号等"- --"
    Slash = 191                 # 斜杠和问号"/?"
    BeakLine = 192              # `~
    LeftSquareBrackets = 219    # {[
    RightSquareBrackets = 221   # ]}
    BackSlash = 220             # \|
    QuotationMark = 222         # '"
    # 多媒体按键
    AddVolume = 175             # 音量加
    SmallVolume = 174           # 音量减
    Stop = 179                  # 停止
    Mute = 173                  # 静音
    Browser = 172               # 浏览器
    Email = 180                 # 邮箱
    Search = 170                # 搜索
    Collect = 171               # 收藏

class MouseEvent:
    """
    部分常用事件集合
    BG开头为后台操作专属事件
    """
    # 鼠标事件
    MOUSELEFT = (win32con.MOUSEEVENTF_LEFTDOWN, win32con.MOUSEEVENTF_LEFTUP)
    MOUSERIGHT = (win32con.MOUSEEVENTF_RIGHTDOWN, win32con.MOUSEEVENTF_RIGHTUP)
    MOUSEMIDDLE = (win32con.MOUSEEVENTF_MIDDLEDOWN, win32con.MOUSEEVENTF_MIDDLEUP)
    BG_MOUSELEFT = (win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32con.WM_LBUTTONUP)
    BG_MOUSERIGHT = (win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, win32con.WM_RBUTTONUP)
    MOUSEWHEEL = win32con.MOUSEEVENTF_WHEEL

class __MessageType:
    """
    消息类型集合
    """
    OK = win32con.MB_OK                         # 带OK按钮
    YESNO = win32con.MB_YESNO                   # 带Yes和No按钮
    YESNOCANCEL = win32con.MB_YESNOCANCEL       # 带Yes、No、Cancel按钮
    HELP = win32con.MB_HELP                     # 说明信息
    WARNING = win32con.MB_ICONWARNING           # 警告提示信息
    QUESTION = win32con.MB_ICONQUESTION         # 疑问信息框
    ASTERISK = win32con.MB_ICONASTERISK         # 提示信息框
    OKCANCEL = win32con.MB_OKCANCEL             # 带OK和Cancel的确认框
    RETRYCANCEL = win32con.MB_RETRYCANCEL       # 重试取消信息框
    ERROR = win32con.MB_ICONERROR               # 错误提示框

class Mouse:
    """
    鼠标操作，
    :param x: x轴坐标
    :param y: y轴坐标点
    :param use_dpi: 当前坐标点是否以分辨率为准的，默认为False
    """
    def __init__(self, x, y, use_dpi=False):
        self.x = x
        self.y = y
        self.use_dpi = use_dpi
        if self.use_dpi is not False:
            self.scale = Window.ComputerDeviceScale()
            self.x = int(self.x / self.scale)
            self.y = int(self.y / self.scale)

    def move(self):
        win32api.SetCursorPos((self.x, self.y))
        return self

    @staticmethod
    def mouse_position(trans_dpi: bool = False) -> Tuple[int]:
        """
        返回当前鼠标所在坐标点
        :param trans_dpi: 是否转换为分辨率下的坐标点
        :return: 元组形式返回坐标点x,y
        """
        if trans_dpi is False:
            scale = 1
        else:
            scale = Window.ComputerDeviceScale()
        pos = win32gui.GetCursorPos()
        trans_pos = tuple(map(lambda x: round(x*scale), pos))
        return trans_pos

    def roll(self, down=True, time_count: int = 1):
        """
        鼠标中键滚动
        :param down: 布尔值，为True即滚轮向后滚动，页面往下跳转
        :param time_count: 指定滚动多少次
        :return:
        """
        num = -120 * time_count
        if down is not True:
            num = 120 * time_count
        win32api.mouse_event(MouseEvent.MOUSEWHEEL, 0, 0, num)
        return self

    def click(self, mouse_event=MouseEvent.MOUSELEFT):
        """
        数百哦点击
        :param mouse_event: 鼠标操作的按键，通过MouseEvent获取
        :return:
        """
        win32api.mouse_event(mouse_event[0], 0, 0, 0, 0)
        win32api.mouse_event(mouse_event[1], 0, 0, 0, 0)
        return self

    def bg_Click(self, hwnd, mouse_event=MouseEvent.BG_MOUSELEFT):
        """
        后台鼠标点击
        :param hwnd: 窗口句柄
        :param mouse_event: 鼠标按键，需使用MouseEvent的BG开头事件
        :return:
        """
        long_pos = win32api.MAKELONG(self.x, self.y)
        win32api.PostMessage(hwnd, mouse_event[0], mouse_event[1], long_pos)
        win32api.PostMessage(hwnd, mouse_event[2], mouse_event[1], long_pos)
        return self

class Keyboard:
    """
    需要填写键盘码，可以使用KeyCode类快捷指定
    """
    def __init__(self, keycode):
        self.keycode = keycode

    def click(self):
        win32api.keybd_event(int(self.keycode), 0, 0, 0)
        win32api.keybd_event(int(self.keycode), 0, win32con.KEYEVENTF_KEYUP, 0)
        return self

    def press(self):
        win32api.keybd_event(int(self.keycode), 0, 0, 0)
        return self

    def release(self):
        win32api.keybd_event(int(self.keycode), 0, win32con.KEYEVENTF_KEYUP, 0)
        return self

    def bg_Click(self, hwnd):
        win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, self.keycode, 0)
        win32api.PostMessage(hwnd, win32con.WM_KEYUP, self.keycode, 0)
        return self

# 后台事件处理方法
class Message(__MessageType):

    @staticmethod
    def InputMessage(message: str, hwnd=None):
        """
        进行文字输入
        :param hwnd: 窗口句柄，如果为空则视为前台剪贴板粘贴输入，需要窗口在最前端
        :param message: 需要进行输入的信息
        :return:
        """
        if hwnd is None:
            ClipBoard.SetClipboard(message)
            win32api.keybd_event(17, 0, 0, 0)
            win32api.keybd_event(86, 0, 0, 0)
            win32api.keybd_event(86, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)
        else:
            ord_str = [ord(x) for x in message]
            for item in ord_str:
                win32api.PostMessage(hwnd, win32con.WM_CHAR, item, 0)

    @staticmethod
    def AlertMessage(message: str, title: str, message_type, hwnd=0):
        """
        弹出窗口信息
        :param message: 消息体
        :param title: 标题
        :param message_type: 消息类型，可使用Message.OK等方式设置
        :param hwnd: 弹窗所属的父级句柄，默认为0
        :return:
        """
        win32gui.MessageBox(hwnd, message, title, message_type)

    @staticmethod
    def SetText(hwnd, text: str):
        """
        向部件中设置文字信息的操作，也可以使用InsertMessage
        :param hwnd: 进行输入的窗口句柄
        :param text: 需要输入的文字信息
        :return:
        """
        win32api.SendMessage(hwnd, win32con.WM_SETTEXT, None, text)

class ClipBoard:
    @staticmethod
    def SetClipboard(message: str, hwnd=None) -> None:
        """
        设置粘贴板数据
        :param message: 存放到粘贴板的数据信息
        :param hwnd: 窗口句柄
        :return:
        """
        if hwnd is None:
            win32clipboard.OpenClipboard()
        else:
            win32clipboard.OpenClipboard(hwnd)
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(message, win32con.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()

    @staticmethod
    def GetClipboard() -> str:
        """
        获取粘贴板数据
        :return: 粘贴板保存的数据
        """
        data = win32clipboard.GetClipboardData()
        return data


class Window:

    @staticmethod
    def WindowClick(father_hwnd, hwnd):
        """
        进行窗口部件点击
        :param father_hwnd: 父窗口句柄
        :param hwnd: 当前部件的句柄值
        :return:
        """
        win32api.SendMessage(father_hwnd, win32con.WM_COMMAND, 1, hwnd)

    @staticmethod
    def GetSystemMetrics() -> tuple:
        """
        或群当前屏幕尺寸
        :return: 屏幕x,y轴长度
        """
        width = win32api.GetSystemMetrics(0)
        height = win32api.GetSystemMetrics(1)
        return width, height

    @staticmethod
    def GetDeviceCaps() -> tuple:
        """
        获取当前设备分辨率
        :return: 分辨率前后值
        """
        hdc = win32gui.GetDC(0)
        dev_h = win32print.GetDeviceCaps(hdc, win32con.DESKTOPHORZRES)
        dev_v = win32print.GetDeviceCaps(hdc, win32con.DESKTOPVERTRES)
        return dev_h, dev_v

    @staticmethod
    def ComputerDeviceScale() -> float:
        """
        获取当前设备的屏幕缩放比
        :return: 当前设备的分辨率和实际尺寸的比率
        """
        size_width = Window.GetSystemMetrics()[0]
        dpi_h = Window.GetDeviceCaps()[0]
        return dpi_h / size_width

    @staticmethod
    def GetAllWindows(father_hwnd=None) -> list:
        """
        获取所有窗口句柄值
        :param father_hwnd: 父级窗口句柄，不输入获取全部一级句柄，输入父级句柄则查找子句柄
        :return: 句柄列表
        """
        if father_hwnd is None:
            windows = []
            win32gui.EnumWindows(lambda hwnd, params: windows.append(hwnd), None)
            return windows
        else:
            child_window = []
            win32gui.EnumChildWindows(father_hwnd, lambda hwnd, params: child_window.append(hwnd), None)
            return child_window

    @staticmethod
    def FindWindow(classname: str = None, title: str = None, father_hwnd=None) -> int:
        """
        查找窗口句柄值
        :param classname: 窗口的class值
        :param title: 窗口的标题文字
        :param father_hwnd: 父级句柄，填写后默认为查询子句柄
        :return: 返回窗口的句柄值
        """
        if any([classname, title]):
            if father_hwnd is None:
                window = win32gui.FindWindow(classname, title)
            else:
                window = win32gui.FindWindowEx(father_hwnd, None, classname, title)
            return window
        else:
            raise RuntimeError("Need Parameter: classname or windowtext")

    @staticmethod
    def GetWindowInfo(hwnd_list: Union[List[int], Tuple[int]], classname: bool = False, title: bool = False, beauty_json=False) -> Union[dict, str]:
        """
        获取窗口信息，class、title
        :param hwnd_list: 需要进行获取的句柄列表(或者元组)
        :param classname: 布尔值，是否获取class
        :param title: 布尔值，是否获取title
        :param beauty_json: 是否转换为更符合打印的json格式
        :return: 字典或者字符串json格式返回
        """
        window_info = {}
        if any([classname, title]):
            for handle in hwnd_list:
                if classname is False:
                    title = win32gui.GetWindowText(handle)
                    # window_info.append({handle: title})
                    window_info[handle] = title
                elif title is False:
                    classname = win32gui.GetClassName(handle)
                    # window_info.append({handle: classname})
                    window_info[handle] = classname
                else:
                    title = win32gui.GetWindowText(handle)
                    classname = win32gui.GetClassName(handle)
                    # window_info.append({handle: {"title": title, "class": classname}})
                    window_info[handle] = {"title": title, "class": classname}
            if beauty_json:
                window_info = json.dumps(window_info, indent=2, ensure_ascii=True, sort_keys=True)
            return window_info
        else:
            raise ValueError("Need Parameter: classname or title")

    @staticmethod
    def MoveOrResizeWindow(hwnd, x, y, width, height):
        """
        移动或者调整窗口大小
        :param hwnd: 窗口的句柄
        :param x: 窗口左上角x坐标点
        :param y: 窗口左上角y轴坐标点
        :param width: 窗口的宽
        :param height: 窗口的高
        :return:
        """
        win32gui.MoveWindow(hwnd, int(x), int(y), int(width), int(height), True)

    @staticmethod
    def ShowWindow(hwnd, minimize=False, maximize=False, default=False, hide=False):
        """
        显示窗口并设置为当前活动窗口，当最后两个参数都为False时默认显示
        :param hwnd: 需要操作的窗口句柄
        :param minimize: 最小化显示
        :param maximize: 最大化显示
        :param default: 使用程序自带的默认大小打开
        :param hide: 是否隐藏窗口
        :return:
        """
        if [minimize, maximize, default, hide].count(True) == 1:
            if minimize is not False:
                show_type = win32con.SW_MINIMIZE
            elif maximize is not False:
                show_type = win32con.SW_MAXIMIZE
            elif default is not False:
                show_type = win32con.SW_ERASE
            elif hide is not False:
                show_type = win32con.SW_HIDE
            else:
                show_type = win32con.SW_SHOW
            if hide is False:
                win32gui.ShowWindow(hwnd, show_type)
                win32gui.SetForegroundWindow(hwnd)
            else:
                win32gui.ShowWindow(hwnd, show_type)
        else:
            raise ValueError("Only one type can be set")

    @staticmethod
    def GetCurrentWindow(beauty_json=False) -> Union[dict, str]:
        window = win32gui.GetForegroundWindow()
        classname = win32gui.GetClassName(window)
        title = win32gui.GetWindowText(window)
        window_dict = {window: {"title": title, "class": classname}}
        if beauty_json:
            window_dict = json.dumps(window_dict, indent=2, ensure_ascii=True, sort_keys=True)
        return window_dict

    @staticmethod
    def GetWindowRect(hwnd) -> dict:
        """
        获取窗口左上右下的坐标点值
        :param hwnd: 当前窗口的句柄
        :return:
        """
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        return {"left": left, "top": top, "right": right, "bottom": bottom}

    @staticmethod
    def MarkChildWindow(hwnd, details_info=False) -> list:
        """
        标记窗口子句柄位置，需要安装numpy、opencv和pillow来使用
        保存标记和原始图片到当前文件同级的Win32Handle文件夹下
        图片红框标记，并在红框中标注句柄值
        并返回当前窗口的所有子句柄的值
        :param hwnd: 需要进行标记的父级窗口句柄
        :param details_info: 是否在图中标记更详细的class和title信息
        :return: 子句柄列表
        """
        try:
            import numpy as np
            import cv2
            from pathlib import Path
            from PIL import ImageGrab
        except ImportError:
            raise ImportError("You need to install numpy, opencv, pillow to use MarkChildWindow")
        waite_time = 0
        red_index = 255
        green_index = 0
        blue_index = 0
        pic_path = Path().cwd().resolve()/'Win32Handle'
        pic_path.mkdir(exist_ok=True)       # 创建文件夹
        str_pic_path = os.fspath(pic_path)
        scale = Window.ComputerDeviceScale()        # 获取设备分辨率与尺寸比
        child_window = Window.GetAllWindows(hwnd)   # 获取所有子句柄
        Window.ShowWindow(hwnd, maximize=True)      # 最大化显示窗口
        window_image = ImageGrab.grab()             # 全凭界面截图
        picname = f"{str_pic_path}/handle-{hwnd}.png"
        window_image.save(picname)
        Window.ShowWindow(hwnd, hide=True)          # 隐藏窗口
        while True:
            if (pic_path/f"handle-{hwnd}.png").exists():
                break
            elif waite_time == 3:
                raise FileExistsError("Image not found")
            else:
                waite_time += 1
                time.sleep(1)
        father_window_color = cv2.imread(picname)
        for child in child_window:
            rect = Window.GetWindowRect(child)
            pos_list = np.array([0 if int(x)<0 else int(x*scale) for x in list(rect.values())])
            cv2.rectangle(father_window_color, (pos_list[0], pos_list[1]), (pos_list[2], pos_list[3]),
                          (blue_index, green_index, red_index), 3)      # 图片区域框选
            center_x = int(np.median([pos_list[0], pos_list[2]]))
            center_y = int(np.median([pos_list[1], pos_list[3]]))
            if details_info is False:
                child_info = str(child)     # 判断是否显示class和title值
            else:
                child_info = str(Window.GetWindowInfo([child], True, True)[0])
            cv2.putText(father_window_color, child_info, (center_x, center_y), cv2.FONT_ITALIC, 0.8,
                        (blue_index, green_index, red_index), 2)        # 设置文字标注
            red_index = red_index - 15          # 颜色更改
            green_index = green_index + 15
            blue_index = blue_index + 15
            color_list = np.array([red_index >= 0, green_index <= 255, blue_index <= 255])
            if not all(color_list):
                red_index = 255
                blue_index = 0
                green_index = 0
        cv2.imwrite(f'{str_pic_path}/mark-{hwnd}.png', father_window_color)     # 保存标注的图片
        return child_window

    @staticmethod
    def FuzzySearchWindow(classname: str = None, title: str = None, father_hwnd=None, beauty_json=False) -> Union[dict, str]:
        """
        模糊搜索窗口句柄
        :param classname: 窗口的class属性
        :param title: 窗口的title
        :param father_hwnd: 父级句柄，填写则仅搜索此句柄下的子句柄
        :param beauty_json: 是否转换为更好打印的json格式
        :return: 字典或者字符串json形式返回窗口句柄和title、class值
        """
        search_res = {}
        windows = Window.GetAllWindows(father_hwnd)
        for window in windows:
            win_title = win32gui.GetWindowText(window)
            win_class = win32gui.GetClassName(window)
            if all([classname, title]):
                if (title in win_title) and (classname in win_class):
                    search_res[window] = {"title": win_title, "class": win_class}
            elif any([classname, title]):
                if (classname is not None) and (classname in win_class):
                    search_res[window] = {"title": win_title, "class": win_class}
                elif (title is not None) and (title in win_title):
                    search_res[window] = {"title": win_title, "class": win_class}
            else:
                raise ValueError("Need class or window title")
        if beauty_json:
            search_res = json.dumps(search_res, indent=2, ensure_ascii=True, sort_keys=True)
        return search_res

class Voice:
    @staticmethod
    def Speak(message: str):
        """
        调用系统声音对文字进行朗读
        :param message: 需要进行朗读的文字
        :return:
        """
        spk = win32com.client.Dispatch("SAPI.SpVoice")
        spk.Speak(message)

class Custom:
    """
    这里主要进行一些win32的功能封装，把某些常用的场景封装使用
    """
    @staticmethod
    def UploadFild(file: str):
        window = Window.FindWindow('#32770', '打开')                      # 获取上传文件主窗口
        button = Window.FindWindow('Button', None, window)               # 获取打开按钮的句柄值
        comboxex = Window.FindWindow('ComboBoxEx32', None, window)         # 获取子句柄combobox的句柄值
        combox = Window.FindWindow('ComboBox', None, comboxex)
        input_ = Window.FindWindow('Edit', None, combox)                 # 获取combobox下的输入框句柄值
        Message.SetText(input_, file)                                    # 进行文件输入
        win32api.SendMessage(window, win32con.WM_COMMAND, 1, button)     # 点击打开按钮进行上传

