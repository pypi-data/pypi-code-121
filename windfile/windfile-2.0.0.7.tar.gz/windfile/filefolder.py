# coding=utf-8 
'''
Created on 2018年1月13日

@author: heguofeng
'''

import hashlib
import os
from _stat import S_ISDIR, S_ISREG
import platform
import shutil
import traceback
import unittest
import logging
from windbase import Tools

# IMPORTANCE!!!!!
# THis is example how to change class method  or add new attribute
# 
# def getfiles(self,folder):
#     for node in self.nodes.values():
#         if node.ntype=="file":
#             node.real_path=node.fullpath
#             folder.add_node(node)
#         if node.ntype == "folder":
#             node.getfiles(folder)
#     return folder

# Folder.getfiles = getfiles

# @property
# def fullpath(self):
    
#     return self.real_path if hasattr(self,"real_path") else os.path.join(self.parent_path,self.name)

# FFNode.fullpath = fullpath

class FFNode(object):
    def __init__(self,parent=None,name=None,stat=None) -> None:
        self.name = name
        self.parent = parent
        self.status = ""
        self.ui_id = None
        if stat:
            self._set_stat(stat)
        else:
            pass
        pass
    
    @property
    def fullpath(self):
        return os.path.join(self.parent_path,self.name)

    @property
    def parent_path(self):
        path = ""
        folder = self.parent
        while folder:
            path = os.path.join(folder.name,path)
            folder = folder.parent
        sys = platform.system()
        if sys == "Windows":
            path = path.replace("/","\\")
        return path
    
    def set_status(self,status):
        self.status=status
        return self


    def __str__(self):
        return "todo"

    def __eq__(self, other):
        if self.ntype == other.ntype:
            if self.size == other.size and self.mtime == other.mtime:
                return True
        else:
            return False

    def _set_stat(self, stat_result):
        if stat_result != None:
            if S_ISREG(stat_result.st_mode):
                self.ntype = "file"
            elif S_ISDIR(stat_result.st_mode):
                self.ntype = "folder"
            else:
                raise Exception("Not a regular object!")
            self.size = stat_result.st_size
            self.mtime = int(stat_result.st_mtime)

    def load(self,fullpath:str=None):
        real_fullpath = fullpath if fullpath else self.fullpath
        path,name = os.path.split(real_fullpath)
        stat_result = os.stat(real_fullpath)
        self._set_stat(stat_result)
        if self.ntype == "file":
            if (not self.parent) and path:
                self.name = name
                self.parent = Folder(None,path)
        else: # folder
            if (not self.parent) and path:
                self.name = real_fullpath
        return self

    def remove(self):
        if self.ntype == "file":
            os.remove(self.fullpath)  # remove the file
        if self.ntype == "folder":
            for node in list(self.nodes.keys()):
                self.nodes[node].remove()
            os.rmdir(self.fullpath)  # remove the path
        if self.parent:
            self.parent.nodes.pop(self.name)
            self.ui_id = ""
            del self
        return 

    def filter(self,filter_func=None):
        return True

    def clone(self,parent=None,status="hidden"):
        if isinstance(self,File):
            node = File(parent=parent,name=self.name)
        if isinstance(self,Folder):
            node = Folder(parent=parent,name=self.name)
        node.status = status
        return node

    @staticmethod
    def count_nodes(nodes:list):
        count = (0,0,0)
        for node in nodes:
            count = tuple(i+j for i,j in zip(count,node.count(recursive=False)))
        return count

    def compare(self,other):
        '''
        compare two node , 
        == 
        ??  unknown
        >>  self is new
        <<  self is old
        !!  not same name 
        xx  not same type

        Args:
            other (_type_): _description_

        Returns:
            _type_: [(self.ui_id,other.ui_id,result)]
        '''
        if self.ntype == other.ntype:
            if self.name == other.name:
                if self.mtime == other.mtime or self.ntype == "folder":
                    if self.size == other.size or self.ntype == "folder":
                        result = "=="
                    else:
                        result = "??"
                else:
                    result = "<<" if self.mtime < other.mtime else ">>"
            else:
                result = "!!"
        else:
            result = "xx"  
        return result


class File(FFNode):
    def __init__(self, parent=None, name=None, stat=None,size=0,mtime=0,md5=None) -> None:
        self.ntype = "file"
        self.size = size
        self.mtime = mtime
        self.md5value = md5
        super().__init__(parent,name,stat)

    
    def __str__(self):
        return "File: %s %s size=%d mtime=%d" % (self.parent_path, self.name, self.size, self.mtime)

    
    def load(self,fullpath:str=None):
        super().load(fullpath)
        if self.ntype == "file":
            return self
        else:
            raise Exception("Not a file!")
  

    def filter(self,filter_func=None):
        if (not filter_func) or filter_func(self):
            return self
        return None

    def copyfile(self,destnode):
        shutil.copy2(self.fullpath, destnode.fullpath)
        destnode.load()

    def copy2path(self,destpath):
        shutil.copy2(self.fullpath, os.path.join(destpath,self.name))

    def count(self,recursive=True):
        return 0,1,self.size

    @property
    def md5(self):
        if self.md5value:
            return self.md5value
        with open(self.fullpath, 'rb') as f:
            md5obj = hashlib.md5()
            md5obj.update(f.read())
            self.md5value = md5obj.hexdigest()
        return self.md5value



class Folder(FFNode):
    max_depth = 10
    max_nodes = 1000
    @classmethod
    def set_max(cls,max_depth=10,max_nodes=1000):
        cls.max_depth = max_depth
        cls.max_nodes = max_nodes

    def __init__(self,parent=None, name=None, nodes=None,depth=0) -> None:
        self.ntype = "folder"
        self.nodes = nodes if nodes else {}
        super().__init__(parent,name)

    def __str__(self):
        result = "Folder:%s %s %d nodes\n    " % (self.parent_path, self.name,len(self.nodes))
        for node in self.nodes.values():
            result += node.__str__()+"\n    "
        return result

    def load(self,fullpath:str=None,depth:int=0):
        super().load(fullpath)
        if self.ntype == "folder":
            node_count = 0
            for f in os.listdir(self.fullpath):
                node_count += 1
                if node_count> Folder.max_nodes:
                    self.nodes[f] = File(self,"~Exceed the maximum nodes!")
                    break
                f_full_path = os.path.join(self.fullpath, f)
                try:
                    stat_result = os.stat(f_full_path)
                    if S_ISREG(stat_result.st_mode):
                        self.nodes[f] = File(self,f,stat_result)
                    if S_ISDIR(stat_result.st_mode):
                        if depth <= Folder.max_depth:
                            self.nodes[f] = Folder(self,f).load(depth=depth+1)
                        else:
                            self.nodes[f] = Folder(self,"~Exceed the maximum depth of folder!")
                except:
                    logging.warning(traceback.format_exc())
            return self
        else:
            raise Exception("Not a folder!")


    def filter(self,filter_func=None):
        '''
        filter_func(node):
            
        '''
        if not filter_func:
            return self

        filted_info=Folder(self.parent,self.name)
        
        for node in self.nodes.values():
            if node.ntype=="folder":
                child_filted_node = node.filter(filter_func)
                if len(child_filted_node.nodes):
                    filted_info.add_node(child_filted_node)
            if node.ntype=="file":
                if node.filter(filter_func):
                    filted_info.add_node(node)
        return filted_info

    def add_node(self,node):
        self.nodes[node.name]=node
        node.parent = self
        return self   

    def delete_node(self,node):
        return self.nodes.pop(node.name,None)    

    def getfiles(self,folder):
        for node in self.nodes.values():
            if node.ntype=="file":
                folder.add_node(node)
            if node.ntype == "folder":
                node.getfiles(folder)
        return folder

    def sorted_nodes(self,sort_func = lambda x:x.name):
        node_list = list(self.nodes.values())
        node_list.sort(key=sort_func)
        return node_list
        return list(self.nodes.values()).sort(key=sort_func)


    @staticmethod
    def combine(my,other,mode="same"):
        table={"reverse": {"==":"==","<<":">>",">>":"<<","??":"??"},
                "same":{"==":"==","<<":"<<",">>":">>","??":"??"}}
        combine_dict = {}
        src_folder = Folder(my.parent,my.name)
        dst_folder = Folder(other.parent,other.name)
        for name in my.nodes.keys():
            combine_dict[name]= 1
        for name in other.nodes.keys():
            combine_dict[name]= combine_dict.get(name,0) + 2
        for name,value in combine_dict.items():
            if value==1:
                status = ">>"
                src_node = my.nodes.get(name)
                dst_node = src_node.clone(parent=dst_folder)
            if value==2:
                status = "<<"
                dst_node = other.nodes.get(name)
                src_node = dst_node.clone(parent=dst_folder)
            if value==3:
                src_node = my.nodes.get(name)
                dst_node = other.nodes.get(name)
                status = src_node.compare(dst_node)
            src_node.status = status
            dst_node.status = table[mode][status]
            src_folder.add_node(src_node)
            dst_folder.add_node(dst_node)
            if src_node.ntype=="folder":
                r_src,r_dst = Folder.combine(src_node,dst_node)
                src_folder.add_node(r_src)
                dst_folder.add_node(r_dst)
        return src_folder,dst_folder

    def copyfiles(self,dest):
        for node in self.nodes.values():
            dest_node:FFNode= dest.nodes.get(node.name,None)
            if not dest_node:
                continue
            if dest_node.ntype=="file":
                node.copyfile(dest_node)
            if dest_node.ntype=="folder":
                self.copy2path(dest_node.fullpath)
                node.copyfiles(dest_node)
        return 

    def copy2path(self,destpath):
        if not os.path.exists(destpath):
            os.mkdir(destpath)

    def count(self,recursive=True):
        filecount = 0
        dircount = 1
        sizecount = 0
        # count_folder  = folder if folder else self
        if recursive:
            for node in self.nodes.values():
                dc,fc,sc = node.count()
                dircount += dc
                filecount += fc
                sizecount += sc
        return dircount, filecount, sizecount




           
class Test(unittest.TestCase):


    def setUp(self):
        Tools.set_debug(logging.DEBUG,"")
        
        pass        


    def tearDown(self):

        pass

    def testFilter(self):
        folderinfo = Folder(name=r"D:\Download\sase\Scripts").load()
        print(folderinfo)
        filted_info = folderinfo.filter(filter_func=lambda node:True if node.name.startswith("s") else False)
        print(filted_info)

        

if __name__ == "__main__":
    unittest.main()
