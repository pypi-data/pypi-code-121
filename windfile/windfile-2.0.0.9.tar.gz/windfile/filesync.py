'''
Created on 2018年1月14日

@author: heguofeng
'''

from windfile.filefolder import Folder,File,FFNode
from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import *

import unittest

from windfile.folder_ui import FolderWidgets

FILE_STATUS_UNKNOWN = 128
FILE_STATUS_NEW = 1
FILE_STATUS_OLD = 2 
FILE_STATUS_SAME = 4
STATUS_STRING = {
                FILE_STATUS_UNKNOWN:"?", \
                FILE_STATUS_NEW:">", \
                FILE_STATUS_OLD:"<", \
                FILE_STATUS_SAME:"=" }



class CompareWidgets(Frame):

    def __init__(self, master=None, cmpFun=None):
        super().__init__(master)
        self.compare = cmpFun
        self.createWidgets()
        self.iid2srcIid = {}
    
    def createWidgets(self):

        self.compareButton = Button(self, text="比较", command=self.compare)
        self.compareButton.grid(row=0, column=0)
        self.compareTreeview = Treeview(self, columns=("Status"), \
                                displaycolumns=["Status"], show='headings', height=16)
        self.compareTreeview.column('Status', width=20)
        self.compareTreeview.grid(row=1, column=0, rowspan=16, sticky=E + W)
        self.compareScrollbar = Scrollbar(self, orient=VERTICAL)
        self.compareScrollbar.grid(row=1, column=0, rowspan=16, sticky=N + S + E)
        
        self.compareScrollbar.configure(command=self.compareTreeview.yview)
        self.compareTreeview.configure(yscrollcommand=self.compareScrollbar.set)
        self.statusFilterCombobox = Combobox(self, \
                                             values=("All", ">>", '==', "<<", '??'), \
                                             width=6, \
                                             )
        self.statusFilterCombobox.set("All")
        self.statusFilterCombobox.grid(row=17, column=0, sticky=S)        
        
    def clearTreeview(self):
        for i in self.compareTreeview.get_children():
            self.compareTreeview.delete(i)
            
    def insertTreeviewItem(self, node):
        if not node:
            iid = self.compareTreeview.insert(parent="", index='end', values=(""))
        if isinstance(node, Folder):
            iid = self.compareTreeview.insert(parent="", index='end', values=(""))
            for n in node.sorted_nodes(sort_func=lambda x:x.name):
                self.insertTreeviewItem(n)
        if isinstance(node, File):
            iid = self.compareTreeview.insert(parent="", index='end', values=(node.status))
        return iid       
    
    def deleteTreeviewItem(self):
        pass        
    
    def refreshTreeview(self,folderInfo):
        self.clearTreeview()
        self.insertTreeviewItem(folderInfo)
        pass
    
            
class SynchronizeWidgets(Frame):
    '''
    widgets has directory label,directory entry,open file dialog button and directory view
    also has popupmenu 
    select event 
    '''

    def __init__(self, master=None, config={}):
        super().__init__(master)
        self.config = config
        self.compare_result_src = None
        self.compare_result_dst = None
        self.create_widgets()
        self.compareWidgets.statusFilterCombobox.bind("<<ComboboxSelected>>", self.filtersyncShow)
        self.srcFolderWidgets.sizeFilterCombobox.bind("<<ComboboxSelected>>", self.sizeDateFilterSyncShow)
        self.srcFolderWidgets.dateFilterCombobox.bind("<<ComboboxSelected>>", self.sizeDateFilterSyncShow)
        self.dstFolderWidgets.sizeFilterCombobox.bind("<<ComboboxSelected>>", self.sizeDateFilterSyncShow)
        self.dstFolderWidgets.dateFilterCombobox.bind("<<ComboboxSelected>>", self.sizeDateFilterSyncShow)
        self.srcIidDstIidDict = {}
        
    def create_widgets(self):

        self.srcFolderWidgets = FolderWidgets(self, folder_label="源始目录",config={"dupFinder":False})
        self.compareWidgets = CompareWidgets(self, self.compare)
        self.dstFolderWidgets = FolderWidgets(self, folder_label="目标目录",config={"dupFinder":False})

        self.srcFolderWidgets.syncButton = Button(self.srcFolderWidgets, text="同步", command=self.doSync)
        self.srcFolderWidgets.syncButton.grid(row=17, column=9)
        self.dstFolderWidgets.syncButton = Button(self.dstFolderWidgets, text="向左同步", command=self.doDst2SrcSync)
        self.dstFolderWidgets.syncButton.grid(row=17, column=0)  

        self.srcFolderWidgets.folderPath.set(self.config.get("last_source_path", "."))
        self.dstFolderWidgets.folderPath.set(self.config.get("last_destination_path", "."))
        
        self.srcFolderWidgets.grid(row=0, column=0, columnspan=5, rowspan=18, sticky=N + S + E + W)
        self.compareWidgets.grid(row=0, column=5, rowspan=17, sticky=N + S + E + W)        
        self.dstFolderWidgets.grid(row=0, column=6, columnspan=5, rowspan=18, sticky=N + S + E + W)
        
        self.srcFolderWidgets.columnconfigure(0, weight=5)    
        self.compareWidgets.columnconfigure(0, weight=1)
        self.dstFolderWidgets.columnconfigure(0, weight=5)   
                
        self.srcFolderWidgets.dirScrollbar.configure(command=self.syncScrollbar)
        self.dstFolderWidgets.dirScrollbar.configure(command=self.syncScrollbar)
        self.compareWidgets.compareScrollbar.configure(command=self.syncScrollbar)

    def syncScrollbar(self, mtype, howmuch, unit=""):
        if mtype == "moveto":
            self.srcFolderWidgets.dirTreeview.yview(mtype, howmuch)
            self.dstFolderWidgets.dirTreeview.yview(mtype, howmuch)
            self.compareWidgets.compareTreeview.yview(mtype, howmuch)
        else:
            self.srcFolderWidgets.dirTreeview.yview(mtype, howmuch, unit)
            self.dstFolderWidgets.dirTreeview.yview(mtype, howmuch, unit)
            self.compareWidgets.compareTreeview.yview(mtype, howmuch, unit)
       
        pass

   
    def sync_filter(self,node:FFNode,status):
        '''
    
        return: 
        '''
        if status == "All":
            return True
        elif  status == node.status:
            return True
        else:
            return False
  

    def filtersyncShow(self, event):
        status = self.compareWidgets.statusFilterCombobox.get()

        self.srcFolderWidgets.clearTreeview()
        self.dstFolderWidgets.clearTreeview()
        self.compareWidgets.clearTreeview()

        filted_folder_src = self.compare_result_src.filter(lambda x: self.sync_filter(x,status))
        filted_folder_dst = self.compare_result_dst.filter(lambda x: self.sync_filter(x,status))
        self.srcFolderWidgets.refreshTreeview(filted_folder_src)
        self.dstFolderWidgets.refreshTreeview(filted_folder_dst)
        self.compareWidgets.refreshTreeview(filted_folder_src)

        
    def sizeDateFilterSyncShow(self, event):
        status = self.compareWidgets.statusFilterCombobox.get()

        if event.widget == self.srcFolderWidgets.sizeFilterCombobox or event.widget == self.dstFolderWidgets.sizeFilterCombobox:
            s = event.widget.get()
            self.srcFolderWidgets.sizeFilterCombobox.set(s)
            self.dstFolderWidgets.sizeFilterCombobox.set(s)
        if event.widget == self.srcFolderWidgets.dateFilterCombobox or event.widget == self.dstFolderWidgets.dateFilterCombobox:
            s = event.widget.get()
            self.srcFolderWidgets.dateFilterCombobox.set(s)
            self.dstFolderWidgets.dateFilterCombobox.set(s)
        if event.widget == self.srcFolderWidgets.nameFilterEntry or event.widget == self.dstFolderWidgets.nameFilterEntry:
            s = event.widget.get()
            self.srcFolderWidgets.nameFilterEntry.set(s)
            self.dstFolderWidgets.nameFilterEntry.set(s)
        pass
    
        
    def doSync(self):
        filted_folder_src:FFNode = self.compare_result_src.filter(lambda x: self.sync_filter(x,">>"))
        filted_folder_dst:FFNode  = self.compare_result_dst.filter(lambda x: self.sync_filter(x,">>"))
        filted_folder_src.copyfiles(filted_folder_dst)
        self.dstFolderWidgets.folderInfo.load()
        self.compare()
        pass

    def doDst2SrcSync(self):
        filted_folder_src:FFNode = self.compare_result_src.filter(lambda x: self.sync_filter(x,"<<"))
        filted_folder_dst:FFNode  = self.compare_result_dst.filter(lambda x: self.sync_filter(x,"<<"))
        filted_folder_dst.copyfiles(filted_folder_src)
        self.srcFolderWidgets.folderInfo.load()
        self.compare()
        pass

    def compare(self):
        source =self.srcFolderWidgets.folderInfo
        dest = self.dstFolderWidgets.folderInfo
        self.compare_result_src,self.compare_result_dst = Folder.combine(source,dest)
        self.srcFolderWidgets.refreshTreeview(self.compare_result_src)
        self.dstFolderWidgets.refreshTreeview(self.compare_result_dst)
        self.compareWidgets.refreshTreeview(self.compare_result_src)
        pass


class Test(unittest.TestCase):

    def testName(self):
        pass


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
