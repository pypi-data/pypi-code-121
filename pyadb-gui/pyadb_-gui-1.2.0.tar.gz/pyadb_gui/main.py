import subprocess, os, re
import tkinter as tk
from tkinter import ttk
from tkinter.constants import END
import tkinter.messagebox as msg
from subprocess import getstatusoutput as sysget
from rich.console import Console
from rich.table import Table
import argparse


class PyadbGUI():
    def __init__(self, root=None):
        self.current_device = self.get_current_device()
        self.root = root  # 定义内部变量root
        self.root.title('pyadb_GUI')
        w = self.root.winfo_screenwidth()   # 屏幕宽度
        h = self.root.winfo_screenheight()  # 屏幕高度
        self.width = w//3
        self.height = h//2
        self.root.geometry('%dx%d+%d+%d' % (self.width, self.height, self.width, self.height//2))  # 设置窗口大小
        self.root.resizable(False,False)
        self.style = ttk.Style()
        self.style.theme_use('clam')
        font_set1 = ('calibri', 10, 'bold', 'underline')
        font_set2 = ('calibri', 10, 'bold')
        font_set3 = ('calibri', 10)
        self.style.configure('A.TButton', font = font_set1,foreground = 'Green')
        self.style.configure('B.TButton', font = font_set1,foreground = 'Purple')
        self.style.configure('C.TButton', font = font_set1,foreground = 'Blue')
        self.style.configure('D.TButton', font = font_set2)
        self.style.configure('TLabel', font = font_set3)
        self.style.configure("TCombobox", padding=5)
        self.style.configure("Treeview", rowheight=self.height//15)

        self.paddings = {'padx': 5, 'pady': 5}


        self.createNotebook()
 
    def createNotebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH,expand=True,padx=5,pady=5)

        # notebook 1 
        self.setup_page = ttk.Frame(self.notebook, padding=3)
        self.setup_page.pack(fill=tk.BOTH,expand=True,padx=5,pady=5)
        self.notebook.add(self.setup_page, text='Setup')
        self.createPage_setup()

        # notebook 2
        self.btn_page = ttk.Frame(self.notebook, padding=3)
        self.btn_page.pack(fill=tk.BOTH,expand=True,padx=5,pady=5)
        self.notebook.add(self.btn_page, text='Button')
        self.createPage_btn()

        # notebook 3
        self.info_page = ttk.Frame(self.notebook, padding=3)
        self.info_page.pack(fill=tk.BOTH,expand=True,padx=5,pady=5)
        self.notebook.add(self.info_page, text='Information')
        self.createPage_info()


    # Setup 页面布局
    def createPage_setup(self):
        self.setup_row_1()
        self.setup_row_2()
        self.setup_row_3()

        # 如果只有一个设备直接选为默认设备
        ttk.Label(self.setup_page, text=self.current_device, style='TLabel').grid(column=2, row=4, **self.paddings)

        self.setup_page.columnconfigure(1, weight=1)
        self.setup_page.columnconfigure(2, weight=1)
        self.setup_page.columnconfigure(3, weight=1)


    def setup_row_1(self):
        # 自动配置电脑静态 ip 功能
        ttk.Label(self.setup_page, text="Network devices", style='TLabel').grid(column=1, row=1, **self.paddings)
        self.setup_text1 = tk.StringVar()
        info = os.popen("nmcli d").read().strip()
        enx = re.findall(r"(enx\S*)", info)
        enx_devices = tuple(enx)
        self.setup_text_entry1 = ttk.Combobox(self.setup_page, textvariable=self.setup_text1)
        self.setup_text_entry1['values'] = enx_devices
        self.setup_text_entry1.grid(column=2, row=1, **self.paddings)
        ttk.Button(self.setup_page, text="Config", command=self.setup_config_eth, style='D.TButton').grid(column=3, row=1, **self.paddings)

    def setup_row_2(self):
        # adb connect 功能
        ttk.Label(self.setup_page, text="ADB connect").grid(column=1, row=2, **self.paddings)
        
        self.setup_text2 = tk.StringVar()
        adb_list = ('192.168.1.101')
        self.setup_text_entry2 = ttk.Combobox(self.setup_page, textvariable=self.setup_text2)
        self.setup_text_entry2['values'] = adb_list
        self.setup_text_entry2.grid(column=2, row=2, **self.paddings)

        ttk.Button(self.setup_page, text="Connect", command=self.setup_connect_adb, style='D.TButton').grid(column=3, row=2, **self.paddings)

    def setup_row_3(self):
        # select multi adb function
        ttk.Button(self.setup_page, text="Reload adb", command=self.setup_load_adb, style='D.TButton').grid(column=1, row=3, **self.paddings)
        self.setup_load_adb()
        self.setup_text3 = tk.StringVar()
        self.setup_text_entry3 = ttk.Combobox(self.setup_page, textvariable=self.setup_text3)
        self.setup_text_entry3['values'] = self.connectable_device
        self.setup_text_entry3.grid(column=2, row=3, **self.paddings)

        ttk.Button(self.setup_page, text="Select", command=self.setup_select_adb, style='D.TButton').grid(column=3, row=3, **self.paddings)

    def setup_config_eth(self):
        value = str(self.setup_text1.get())
        answer = msg.showinfo(title='Confirmation', message='请在命令行输入密码')
        try: 
            info = os.popen("nmcli c").read().strip()
            search = 'ethernet-'+value
            if search in info:
                search_result = sysget(f'sudo nmcli con delete {search}')
                os.popen("wait")
            out = sysget(f'sudo nmcli con add type ethernet ifname {value}')
            os.popen("wait")

            os.popen(f'sudo nmcli con modify ethernet-{value} ipv4.method manual ip4 192.168.1.102/24 gw4 192.168.1.1')
            # os.popen("wait")
            # os.popen(f'sudo nmcli connection up ethernet-{value}')
    
        except Exception as e:
            print(e)

    def setup_connect_adb(self):
        value = str(self.setup_text2.get())
        try: 
            os.popen(f'adb connect {value}')
            os.popen("wait")
            result = os.popen(f'adb connect {value}').read()
            if "already connected" in result:
                msg.showinfo("Message", "Connect Successful!")
            else:
                msg.showerror("Message", "Failed! wait a sec and retry")
                
    
        except Exception as e:
            print(e)

    def setup_select_adb(self):
        value = str(self.setup_text3.get())
        self.current_device = value
        self.createPage_btn()
        self.createPage_info()
        ttk.Label(self.setup_page, text=self.current_device).grid(column=2, row=4, **self.paddings)

    def setup_load_adb(self):
        info = os.popen("adb devices -l").read().strip()
        able_device = re.findall(r"(\w{16}|192.168.\S*)", info)
        self.connectable_device = tuple(able_device)

    @classmethod
    def get_current_device(self):
        info = os.popen("adb devices -l").read().strip()
        able_device = re.findall(r"(\w{16}|192.168.\S*)", info)
        connectable_device = tuple(able_device)
        if len(connectable_device) == 1:
            current_device = connectable_device[0]
        else:
            current_device = None
        return current_device



    # Button 页面布局
    def createPage_btn(self):

        # 实例化 ButtonPress 类
        bp = ButtonPress(self.current_device)

        btn_up = ttk.Button(self.btn_page, text='up', command=bp.ky_up, style = 'D.TButton').grid(row=1, column=2, **self.paddings)
        btn_down= ttk.Button(self.btn_page, text='down', command=bp.ky_down, style = 'D.TButton').grid(row=3, column=2, **self.paddings)
        btn_left = ttk.Button(self.btn_page, text='left', command=bp.ky_left, style = 'D.TButton').grid(row=2, column=1, **self.paddings)
        btn_right = ttk.Button(self.btn_page, text='right', command=bp.ky_right, style = 'D.TButton').grid(row=2, column=3, **self.paddings)
        btn_enter = ttk.Button(self.btn_page, text='Enter', command=bp.ky_select, style = 'D.TButton').grid(row=2, column=2, **self.paddings)

        ttk.Button(self.btn_page, text='Back', command=bp.ky_back, style = 'D.TButton').grid(row=4, column=1, **self.paddings)
        ttk.Button(self.btn_page, text='Home', command=bp.ky_home, style = 'D.TButton').grid(row=4, column=2, **self.paddings)
        ttk.Button(self.btn_page, text='Menu', command=bp.ky_menu, style = 'D.TButton').grid(row=4, column=3, **self.paddings)

        ttk.Button(self.btn_page, text='Play/Pause', command=bp.ky_play, style = 'D.TButton').grid(row=5, column=2, **self.paddings)
        ttk.Button(self.btn_page, text='Vol +', command=bp.ky_vol_up, style = 'D.TButton').grid(row=5, column=1, **self.paddings)
        ttk.Button(self.btn_page, text='Vol -', command=bp.ky_vol_down, style = 'D.TButton').grid(row=5, column=3, **self.paddings)

        ttk.Button(self.btn_page, text='Bluetooth', command=bp.shortcut_bluetooth, style = 'A.TButton').grid(row=6, column=1, **self.paddings)
        ttk.Button(self.btn_page, text='Wifi', command=bp.shortcut_wifi, style = 'A.TButton').grid(row=6, column=2, **self.paddings)
        ttk.Button(self.btn_page, text='Mirror', command=bp.shortcut_mirror, style = 'A.TButton').grid(row=6, column=3, **self.paddings)

        ttk.Button(self.btn_page, text='Reload', command=self.createPage_info, style='C.TButton').grid(row=7, column=1, **self.paddings)
        ttk.Button(self.btn_page, text='Reboot', command=bp.ky_reboot, style='B.TButton').grid(row=7, column=2, **self.paddings)
        ttk.Button(self.btn_page, text='OOBE', command=bp.ky_OOBE, style='B.TButton').grid(row=7, column=3, **self.paddings)

        ttk.Label(self.btn_page, text="input your text:").grid(column=1, row=8, **self.paddings)

        self.btn_page.columnconfigure(1, weight=1)
        self.btn_page.columnconfigure(2, weight=1)
        self.btn_page.columnconfigure(3, weight=1)

        # 可输入文字 统一以 input 开头
        self.input_text = tk.StringVar()
        account = ('kpbhat@us.neusoft.com',
                    'BeyondTech21!',
                    'coex-prime@amazon.com',
                    'lab126@126',
                    'wang.yao_neu@neusoft.com',
                    'w@ngya0O')

        # 可输入文字对应的输入框 在文字变量后加 entry
        self.input_text_entry = ttk.Combobox(self.btn_page, textvariable=self.input_text)
        self.input_text_entry['values'] = account
        self.input_text_entry.grid(column=2, row=8, **self.paddings)

        ttk.Button(self.btn_page, text="Input",  command=self.input, style='D.TButton').grid(column=3, row=8, **self.paddings)

    def input(self):
        value = str(self.input_text.get())
        out = sysget(f'adb -s {self.current_device} shell input text {value}')
        self.input_text_entry.delete(0, END)
        if out[0]==0:
            pass
        else:
            self.sayTry()


    # Info 页面布局
    def createPage_info(self):
        all_device_info = DeviceInfo(dsn=self.current_device).get_all_info()

        # tree view 布局
        columns = ('#1', '#2')
        tree = ttk.Treeview(self.info_page, columns=columns, height=100, show='headings')
        tree.column("#1", width=self.width//2-20)
        tree.column("#2", width=self.width//2-20)
        tree.heading('#1', text='Name')
        tree.heading('#2', text='Value')

        # adding data to the treeview
        for item in all_device_info:
            tree.insert('', tk.END, values=item)

        # bind the select event
        def item_selected(event):
            for selected_item in tree.selection():
                item = tree.item(selected_item)
                record = item['values']
                self.root.clipboard_clear()
                self.root.clipboard_append(record[1])

        tree.bind('<Double-1>', item_selected)

        tree.pack()




    @classmethod
    def sayTry(cls):
        msg.showinfo("Message", "手机连接失败,请尝试重新连接")  # 弹出消息窗口

    @classmethod
    def sayFail(cls):
        msg.showerror("Message", "操作失败")  # 弹出消息窗口



class ButtonPress():
    def __init__(self, dsn=None):
        self.current_device = dsn

    def ky_reboot(self):
        answer = msg.askyesno(title='Confirmation', message='Are you sure that you want to Reboot?')
        if answer:
            out = sysget(f'adb -s {self.current_device} shell reboot')
            if out[0]==0:
                pass
            else:
                PyadbGUI.sayTry()

    def ky_OOBE(self):
        answer = msg.askyesno(title='Confirmation', message='Are you sure that you want to OOBE?')
        if answer:
            out = sysget(f'adb -s {self.current_device} shell am start -n com.amazon.tv.settings.v2/com.amazon.tv.settings.v2.tv.FactoryResetActivity')
            if out[0]==0:
                pass
            else:
                PyadbGUI.sayTry()

    def ky_up(self):
        out = sysget(f'adb -s {self.current_device} shell input keyevent 19')
        if out[0]==0:
            pass
        else:
            PyadbGUI.sayTry()
 
    def ky_down(self):
        out = sysget(f'adb -s {self.current_device} shell input keyevent 20')
        if out[0]==0:
            pass
        else:
            PyadbGUI.sayTry()

    def ky_left(self):
        out = sysget(f'adb -s {self.current_device} shell input keyevent 21')
        if out[0]==0:
            pass
        else:
            PyadbGUI.sayTry()

    def ky_right(self):
        out = sysget(f'adb -s {self.current_device} shell input keyevent 22')
        if out[0]==0:
            pass
        else:
            PyadbGUI.sayTry()

    def ky_select(self):
        out = sysget(f'adb -s {self.current_device} shell input keyevent 23')
        if out[0]==0:
            pass
        else:
            PyadbGUI.sayTry()

    def ky_back(self):
        out = sysget(f'adb -s {self.current_device} shell input keyevent 4')
        if out[0]==0:
            pass
        else:
            PyadbGUI.sayTry()

    def ky_home(self):
        out = sysget(f'adb -s {self.current_device} shell input keyevent 3')
        if out[0]==0:
            pass
        else:
            PyadbGUI.sayTry()

    def ky_menu(self):
        out = sysget(f'adb -s {self.current_device} shell input keyevent 82')
        if out[0]==0:
            pass
        else:
            PyadbGUI.sayTry()

    def ky_play(self):
        out = sysget(f'adb -s {self.current_device} shell input keyevent 85')
        if out[0]==0:
            pass
        else:
            PyadbGUI.sayTry()

    def ky_vol_up(self):
        out = sysget(f'adb -s {self.current_device} shell input keyevent 24')
        if out[0]==0:
            pass
        else:
            PyadbGUI.sayTry()

    def ky_vol_down(self):
        out = sysget(f'adb -s {self.current_device} shell input keyevent 25')
        if out[0]==0:
            pass
        else:
            PyadbGUI.sayTry()

    def shortcut_bluetooth(self):
        sysget(f'adb -s {self.current_device} shell input keyevent 4')
        out = sysget(f'adb -s {self.current_device} shell am start -n com.amazon.tv.settings.v2/com.amazon.tv.settings.v2.tv.controllers_bluetooth_devices.ControllersAndBluetoothActivity')
        if out[0]==0:
            pass
        else:
            PyadbGUI.sayTry()

    def shortcut_wifi(self):
        sysget(f'adb -s {self.current_device} shell input keyevent 4')
        out = sysget(f'adb -s {self.current_device} shell am start -n com.amazon.tv.settings.v2/com.amazon.tv.settings.v2.tv.network.NetworkActivity')
        if out[0]==0:
            pass
        else:
            PyadbGUI.sayTry()

    def shortcut_mirror(self):
        out = sysget(f'adb -s {self.current_device} shell am start -n com.amazon.cast.sink/.DisplayMirroringSinkActivity')
        if out[0]==0:
            pass
        else:
            PyadbGUI.sayTry()



class DeviceInfo():
    def __init__(self, dsn = None):
        self.dsn = dsn

    def get_all_info(self):
        all_device_info = []
        if self.dsn is not None:
            all_device_info.append((f'TV Name', f'{self.get_name()}'))
            all_device_info.append((f'Time', f'{self.get_time()}'))
            all_device_info.append((f'DSN', f'{self.get_dsn()}'))
            all_device_info.append((f'Version', f'{self.get_build_version()}'))
            all_device_info.append((f'Wifi Mac Address', f'{self.get_mac_addr()[0]}'))
            all_device_info.append((f'Eth Mac Address', f'{self.get_mac_addr()[1]}'))
            all_device_info.append((f'Wifi IP Address', f'{self.get_ip_addr()[0]}'))
            all_device_info.append((f'Eth IP Address', f'{self.get_ip_addr()[1]}'))

        ble_all = self.get_bluetooth_all()
        for i in range(len(ble_all[0])):
                all_device_info.append((f'{ble_all[1][i]}', f'{ble_all[0][i]}'))
        return all_device_info



    def get_name(self):
        try:
            info = os.popen("adb devices -l").read().strip()
            name = re.findall(r"%s.*device:(\w*)"%self.dsn, info)[0]
        except:
            name = None
        return name
        

    def get_time(self):
        try:
            time = os.popen(f"adb -s {self.dsn} shell date").read().strip()
        except:
            time = None
        return time

    def get_build_version(self):
        try:
            info = os.popen(f"adb -s {self.dsn} shell cat /system/build.prop").read()
            info = info.strip()
        except:
            build_info = None
        try:
            if self.get_name() != "tank":
                build_info = re.findall(r"ro.build.description=\S+-(.*)\d{13}?\samz", info)[0].strip()
            else:
                build_info = re.findall(r"ro.build.description=(.*)", info)[0].strip()
        except:
            build_info = None
        return build_info

    def get_dsn(self):
        try:
            info = os.popen(f"adb -s {self.dsn} shell idme print").read().strip()
            dsn = re.findall(r"serial:\s(\S*)", info)[0].strip()
        except UnicodeDecodeError:
            info = subprocess.check_output(['adb', 'shell', 'idme', 'print'])
            regex = rb"serial:\s(\w*)"
            dsn = re.findall(regex, info)
            dsn = str(dsn)[3:-2]
        except:
            dsn = None
        return dsn
        
    def get_mac_addr(self):
        try:
            info = os.popen(f"adb -s {self.dsn} shell ifconfig").read()
            info = info.strip()
        except:
            wifi_mac = None
            eth_mac = None
        try:
            wifi_mac = re.findall(r"wlan0.*HWaddr\s(\S*)", info)[0].strip()
        except:
            wifi_mac = None
        try:
            eth_mac = re.findall(r"eth0.*HWaddr\s(\S*)", info)[0].strip()
        except:
            eth_mac = None

        return wifi_mac, eth_mac

    def get_ip_addr(self):
        try:
            info = os.popen(f"adb -s {self.dsn} shell ifconfig").read()
            info = info.strip()
        except:
            wifi_ip = None
            eth_ip = None
        try:
            wifi_ip = re.findall(r"wlan0.*\n.*addr:(\S*)", info)[0].strip()
        except:
            wifi_ip = None
        try:
            eth_ip = re.findall(r"eth0.*\n.*addr:(\S*)", info)[0].strip()
        except:
            eth_ip = None
        return wifi_ip, eth_ip

    def get_bluetooth_all(self):
        try:
            if self.get_name() != "tank":
                info = os.popen(f"adb -s {self.dsn} shell cat /data/misc/bluedroid/bt_config.conf").read()
                info = info.strip()
            else:
                mac=os.popen(f"adb -s {self.dsn} shell ls /data/misc/bluedroid | grep -oE '[a-z0-9]{12}'").read()
                mac = mac[0:2] + ":" + mac[2:4] + ":" + mac[4:6] + ":" + mac[6:8] + ":" + mac[8:10] + ":" + mac[10:12]
                device_mac_addr=mac
                device_name="Default"
        except:
            device_mac_addr = None
            device_name = None
        try:
            device_mac_addr = re.findall(r"\[(\S{17})\]", info)
        except:
            device_mac_addr = None
        try:
            device_name = re.findall(r"Timestamp.*\nName\s=\s(.*)", info)[0:]
        except:
            device_name = None
        
        return device_mac_addr, device_name



class PyadbCLI():
    def __init__(self):
        pass
    def show_info(self):
        current_device = PyadbGUI.get_current_device()
        all_device_info = DeviceInfo(dsn=current_device).get_all_info()
        # print(all_device_info)

        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Info", style="dim")
        table.add_column("Data")
        for i in all_device_info:
            table.add_row(i[0], i[1])
        console.print(table)

def run():
    root = tk.Tk()
    PyadbGUI(root)
    root.mainloop()

def main():
    parser = argparse.ArgumentParser(prog ='pyadb',
                                     description ='test pyadb man page')
  
    parser.add_argument('-gui', action ='store_const', const = True,
                        default = False, dest ='gui',
                        help ="run pyadb gui")
    parser.add_argument('-i', action ='store_const', const = True,
                        default = False, dest ='info',
                        help ="show adb devices")
  
    args = parser.parse_args()

    cli = PyadbCLI()
  
    if args.gui:
        run()
    elif args.info:
        cli.show_info()
    else:
        run()

if __name__ == '__main__':
    run()
