from tkinter import Menu
import tkinter as tk
class MenuSet(Menu):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.Gui_Show()
    def Gui_Show(self):
        self.add_command(label="导入",command=lambda :self.KeyDeal("Import"))
        self.add_command(label="导出",command=lambda :self.KeyDeal("Export"))
        self.add_command(label="保存",command=lambda :self.KeyDeal("Save"))
    def KeyDeal(self,action:str):
        if action=="Import":
            self.CallBackImport()
        elif action=="Export":
            self.CallBackExport()
        elif action=="Save":
            self.CallBackSave()
    def CallBackImport(self):
        print("Import")
    def CallBackExport(self):
        print("Export")
    def CallBackSave(self):
        print("Save")


if __name__=="__main__":
    win = tk.Tk()
    xe = MenuSet(win)
    win.config(menu=xe)
    win.mainloop()