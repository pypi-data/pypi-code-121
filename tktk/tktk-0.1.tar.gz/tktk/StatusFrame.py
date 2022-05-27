import tkinter as tk
import threading
from DlxTestPack.DlxTestClassV5 import InThreadTime
import time
class StatusFrame(tk.Frame):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.strvar = tk.StringVar()
        self.MesList=["","","",""]
        self.columnconfigure(0,weight=1)
        self.statusbar = tk.Label(self,relief="sunken",anchor="sw",textvariable=self.strvar)
        
        self.statusbar.grid(column=0,row=0,sticky="WE")
        self.RunThread()
    def ShowMessage(self):
        while True:
            self.UpdateTime()
            self.strvar.set(" || ".join(self.MesList))
            time.sleep(1)

   
    def RunThread(self):
        self.UpdateStatus(0)
        self.UpdatePercent(0)
        tr=threading.Thread(target=self.ShowMessage)
        tr.setDaemon(True)
        tr.start()
    def UpdateInfo(self,msg):
        self.MesList[3]="Info:{}".format(msg)
    def UpdateStatus(self,index):
        '''
        0.Ready 1.Running 2.Finish 3.Fail 
        '''
        self.MesList[2]=["Ready","Running","Finish","Fail"][index]
        self.statusbar["bg"]=["green","yellow","green","red"][index]
        if index == 0 or index == 2:
            self.UpdatePercent([0,100][index>0])
    def UpdatePercent(self,pros):
        self.MesList[1]="{}>{} {:>3d}%".format("="*int(pros/10),"="*(10-int(pros/10)),pros)
    def UpdateTime(self):
        self.MesList[0]=InThreadTime.GetTimeStr()

if __name__=="__main__":
    import tkinter as tk

    xe = tk.Tk()
    xe.columnconfigure(0,weight=1)
    ggd = tk.Button(xe,text="231")
    ggd.grid(column=0,row=0)
    bb=StatusFrame(xe)
    # bb.ShowMessage('233')
    bb.UpdateStatus(2)
    bb.grid(column=0,row=1,sticky="WE")

    xe.mainloop()