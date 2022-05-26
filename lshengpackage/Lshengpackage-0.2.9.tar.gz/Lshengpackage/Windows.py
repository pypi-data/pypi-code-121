# 全局变量
# coding:utf-8
# !/usr/bin/env python#

class windows:
    def __init__(self, dm_obj):
        self.__dm_obj = dm_obj

    def hwnd_windows(self, name, taxon, rank):
        # rank 1+2+4+8+16
        hwnd_window = int(self.__dm_obj.EnumWindow(0, name, taxon, rank))
        return hwnd_window

    def down_windows(self, hwnd):
        down_window = self.__dm_obj.SetWindowState(hwnd, 1)
        return down_window

    def open_windows(self, hwnd):
        open_window = self.__dm_obj.ForceUnBindWindow(hwnd)
        return open_window

    def bind_windows(self, hwnd, type_windows, type_mouse, type_keyboard, public, mode):
        dm_bind = self.__dm_obj.BindWindowEx(hwnd, type_windows, type_mouse, type_keyboard, public, mode)
        return dm_bind

        #     "normal": 正常模式, 平常我们用的前台截屏模式
        #     "gdi": "gdi2": "dx2": "dx3": dx3模式
        #     dx模式, 用于窗口采用dx模式刷新, 取值可以是以下任意组合，组合采用
        #     "dx.graphic.2d" "dx.graphic.2d.2""dx.graphic.3d""dx.graphic.3d.8""dx.graphic.opengl"
        #     "dx.graphic.opengl.esv2""dx.graphic.3d.10plus"

        #     mouse
        #     1."normal": 正常模式, 平常我们用的前台鼠标模式
        #     2."windows": Windows模式, 采取模拟windows消息方式
        #     3."windows3": Windows3模式，采取模拟windows消息方式, 可以支持有多个子窗口的窗口后台

        #     1."dx.mouse.position.lock.api"此模式表示通过封锁系统API，来锁定鼠标位置.
        #     2."dx.mouse.position.lock.message"此模式表示通过封锁系统消息，来锁定鼠标位置.
        #     3."dx.mouse.focus.input.api"此模式表示通过封锁系统API来锁定鼠标输入焦点.
        #     4."dx.mouse.focus.input.message"此模式表示通过封锁系统消息来锁定鼠标输入焦点.
        #     5"dx.mouse.clip.lock.api"此模式表示通过封锁系统API来锁定刷新区域。注意，使用这个模式，在绑定前，必须要让窗口完全显示出来.
        #     6."dx.mouse.input.lock.api"此模式表示通过封锁系统API来锁定鼠标输入接口.
        #     7."dx.mouse.state.api"此模式表示通过封锁系统API来锁定鼠标输入状态.
        #     8."dx.mouse.state.message"此模式表示通过封锁系统消息来锁定鼠标输入状态.
        #     9."dx.mouse.api"此模式表示通过封锁系统API来模拟dx鼠标输入.
        #     10."dx.mouse.cursor"开启此模式，可以后台获取鼠标特征码.
        #     11."dx.mouse.raw.input"有些窗口需要这个才可以正常操作鼠标.
        #     12."dx.mouse.input.lock.api2"部分窗口在后台操作时，前台鼠标会移动, 需要这个属性.
        #     13."dx.mouse.input.lock.api3"部分窗口在后台操作时，前台鼠标会移动, 需要这个属性.
        #
        #     keypad
        #     "normal": 正常模式, 平常我们用的前台键盘模式
        #     "windows": Windows模式, 采取模拟windows消息方式
        #     同按键的后台插件.
        #     1."dx.keypad.input.lock.api"此模式表示通过封锁系统API来锁定键盘输入接口.
        #     2."dx.keypad.state.api"此模式表示通过封锁系统API来锁定键盘输入状态.
        #     3."dx.keypad.api"
        #     此模式表示通过封锁系统API来模拟dx键盘输入.
        #     4."dx.keypad.raw.input"有些窗口需要这个才可以正常操作键盘.
        #
        #     public
        #     1."dx.public.active.api"此模式表示通过封锁系统API来锁定窗口激活状态.注意，部分窗口在此模式下会耗费大量资源慎用.
        #     2."dx.public.active.message"此模式表示通过封锁系统消息来锁定窗口激活状态.注意，部分窗口在此模式下会耗费大量资源慎用.
        #     另外如果要让此模式生效，必须在绑定前，让绑定窗口处于激活状态, 否则此模式将失效.比如dm.SetWindowStatehwnd, 1然后再绑定.
        #     3."dx.public.disable.window.position"此模式将锁定绑定窗口位置.不可与"dx.public.fake.window.min"共用.
        #     4."dx.public.disable.window.size"此模式将锁定绑定窗口, 禁止改变大小.不可与"dx.public.fake.window.min"共用.
        #     5."dx.public.disable.window.minmax"此模式将禁止窗口最大化和最小化, 但是付出的代价是窗口同时也会被置顶.不可与"dx.public.fake.window.min"共用.
        #     6."dx.public.fake.window.min"此模式将允许目标窗口在最小化状态时，仍然能够像非最小化一样操作..另注意，此模式会导致任务栏顺序重排，
        #     所以如果是多开模式下，会看起来比较混乱，建议单开使用，多开不建议使用.同时此模式不是万能的, 有些情况下最小化以后图色会不刷新或者黑屏.
        #     7."dx.public.hide.dll"此模式将会隐藏目标进程的大漠插件，避免被检测..另外使用此模式前，请仔细做过测试，此模式可能会造成目标进程不稳定，出现崩溃。
        #     8."dx.public.active.api2"此模式表示通过封锁系统API来锁定窗口激活状态.部分窗口遮挡无法后台, 需要这个属性.
        #     9."dx.public.input.ime"此模式是配合SendStringIme使用.具体可以查看SendStringIme接口.
        #     10
        #     "dx.public.graphic.protect"
        #     此模式可以保护dx图色不被恶意检测.同时对dx.keypad.api和dx.mouse.api也有保护效果.这个参数可能会导致某些情况下目标图色失效.一般出现在场景重新加载的时候.重新绑定会恢复.
        #     11"dx.public.disable.window.show"禁止目标窗口显示, 这个一般用来配合dx.public.fake.window.min来使用.
        #     12"dx.public.anti.api"此模式可以突破部分窗口对后台的保护.
        #     13"dx.public.km.protect"此模式可以保护dx键鼠不被恶意检测.最好配合dx.public.anti.api一起使用.此属性可能会导致部分后台功能失效.
        #     14"dx.public.prevent.block"绑定模式1 3 5 7 101 103下，可能会导致部分窗口卡死.这个属性可以避免卡死.
        #     15"dx.public.ori.proc"此属性只能用在模式0 1 2 3 和101下.有些窗口在不同的界面下(比如登录界面和登录进以后的界面)，
        #     键鼠的控制效果不相同.那可以用这个属性来尝试让保持一致.注意的是，这个属性不可以滥用，确保测试无问题才可以使用.否则可能会导致后台失效.
        #     16"dx.public.down.cpu"此模式可以配合DownCpu来降低目标进程CPU占用.当图色方式降低CPU无效时，可以尝试此种方式.需要注意的是，
        #     当使用此方式降低CPU时，会让图色方式降低CPU失效
        #     17"dx.public.focus.message"当后台绑定后, 后台无法正常在焦点窗口输入文字时, 可以尝试加入此属性.此属性会强制键盘消息发送到焦点窗口.
        #     慎用此模式, 此模式有可能会导致后台键盘在某些情况下失灵.
        #     18"dx.public.graphic.speed"只针对图色中的dx模式有效.此模式会牺牲目标窗口的性能，来提高DX图色速度，尤其是目标窗口刷新很慢时，这个参数就很有用了.
        #     19"dx.public.memory"让本对象突破目标进程防护, 可以正常使用内存接口.当用此方式使用内存接口时，内存接口的速度会取决于目标窗口的刷新率.
        #     20"dx.public.inject.super"突破某些难以绑定的窗口.此属性仅对除了模式0和2的其他模式有效.
        #     21"dx.public.hack.speed"类似变速齿轮，配合接口HackSpeed使用
        #     22"dx.public.inject.c"突破某些难以绑定的窗口.此属性仅对除了模式0和2的其他模式有效.
        #
        #     mode
        #     0: 推荐模式此模式比较通用，而且后台效果是最好的.
        #     2: 同模式0, 如果模式0有崩溃问题，可以尝试此模式.注意0和2模式，当主绑定(第一个绑定同个窗口的对象)绑定成功后，那么调用主绑定的线程必须一直维持, 否则线程一旦推出, 对应的绑定也会消失.
        #     101: 超级绑定模式.可隐藏目标进程中的dm.dll.避免被恶意检测.效果要比dx.public.hide.dll好.推荐使用.
        #     103: 同模式101，如果模式101有崩溃问题，可以尝试此模式.
        #     11: 需要加载驱动, 适合一些特殊的窗口, 如果前面的无法绑定，可以尝试此模式.此模式不支持32位系统
        #     13: 需要加载驱动, 适合一些特殊的窗口, 如果前面的无法绑定，可以尝试此模式.此模式不支持32位系统
        # 需要注意的是: 模式101 103在大部分窗口下绑定都没问题。但也有少数特殊的窗口，比如有很多子窗口的窗口，对于这种窗口，在绑定时，
        # 一定要把鼠标指向一个可以输入文字的窗口，比如一个文本框，最好能激活这个文本框，这样可以保证绑定的成功.
