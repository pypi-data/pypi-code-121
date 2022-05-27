# coding=utf-8 
'''
Created on 2018年1月13日

@author: heguofeng

should change in filefolder.py 2018.3.27 
'''

import os
import datetime
import re
from tkinter.messagebox import askyesnocancel
from tkinter.ttk import Frame, Label, Entry, Button, Treeview, Scrollbar,\
    Combobox
from tkinter import StringVar, PhotoImage, Menu
from tkinter.constants import VERTICAL,W,E,N,S
from tkinter.filedialog import askdirectory
import time

from windfile.filefolder import  FFNode, Folder

NODE_TYPE_FILE = 1
NODE_TYPE_FOLDER = 2
NODE_TYPE_UP = 3
NODE_TYPE_DOWN = 4
NODE_TYPE_IMAGE = {NODE_TYPE_FILE:"image/file.gif", NODE_TYPE_FOLDER:"image/folder.gif"}
NODE_TYPE_STRING = {NODE_TYPE_FILE:"File", NODE_TYPE_FOLDER:"Folder"}
DATE_FILTER = {"日期选项":(0, 10000), "in 1 week":(0, 7), 'in 1 month':(7, 30), "in 3 month":(30, 90), 'in 1 year':(90, 365), '1 year earlier':(365, 10000)}
SIZE_FILTER = {"大小选项":(0, 100000000000), "< 1 KB":(0, 1000), '<1 MB':(1000, 1000000), "<10 MB":(1000000, 10000000), '>10 MB':(10000000, 100000000000)}
FILE_STATUS={"unknown":128,"new":1,"old":2,"same":4}
DUP_MODE={"重复选项":0,"Size":1,"Size&Date":2,"MD5":3}


class FolderWidgets(Frame):
    '''
    widgets has directory label,directory entry,open file dialog button and directory view
    also has popupmenu 
    select event 
    '''

    def __init__(self, master=None, folder_label="Folder",config={}):
        super().__init__(master)
        self.config = config
        self.folderPath = StringVar()
        self.nameFilter = StringVar()
        self.folderInfo = None
        self._load_icon()  # must left in memory
        self.showFullPath = config.get("show_full_path",False)
        Folder.set_max(config.get("max_depth",10),config.get("max_nodes",1000))
        self.folderLabel = folder_label
        self.createWidgets()
        self.dirTreeview.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.dirTreeview.bind("<ButtonRelease-1>", self.on_tree_click)
        self.dirTreeview.bind("<Button-3>", self.popupMenu)
        self.dirEntry.bind("<Button-3>", self.popupCopyPasteMenu)
        self.sizeFilterCombobox.bind("<<ComboboxSelected>>", self.filterShow)
        self.dateFilterCombobox.bind("<<ComboboxSelected>>", self.filterShow)
        self.ui_id_node = {}  # {iid:nodeinfo}
        # self.detachIids = {}  # {selfiid:parentiid)
        self.sortDict = {"Name":0, "Size":0, "Date":0, "Path":0, "#0":0}
        self.valueField = {"Path":0, "Name":1, "Size":2, "Date":3, }
        self.sort_func = lambda x:x.ntype+x.name
        self.filter_func = lambda x: True 
        
    def _load_icon(self):
        self.icon = {}
        self.icon[NODE_TYPE_FOLDER] = PhotoImage(data="iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAALLSURBVDhPLZNLT1NRFIUv8hJEAmrUODAxMQw0jtBIogMTBurIwMCQEBLjD9CJiXHiUGcmOnDq35AgLW1paQttaSpPrQE0EUOAYml735/rtDY56bn7nLX32mvtYzVwYR8aHEMAoRbYih7jNXd/MVfMoW/uaO+6NiF1qIHlBCH8GINvd6E4TH1xCEojhD8/ChMosflVBbC1t5XEIxTEJPeUzXJ0GGRGqC9b1HPtHC5akNRaPqHEbxBCtFTNFsALxEMptXerLns6spr0ElchI1BMa7YX5iy8WYtqoY1afpRG8QEUnlBfe0hl4xGsj8PGuJL9MQxEcGkYu9iLH7Fwol2qbuHnlaykta7vTf2b9d2isaYCK+asDyq+GKgFrzSEk+/Hi3TgFq7A6mO8lQnIT+JsTmKvjuGXpnDKE/hbT5VoiqD8TMofYXmIQ/o2brpTIp5S3yk4KBA6JQJvB9fPwtGmYr+xqzmBMrgHX6lWi+p+Acs1vuXuiFYH4eY4/u5bamtqYUHkUqKc1X9SyVUgmNde8UAi+0strRSRp3lZWFBw9xNBWoIKSOw0xBXTIt4GkU4cAZgbaAKRyE6imcCVjbeU8Qz8+kAjNdiswoxsFNiLt7fciXbiChDGFZ/Rd7KLWqobSzOBn7iOV7wvpZ9TN3bO98C0qAroxeRCVLG5dny1EJo1rVhugFruBpaZkyB5DcqvFZSYss+PdsCXFv1mRdnbpJ0Q0LSkMy+nffmlcUEiLo/C1nsJ1YMtBu7/Hl1zWbSZlYiGRexkK5lErGQVO1zUIIWay+1XGpgXsKRx1kWjMjOaCaO6SRKRvU0B1ZriyJlK4SY4gWlBc773mSB/jzDXLcqaSAlEpAc/1UeQUNXYIKGShkabuNzJKrb9Tm/EvAXzMvZ3CJYuaUbOweIF7Fi/qMuu9Hm81EWBzxJmO/Ay8l533OxlDfCGHrfLP8BrKFJCCdDsAAAAAElFTkSuQmCC")
        self.icon[NODE_TYPE_FILE] = PhotoImage(data="iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAEGSURBVDhPtdMxagJBGMVxBZNCCIi1jV0qCYoYEZs0xsLoAWySRq3UIgEbWwuxtM0BchKPoGghpEsag2gMQuL/obu46w4KwQc/mGXh7TfDrG8vEeRRcnlADkdTxS9mLnP8YYAojHnGFGEXfX0NlbzjGp5RwXi7dOQWHyhggS/c4SAqmGyXjmTxgysUoWm+8Qg/7JgK0tD4K3zu1tZzCHZUMEIADbSg/QeRRGYnhQq0HZ2Rnf2CJlRwD68ksMRBwRAX6KKPV7y5lHEDzwJrgifUDHQm2pKxQBO00THQbY3jfAX/2oIO8RJeh2cxHuILNMEpiUG30VFQh+68/kpdFBO974G/1BfeAF8PWWuSHBmSAAAAAElFTkSuQmCC")
        self.icon[NODE_TYPE_UP] = PhotoImage(data="iVBORw0KGgoAAAANSUhEUgAAAB0AAAAQCAYAAADqDXTRAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAJISURBVEhLvZNbTxNREMd9qgnvRqOiQFvtxW6BVjZeEkkwaCJ95CvoAzS2RCnsbrttrYUYXvwAfAZT/Cp98s0QWHGlLbvbdpuKf+fsRS4FL1yc5Jf5z8w5Z3Lm7F44qX1O+ryO/D+mZLhEs3S/U8+OfaxOhzxO+vyMNTRk3myvPANWHqOeHa2ca2MlE05oBd7sLE9CL09CKz8B3k2gIXCVjeexPmfZ2dm6FPRr8ojZWRqH/uYRMQ6tRLo0ASw/hCqOrjpLz8aqcsjTyMXWdssPoOXHoOd5G5mnmEe7cA9GId5ShJGEs+V0xt5Lo3fDEo+mHIdB6Ja/a+HmukVLm+ppG1s3pPfC22E0pQgMopmNoMWwNAedtJG9Q/UQvuejVIuaSuaEjavytId9mShxaAq3YTDEPd8UbpF2YXlbd3NB6FKEGsf/rfGGPNXXEKIVFCPQF32E/6/QGAs+mLkAm4Cp0u/lHPlnq2WHV1EMojE/SAxZ7GS8PfqonEtb8EGjUa9LvN859nhTs/GEIQVbesbeXH89aOEetl8fh7umK9GUxMAaeyrn+F5jX54hBkx9fgBq+ga+zdmo6f4eDuf3x+4+xq5EE6CP8dP7pxedNntWk7ipxmLQ3HnVj62X137xNXX9QHyY39ftWlf00htHDzZmDQ0h3K6lrmJz5jKU2SvYnLW9Qt7VtnfpXWPFSSdP3q5RPHMJP9io2Y2T1HhbjL2g67eNhSEoqQF8YaSJuUHbH4lbI2+td7y7l0F6yzrDIXUTyIexLXAffgLEu2VV4B5CWgAAAABJRU5ErkJggg==")
        self.icon[NODE_TYPE_DOWN] = PhotoImage(data="iVBORw0KGgoAAAANSUhEUgAAAB0AAAAQCAYAAADqDXTRAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAJVSURBVEhLvZPLbhJRHMZZYdK90ajVlotykaEFCvGS2KSmmliWfQVdtERotMAwwyAibUw3PkCfwVBfhVV3pmnHioVhhssQrJ/nzMyxldKmVfRLfvlfzuWbyzm2g1z4RSPDdVsZB+TkBL5QUoSVSTMOhY2RaMy3IltLIfm+sYdF8hZQ8OOA5z7aqOoCt6Bm/N168hr2lq5AXr6KvWUzyiSy3IyMk3OMOmH1STTHSL10GT8EFzSeq2wnnl4yTKmocT3r1ZuvxrH/8vovviZv/FYPcva4OdbPOaGJwcr2h2OGTDV+Oq7mPLq2OoFa6ia+rZjUUuMnGOwfr9k6yqHghELfcJghU02MxFXB29HSDiirDjReTxrQnNUsPw02p08/ac6zVZUW7db2p6suTm2i6CULjwyaafLEA/mwHqPLu6CIQX1HiLmtbc/WrrQwpvDBCooBaFnytFn3uVApGRf0vAdNMaDX0lzc2vJ8op+kIYYqKHFo83fQouSOYpu/TXIG7Zt5P+9FUwjocjpyMUOmquSz00OAd1NoCwG0CG0xgA7FyDlyKklfvEvGffheCJI8SAyn/8yQqbros6v0jddiaEsRtAiaEWcMWK9fnKF9nd4Aa+nfyXjjfHjrsPwAaiEKrRAzkWKkjqH75h5UKdSRR2XItCN43Yo0rffWZqG9fUSYhVoieWkOWH+IWi60aU0dreS0P65IUb23Pg+tPA+1/AR4P2dc/t3n4TFr2uglk2ugEuPuxjNg4zHoCaf/3Rr+d6LGWul+ryFGP/0XQ6bPCZfTSi8om+0nKo5lLNpCa/oAAAAASUVORK5CYII=")
        # self.icon[5] = PhotoImage(data="iVBORw0KGgoAAAANSUhEUgAAABkAAAAZCAYAAADE6YVjAAAAAXNSR0IArs4c6QAAAARnQU1BAACx\njwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAApSURBVEhL7c0xAQAwDASh+jf91cCS6TDA24ES\nUkJKSAkpISWkhJSA7QPKeLrEEQphcgAAAABJRU5ErkJggg==")
        #         for t in NODE_TYPE_IMAGE:
        #             self.icon[t] = ImageTk.PhotoImage(Image.open(NODE_TYPE_IMAGE[t]).resize((16,16))) #must left in memory
            
    def popupMenu(self, event):
        self.popmenu.post(event.x_root, event.y_root)  
    
    def popupCopyPasteMenu(self,event):
        self.popupCCPMenu.post(event.x_root, event.y_root)
       
    def popupCopy(self):
        self.clipboard_clear()
        self.clipboard_append(string=self.folderPath.get(),type='STRING') 
        
    def popupPaste(self):
        self.folderPath.set(self.clipboard_get(type='STRING'))
       
    def on_tree_click(self, event):
        selected = self.dirTreeview.identify_row(event.y)
        self.set_statusLabel(text="%s"%(self.ui_id_node[selected].fullpath if selected else ""))
        

    def on_tree_select(self, event):
        selected:tuple = self.dirTreeview.selection()
        # if selected:
        #     selected += self.descendant(selected[0])
        #     self.dirTreeview.selection_set(selected)
        # count = self.selected_count()
        # self.master.statusLabel.config(text="{} folder {} files total size {} bytes.".format(count[0],count[1],count[2])) 
        # self.set_statusLabel(text="%s"%(self.ui_id_node[selected[0]].fullpath if selected else ""))      
        pass 

    def selected_count(self):
        selected = self.dirTreeview.selection()
        nodes = []
        for n in selected:
            nodes.append(self.ui_id_node[n])
        return FFNode.count_nodes(nodes)

    def set_statusLabel(self,text=""):
        status_text = text
        selected = self.dirTreeview.selection()
        if len(selected)>=2:
            count = self.selected_count()
            status_text += "     Total: {} folder {} files total size {} bytes.".format(count[0],count[1],count[2])
        self.statusLabel.config(text=status_text) 

    def selecteFilesInSameFolder(self):
        selected = self.dirTreeview.selection()
        if len(selected) == 0:
            return 
        selected_node:FFNode = self.ui_id_node[selected[0]] 
        parent = selected_node.parent
        if parent:
            for node in parent.nodes.values():
                self.dirTreeview.selection_add(node.ui_id)
        # count = self.selected_count()
        self.set_statusLabel(text="{} ".format(parent.fullpath)) 
        pass
    
    def clearSelected(self):
        self.dirTreeview.selection_remove(self.dirTreeview.selection())
        return 
    
            
    def createWidgets(self):

        self.dirLabel = Label(self, compound="left" , anchor='w',text=self.folderLabel, \
                              image=self.icon[NODE_TYPE_FOLDER])

        self.dirEntry = Entry(self, width=40, textvariable=self.folderPath)
        self.dirButton = Button(self, text="选择目录", command=self.dirselect)

        self.dirTreeview = Treeview(self, columns=("Path", "Name", "Size", "Date","ntype"), \
                                displaycolumns=['Path', 'Name', 'Size', 'Date'], \
                                height=16, show='tree headings')
        self.dirTreeview.heading('#0', command=self.sortClear)
        self.dirTreeview.heading('Path', text="路径", command=lambda : self.sort("Path"))
        self.dirTreeview.heading('Name', text="名称", command=lambda : self.sort("Name"))
        self.dirTreeview.heading('Size', text="大小", command=lambda : self.sort("Size"))
        self.dirTreeview.heading('Date', text="日期", command=lambda : self.sort("Date"))
        self.dirTreeview.column('Path', width=260)
        self.dirTreeview.column('Date', width=80)
        self.dirTreeview.column('Size', width=60)
        self.dirTreeview.column('Name', width=80)
        self.dirTreeview.column('#0', width=60)
        self.dirScrollbar = Scrollbar(self, orient=VERTICAL)

        self.dirLabel.grid(row=0, column=0, sticky= W)
        self.dirEntry.grid(row=0, column=1, columnspan=7, sticky=E + W)
        self.dirButton.grid(row=0, column=7, sticky=E + W)
        self.dirTreeview.grid(row=1, column=0, rowspan=16, columnspan=10, sticky=W + E + N + S)
        self.dirScrollbar.grid(row=1, column=9, rowspan=16, sticky=N + S + E)
        
        self.dirLabel.rowconfigure(0, weight=1)
        self.dirLabel.rowconfigure(0, weight=1)
        
        self.dirScrollbar.configure(command=self.dirTreeview.yview)
        self.dirTreeview.configure(yscrollcommand=self.dirScrollbar.set)
        
        self.sizeFilterCombobox = Combobox(self , values=list(SIZE_FILTER.keys()), width=8)
        self.sizeFilterCombobox.grid(row=17, column=2)
        self.sizeFilterCombobox.set("大小选项")

        self.dateFilterCombobox = Combobox(self, values=list(DATE_FILTER.keys()), width=12)
        self.dateFilterCombobox.grid(row=17, column=4)
        self.dateFilterCombobox.set("日期选项")
        self.nameFilterLabel = Label(self, text="文件名:")
        self.nameFilterLabel.grid(row=17, column=5)
        self.nameFilterEntry = Entry(self, width=20, textvariable=self.nameFilter)
        self.nameFilterEntry.grid(row=17, column=6)
        self.nameFilterEntry.bind("<Return>", self.filterShow)
        
        self.statusLabel = Label(self, text="", anchor='w',wraplength=1000)
        self.statusLabel.grid(row=18, column=0, columnspan=10, sticky=W + E)

        self.popmenu = Menu(self, tearoff=0)
        self.popmenu.add_command(label="资源管理器打开所选", command=self.openExplorer)
        self.popmenu.add_command(label="复制目录到剪贴板", command=self.copy2Clipboard)
        self.popmenu.add_separator()
        self.popmenu.add_command(label="选择该目录所有文件", command=self.selecteFilesInSameFolder)
        self.popmenu.add_command(label="取消选择", command=self.clearSelected)
        self.popmenu.add_separator()
        self.popmenu.add_command(label="删除所选", command=self.deleteFiles)
        self.popmenu.add_command(label="复制所选", command=self.copyFiles)
        self.popmenu.add_command(label="移动所选", command=self.moveFiles)

        self.popupCCPMenu = Menu(self, tearoff=0)
        self.popupCCPMenu.add_command(label="copy", command=self.popupCopy)
        self.popupCCPMenu.add_command(label="paste", command=self.popupPaste)

        if self.config.get("dupFinder",True):
            self.dupCombobox = Combobox(self, values=list(DUP_MODE.keys()), width=9)
            self.dupCombobox.set("重复选项")
            self.dupCombobox.grid(row=17, column=8)
            self.select1stButton = Button(self, text="选择第一个", command=self.select1st)
            self.select1stButton.grid(row=17, column=9)

         
        if not self.showFullPath:
            self.dirTreeview.config(displaycolumns=['Name', 'Size', 'Date'])


    
    def descendant(self, parentiid):
        iids = tuple()
        for i in self.dirTreeview.get_children(parentiid):
            iids += tuple([i])
            iids += self.descendant(i)
        return iids
    
    def _clearSort(self):
        for item in self.sortDict:
            self.sortDict[item] = 0
            self.dirTreeview.heading(item, image="")        
            
    def sortClear(self):
        # self.sort_func = lambda x:x.ntype+x.name
        self.filter_func = lambda x: True 
        self.clear_heading_image()
        self.refreshTreeview()
 


    def sort(self, col:str,reverse:bool=False):
        # order or reverse
        icon_id = NODE_TYPE_DOWN if reverse else NODE_TYPE_UP
        self.clear_heading_image()
        self.dirTreeview.heading(col, image=self.icon[icon_id])
        tv_values = [(self.dirTreeview.item(id,"values"),id) for id in self.descendant("")]
        file_filter = filter(lambda x: x[0][4] == "file", tv_values)
        file_tv_values = list(file_filter)
        if col in ["Size"]:
            sort_key = lambda x:int(x[0][2])
        else:
            sort_key = lambda x:x[0][self.valueField[col]]
        file_tv_values.sort(key=sort_key,reverse=reverse)
        for index in range(0, len(file_tv_values)):
            self.dirTreeview.move(file_tv_values[index][1], "", index)
        self.dirTreeview.heading(col,command=lambda: self.sort(col, not reverse))
    
    def clear_heading_image(self):
        for col in ["Size","Date","Name"]:
            self.dirTreeview.heading(col, image="")

    def select1st(self):
        self.clearSelected()
        dupMode = self.dupCombobox.get()
        dupMode = "Size&Date" if dupMode=="重复选项" else dupMode
        tv_values = [(self.dirTreeview.item(id,"values"),id) for id in self.descendant("")]
        file_filter = filter(lambda x: x[0][4] == "file", tv_values)
        file_tv_values = list(file_filter)
        selected = []
        last_size,last_mtime,last_tv_id="","",""
        last_selected = 0
        for tv_item in file_tv_values:
            if tv_item[0][2]==last_size and ( tv_item[0][3]==last_mtime or dupMode in ["Size","MD5"]):
                if (not dupMode == "MD5") or self.ui_id_node[last_tv_id].md5 == self.ui_id_node[tv_item[1]].md5: 
                    if not last_selected:
                        selected.append(last_tv_id)
                        last_selected += 1
            else:
                last_selected = 0

            last_size,last_mtime,last_tv_id = tv_item[0][2],tv_item[0][3],tv_item[1]
        self.dirTreeview.selection_set(selected)
        self.select1stButton.config(text="选择第二个后", command=self.select2nd)

        self.set_statusLabel(text="Find {} items.".format(len(self.dirTreeview.selection())))
        pass


    
    def select2nd(self):
        self.clearSelected()
        tv_values = [(self.dirTreeview.item(id,"values"),id) for id in self.descendant("")]
        dupMode = self.dupCombobox.get()
        dupMode = "Size&Date" if dupMode=="重复选项" else dupMode
        file_filter = filter(lambda x: x[0][4] == "file", tv_values)
        file_tv_values = list(file_filter)
        selected = []
        last_size,last_mtime,last_tv_id="","",""
        for tv_item in file_tv_values:
            if tv_item[0][2]==last_size and ( tv_item[0][3]==last_mtime or dupMode in ["Size","MD5"]):
                if (not dupMode == "MD5") or self.ui_id_node[last_tv_id].md5 == self.ui_id_node[tv_item[1]].md5: 
                    selected.append(tv_item[1])
            last_size,last_mtime,last_tv_id = tv_item[0][2],tv_item[0][3],tv_item[1]
        self.dirTreeview.selection_set(selected)
        self.select1stButton.config(text="选择第一个", command=self.select1st)
        self.set_statusLabel(text="Find {} items.".format(len(self.dirTreeview.selection())))
        pass

        
    def _get1stSelectionPath(self):
        path="."
        selected = self.dirTreeview.selection()
        if len(selected) > 0:
            path = self.ui_id_node[selected[0]].parent_path
        return path
              
    def openExplorer(self):
        os.system("explorer.exe %s" % self._get1stSelectionPath()) 

    
    def copy2Clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(string=self._get1stSelectionPath(),type='STRING')        

    def deleteFiles(self, files:set=(),confirm:bool=False):
        '''
        delete given tv_ids file

        Args:
            files (set, optional): set of tv_ids. Defaults to ().
        '''
        if files == ():
            files = self.dirTreeview.selection()   
        message="共%d个文件：\n"%len(files)
        for f in files:
            node:FFNode = self.ui_id_node[f]
            message+=node.fullpath+"\n"
        if confirm or askyesnocancel("真的要删除这些文件吗？",message[0:1000]):
            for f in files:
                if f in self.dirTreeview.selection():
                # if self.ui_id_node[f].ui_id == f:
                    self.ui_id_node[f].remove()
                    self.dirTreeview.delete(f)
                self.ui_id_node.pop(f)
        
        self.set_statusLabel(text="Deleted! ") 
        return 
    

    def copyFiles(self, files:set=()):
        '''
        copy given tv_ids file to dst folder

        Args:
            files (set, optional): _description_. Defaults to ().
        '''
        # print("copy")
        selectedDir = askdirectory(initialdir=self.folderPath.get())
        if files == ():
            files = self.dirTreeview.selection()   
        if selectedDir and files:
            for f in files:
                node:FFNode = self.ui_id_node[f]
                node.copy2path(selectedDir)
        # count = self.selected_count()
        self.set_statusLabel(text="Copyed! ") 
        pass

    def moveFiles(self,files:set=()):
        self.copyFiles(files)
        self.deleteFiles(files,confirm=True)
        self.set_statusLabel(text="Moved! ") 
        
    def dirselect(self):
        selectedDir = askdirectory(initialdir=self.folderPath.get())
        if selectedDir != "":
            self.folderPath.set(selectedDir)
            self.folderInfo = Folder(name=selectedDir).load()
            # logging.debug(self.folderInfo)
            self.refreshTreeview()
        return
    
    def refreshTreeview(self, folderInfo=None):
        self.clearTreeview()
        tv_folder = folderInfo if folderInfo else self.folderInfo
        self.insertTreeviewItem("", tv_folder)
    
    def clearTreeview(self):
        for i in self.dirTreeview.get_children():
            self.dirTreeview.delete(i)
        self.ui_id_node.clear()
        # self.detachIids.clear()
        self._clearSort()

            
    def insertTreeviewItem(self, treeParent, node:FFNode, showFullPath=False):
        if node is None:
            tree_id = self.dirTreeview.insert(parent=treeParent, index='end', open=True, values=("", "", "", "",""))
            self.ui_id_node[tree_id] = None
            return tree_id
        
        if node.ntype == "folder":
            tree_id = self.dirTreeview.insert(parent=treeParent, index='end', open=True, \
                                values=("",node.name, "", "","folder"),
                                image=self.icon[NODE_TYPE_FOLDER])
            for child_node in node.sorted_nodes(sort_func=self.sort_func):
                self.insertTreeviewItem(tree_id, child_node)
            
        if node.ntype == "file":
            if not self.filter_func(node):
                return ""
            tree_id = self.dirTreeview.insert(parent=treeParent, index='end', \
                                 values=("", node.name, node.size, \
                                         datetime.datetime.fromtimestamp(node.mtime).strftime('%Y%m%d %H:%M:%S'), "file"\
                                        ), \
                                image=self.icon[NODE_TYPE_FILE])
        self.ui_id_node[tree_id] = node
        node.ui_id = tree_id
        return tree_id    
    
      

            

    def filterShow(self, event=None):
        # self._removeFilterShow("")
        filter = self._getFilter()
        self.filter_func = lambda x: self._filter_func(x,filter)
        self.refreshTreeview()

        # if self.folderInfo:
        #     filter_folder = self.folderInfo.filter(lambda x: self._filter_func(x,filter))
        #     self.refreshTreeview(filter_folder)
        pass

    def _getFilter(self):
        sizeFilter = SIZE_FILTER[self.sizeFilterCombobox.get()]
        dateFilter = DATE_FILTER[self.dateFilterCombobox.get()]
        date0 = time.time() - dateFilter[1] * 24 * 60 * 60
        date1 = time.time() - dateFilter[0] * 24 * 60 * 60
        name_filter = self.nameFilter.get()
        return {"size":sizeFilter, "date":(date0, date1),"name":name_filter}
           
    def _filter_func(self,node:FFNode,filter={}):
        '''
        filter = {"size":(0,10000000),"date":（"19000101"，"2099010"),"status":"="}
        return: 
        '''
        sizeFilter = filter.get("size", (0,100000000000))
        dateFilter = filter.get("date", (0, 3229994183))
        nameFilter = filter.get("name","[\s\S]")
        size = node.size
        date = node.mtime
        name = node.name
        if size <= sizeFilter[1] and size >= sizeFilter[0] \
                and date >= dateFilter[0] and date <= dateFilter[1] \
                    and re.search(nameFilter,name):
            return True
        else:
            return False


    

        
    # def insert_folder(self, treeParent, folderInfo):  
    #     if not folderInfo :
    #         return
    #     for node in folderInfo.sorted_nodes(sort_func=self.sort_func):
    #         tree_id = self.insertTreeviewItem(treeParent, node)
    #     pass
    
    
    # def filterOut(self, iid):
    #     # self.detachIids[iid] = self.dirTreeview.parent(iid)
    #     self.dirTreeview.detach(iid)
    #     pass
    
    # def _filterChildren(self, parent, filter):
    #     iids = {}
    #     for i in self.dirTreeview.get_children(parent):
    #         if  self._inFilter(i, filter)==0 :
    #             iids[i] = parent
    #         iids.update(self._filterChildren(i, filter))
    #     return iids
     
    # def _checkNoChild(self, parent, grandpa): 
    #     hasChild = False  #suppose have child    
    #     for i in self.dirTreeview.get_children(parent):
    #         hasChild = True
    #         self._checkNoChild(i, parent)
    #         if self.detachIids.get(i, None) == None: # if anyone not in detach keep it 
    #             return
    #     if hasChild:  # all children  in detach , remove  it 
    #         self.detachIids[parent] = grandpa