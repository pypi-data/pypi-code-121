# coding=utf-8 
'''
Created on 2018年1月13日

@author: heguofeng
'''

# from secure_book_ui import SecureBookWidgets
import logging
from tkinter.messagebox import showinfo

from windfile.folder_ui import FolderWidgets
from windfile.filesync import SynchronizeWidgets
import yaml  
import requests
import json
from tkinter.ttk import Frame, Label
from tkinter import Menu, Tk
from tkinter.constants import W,E,N,S
from windbase import Tools





class Application(Frame):
    def __init__(self, master=None):
        try:
            self.config = yaml.load(open("./fmconfig.yaml","rt"),Loader=yaml.FullLoader)
        except:
            # print(traceback.format_exc())
            self.config = {"Version":"2.0.0","FileFolderDeleteConfirm":"Yes","DuplicationMode":2,
                            "max_depth":10,"max_nodes":500}
        super().__init__(master)
        self.grid(row=0, column=0, sticky=E + W + N + S)
        self.create_widgets()
        # self.getUpdateInfo()

    def create_widgets(self):
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.menu_bar = Menu(top)
        top['menu'] = self.menu_bar
        self.help_menu = Menu(self.menu_bar)
        self.menu_bar.add_cascade(label='帮助', menu=self.help_menu)
        self.help_menu.add_command(label='说明', command=self.openHelp)
        self.help_menu.add_command(label='关于', command=self.sayAbout)
        self.help_menu.add_command(label='退出', command=self.saveQuit)
        self.tool_menu = Menu(self.menu_bar)
        self.menu_bar.add_cascade(label='工具软件', menu=self.tool_menu)
        # self.tool_menu.add_command(label='文件消重', command=self.showDuplicationUI)
        self.tool_menu.add_command(label='文件同步', command=self.showSynchronizeUI)
        self.tool_menu.add_command(label='文件清理', command=self.showFolderUI)


        self.secure_menu = Menu(self.menu_bar)
        self.menu_bar.add_cascade(label='安全工具', menu=self.secure_menu)
        self.secure_menu.add_command(label='密码本', command=self.showSecureBookUI)


        self.mainWidgets = FolderWidgets(self,config=self.config)
        self.mainWidgets.grid(row=0, column=0, columnspan=10, rowspan=18, sticky=W + E + N + S)
        self.mainWidgets.rowconfigure(0, weight=1)
        self.mainWidgets.columnconfigure(0, weight=1)
        
        self.statusLabel = Label(self, text="文件管理工具 v2.0 Copyright @2022 by gonewind08@qq.com")
        self.statusLabel.grid(row=18, column=0, sticky=W + E)


    def saveQuit(self, quit=True):
        try:
            with open('fmconfig.yaml', "w") as f:
                yaml.dump(self.config, f)
        except:
            pass
        pass
        
        
    def showFolderUI(self): 
        self.mainWidgets.grid_remove()
        self.mainWidgets = FolderWidgets(self)
        self.mainWidgets.grid(row=0, column=0, columnspan=10, rowspan=18, sticky=W + E + N + S)
        self.mainWidgets.rowconfigure(0, weight=1)
        self.mainWidgets.columnconfigure(0, weight=1)     
        pass

    # def showDuplicationUI(self):
    #     self.mainWidgets.grid_remove()
    #     self.mainWidgets = DuplicateWidgets(self, config=self.config)
    #     self.mainWidgets.grid(row=0, column=0, columnspan=10, rowspan=18, sticky=W + E + N + S)
    #     self.mainWidgets.rowconfigure(0, weight=1)
    #     self.mainWidgets.columnconfigure(0, weight=1)
    #     pass
                

    def showSynchronizeUI(self): 
        self.mainWidgets.grid_remove()
        self.mainWidgets = SynchronizeWidgets(self, config=self.config)
        self.mainWidgets.grid(row=0, column=0, columnspan=10, rowspan=18, sticky=W + E + N + S)
        self.mainWidgets.rowconfigure(0, weight=1)
        self.mainWidgets.columnconfigure(0, weight=1)     
        pass

    def showSecureBookUI(self):
        # self.mainWidgets.grid_remove()
        # self.mainWidgets = SecureBookWidgets(self, config=self.config)
        # self.mainWidgets.grid(row=0, column=0, columnspan=10, rowspan=18, sticky=W + E + N + S)
        # self.mainWidgets.rowconfigure(0, weight=1)
        # self.mainWidgets.columnconfigure(0, weight=1)           
        pass

    def openHelp(self):
        Tools.browse_markdown("Readme.md")
        # md2html='\n<!-- Markdeep: --><style class="fallback">body{visibility:hidden;white-space:pre;font-family:monospace}</style><script src="markdeep.min.js" charset="utf-8"></script><script src="https://casual-effects.com/markdeep/latest/markdeep.min.js" charset="utf-8"></script><script>window.alreadyProcessedMarkdeep||(document.body.style.visibility="visible")</script>'
        # if not os.path.exists("Readme.md.html"):
        #     with open("Readme.md","rt",encoding="utf-8") as f:
        #         content = f.read()
        #     with open("Readme.md.html","wt") as f1:
        #         f1.write(content+md2html)
        #         f1.close()
        # webbrowser.open("Readme.md.html")
       
    def sayAbout(self):
        showinfo(title="About", message="感谢您使用文件管理工具，任何建议请发送gonewind08@qq.com!\n Version 2.0\n copyrigth @2022 \n")

    def getUpdateInfo(self):
        try:  # if network failure ,skip
            res = requests.get("http://joygame1.pythonanywhere.com/static/appinfo/filemanage",timeout=5)
            info = json.loads(res.text)
            message = info.get(self.config["Version"],"")
            if len(message):
                showinfo("系统提示",message)
        except:
            return

def main():
    Tools.set_debug(logging.DEBUG,"")
    root = Tk()
    root.title("FileManage")
    app = Application(master=root)
    app.mainloop()
    app.saveQuit(quit=False)
    pass

if __name__ == '__main__':
    main()
