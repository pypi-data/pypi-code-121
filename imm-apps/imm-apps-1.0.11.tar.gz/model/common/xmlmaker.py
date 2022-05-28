from abc import abstractclassmethod
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element,SubElement

"""     
1. 根据表格字典，构建所有节点
2. 根据excel数据，以及program定义的结构，将原始数据按照对应的数据字典的keys来拆分
3. switch数据字典，根据xpath，找到数据的key value，然后给xpath的元素赋值

"""
class XmlMaker(object):
    def __init__(self,model,root_tag:str,source_data):
        self.model=model
        self.source_data=source_data
        # 根据excel来的数据，改造model,成为直接匹配xml的格式。 
        # self.model=self.rebuild_model()
        # 构建树根
        self.root=ET.Element(root_tag)
        # 此处的paths是在已经重构的model下，所有的xpath都是绝对路径
        self.paths=self.getPaths()
        # 够条件xml树
        self.makeTree()
        #根据重构的model和source_data来赋值
        self.fill()
        
    # 不同的项目重写该方法。
    @abstractclassmethod
    def rebuild_model(self):
        raise NotImplementedError('rebuild_model method in class XmlMaker  not implemented...')
        
    def makeTree(self):
        for path_pairs in self.paths.values():
            for path in path_pairs.values():
                self.make_tree(self.root,path)
        
    def getPaths(self):
        path_model={}
        for key,value_pairs in self.model.items():
            path_model[key]={}
            for variable,path in value_pairs.items():
                path=path.split('/')
                path.reverse()
                path_model[key][variable]=path
        return path_model

    # 利用递归来构建无穷可能的树
    def make_tree(self,root,data:list):
        d=data.pop()
        parent=root
        new_element=parent.find(d)
        if isinstance(new_element,Element):
            parent=new_element
        else:
            parent=SubElement(parent,d)
        if len(data)>0:
            self.make_tree(parent,data)
        else:
            return 

    # fill xml tag text with value
    def fill(self):
        for sheet, xpath_pairs in self.model.items():
            for variable, xpath in xpath_pairs.items():
                s=self.root.find(xpath)
                s.text=str(self.source_data[sheet][variable])
    
    def write(self,output_xml_filename):
        tree = ET.ElementTree(self.root)
        tree.write(output_xml_filename)


