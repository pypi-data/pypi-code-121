from logging import root
import xml.etree.ElementTree as ET
import xmltodict
import copy

#几个对应点
# 1. data source的原始值key:value。该原始字典的keys为核心变量列表，该变量在get和set两个部分是核心变量。在获取xml信息中，提供keys列表去获取数据。 在get中，提供字典去设置值。
# 2. 核心变量对应的在字典中的位置。 key可以由核心变量+‘_path',赋值为一个list，里面包含从字典从外到内的keys
# 3. 核心变量对应的的data source的keys。 可以由核心变量+’_pairs‘,赋值为对应的excel的keys。  

class pdfformmodel(object):
    
    def __init__(self) -> None:
        self.xml_data={}
    
    def _getDict(self,data_dict,path):
        new_dict=data_dict
        for p in path:
            new_dict=new_dict[p]
        return new_dict
    
    #get info from xml, and not in excluded keys
    def _getItems(self,path,excluded_keys=None,pairs=None):
        rows=self._getDict(self.data_dict,path)
        temp_list=[]
        for row in rows:
            keys=[key for key in row.keys() if excluded_keys and key not in excluded_keys]
            # convert keys based on pairs
            temp_list.append({pairs.get(k):v for k,v in row.items() if pairs and k in keys})
        return temp_list
    
    # convert xml to dict
    def getXmlDict(self,source_xml):
        tree=ET.parse(source_xml)
        root=tree.getroot()
        xmlstr = ET.tostring(root, encoding='utf8', method='xml')
        data_dict = dict(xmltodict.parse(xmlstr))
        return data_dict
    
    # get xml info in excel source data format 
    def getXmlData(self,source_xml):
        self.data_dict=self.getXmlDict(source_xml)    
        
        #子类必须定义和paths的keys相对应的pairs，excludes keys。 此处应该根据paths的key，自动生成对应的变量名，并自动查找其需要的值
        for variable, path in self.paths.items(): #variable 是大类， path是其对应在form中keys chain的列表
            # variable_rows=self._getDict(self.data_dict,path)
            excluded_keys=self.excluded_keys.get(variable)
            pair=self.pairs.get(variable)
            self.xml_data[variable]=self._getItems(path,excluded_keys=excluded_keys,pairs=pair)

        return self.xml_data
    
    # fill xml template file with xml_data 
    def makeXml(self,template,output,context=None):
        context=context if context else self.xml_data
        # if len(self.xml_data)==0:
        #     raise ValueError('No data. Please getXmlData first...')
        o=[]
        with open(template) as x:
            s=x.read()
        out=''.join(s.format(**context))
        with open(output,'w')as w:
            w.write(out)
            print(f' {output} Saved')





