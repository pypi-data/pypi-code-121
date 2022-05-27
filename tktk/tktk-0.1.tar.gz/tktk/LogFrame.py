import tkinter as tk
from tkinter import LabelFrame
from tkinter.scrolledtext import ScrolledText


class LogFrame(LabelFrame):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.Gui_Show()
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)
    def Gui_Show(self):
        self.scText=ScrolledText(self)
        self.scText.grid(row=0,column=0,sticky="WNSE")
    def Gui_LogClear(self):
        self.scText.delete(0.0,'end')
    def Gui_LogInsert(self,msg,see_end:bool=False):
        self.scText.insert('end',msg+"\n")
        if see_end:
            self.scText.see('end')


if __name__=="__main__":
    win = tk.Tk()
    xe=LogFrame(win)
    xe.grid(column=0,row=0,sticky="WNSE")
    win.columnconfigure(0,weight=1)
    tk.Button(win,text="Insert1",command=lambda: xe.Gui_LogInsert("233")).grid(column=0,row=1,sticky='WNSE')
    tk.Button(win,text="Insert2",command=lambda: xe.Gui_LogInsert("244",True)).grid(column=0,row=2,sticky='WNSE')
    tk.Button(win,text="Clear",command=lambda: xe.Gui_LogClear()).grid(column=0,row=3,sticky='WNSE')
    win.mainloop()