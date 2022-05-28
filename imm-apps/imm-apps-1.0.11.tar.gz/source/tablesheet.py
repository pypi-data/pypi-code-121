#!/Users/jacky/tools/venv/bin/python3.9
import json
import copy
from functools import total_ordering
from collections import OrderedDict
from termcolor import colored


class TableNode(object):
    
    def __init__(self,*args,**kwargs) -> None:
        super().__init__()
        for k,v in kwargs.items():
            setattr(self,k,v)
        
        
    def __len__(self):
        return len(self.__dict__)
    
    # return True if every key and value is same and with same length
    def __eq__(self, another: object) -> bool:
        if len(self) != len(another): return False
        for p in self.__dict__: # check every property's value is same
            if self.__dict__.get(p) != another.__dict__.get(p): return False 
        return True     
    
    # Return True if self and another has top three values in same, which we regard they are some record
    # The purpose of doing so is to check if two records are actually same, so has to be merged.
    def is_same_record(self, another: object):
        obj=copy.deepcopy(self)
        try:
            top_three=list(obj.__dict__)[0:3]
        except:
            raise IndexError(f'{self} has less than 3 columns')
        for property in top_three:
            if getattr(obj,property) !=getattr(another,property): 
                return False
        return True 
    
    # + operator： if another has value, no matter self has value or not,  replace self’s value with another’s value, but if another has no value, keep self’s value. 
    def __add__(self,another:object):
        obj=copy.deepcopy(self)
        # 相同变量部分：搜索another每一个值，如果不为空，就替代self。 
        # 不同变量部分，another多出来的部分,增加变量和值到self。
        for p in another.__dict__:
            if p in self.__dict__:
                # If another has value, no matter self has value or not,  replace self’s value with another’s value
                if getattr(another,p,None): 
                    setattr(obj,p,getattr(another,p))
                # but if another has no value, keep self’s value. 
            else:
                # if a property in another but not in self, add it to self 
                setattr(obj,p,getattr(another,p,None))
                
        return obj
        
    # copy:  if another has value, no matter self has value or not,  replace self’s value with another’s value
    def copy(self,another:object):
        obj=copy.deepcopy(self)
        # 相同变量部分：搜索another每一个值，替代self。 
        for p in another.__dict__:
            if p in self.__dict__ : setattr(obj,p,getattr(another,p))
        return obj
        
    def __hash__(self) -> int:
        hs=[]
        for key, value in self.__dict__.items():
            hs.append('{} = {}'.format(key, value))
        return hash(','.join(hs))
    
    # return the variable name representing the object
    def __str__(self):
        str_str=['{}:{}'.format(key, value) for key, value in self.__dict__.items()]
        return ', '.join(str_str)
    
    # return the string representing the class constructor method
    def __repr__(self):
        repr_str=['{} = "{}"'.format(key, value)  if type(value)==str else '{} = {}'.format(key, value) for key, value in self.__dict__.items()]
        return f'TableNode({",".join(repr_str)})'
    
    # return True or False representing node is null or not null. 
    # null means the infoNode has no any value, reflecting in excel is a blank row
    def __bool__(self):
        return any(self.__dict__.values())

# sheet data as a dict xx 
@total_ordering
class TableList(object):
    """[TableList class used for handle inside  of table sheet and between of table sheets level information]

    Args:
        2D list including three  rows of sheet title list, column title list, and variables list
        columns are defined by excel files. 

    Raises:
        StopIteration: [description]
        KeyError: ['description']

    Returns:
        TableList object
    """    
    def __init__(self,rows) -> None:
        super().__init__()
        self.rows=rows
        self.sheet_title=self._getSheetTitle() # the first line is the sheet's title
        self.column_titles=self.rows.pop(0) # the second line is the display title
        # self.column_variables=[self._title2variable(x) for x in variables]# the third line in rows is this sheet's schema, used as title variables
        self.column_variables=self._cleanTitles()
        self.column_titles=OrderedDict(zip(self.column_variables,self.column_titles)) #绑定title到variable，否则在后续+ - table的时候，title和variable 以及value可能无法保持一致。 
        self.rows=rows  # data rows
        self.data=[]  # contains the sheet's all TableNode objects
        self.createTableNodes(rows) #rows after poped three rows
        self.index=0
    
    def _getSheetTitle(self):
        st=self.rows.pop(0)
        st=st[0].split('\n')[0] if len(st)>0 else "A TableList object"
        return st
    
    def _cleanTitles(self):
        raw_variables=self.rows.pop(0)
        variables=[x for x in raw_variables if x!=None]
        if len(variables)<len(raw_variables): print(colored(f"There are some blank columns inside the table sheet {self.sheet_title}, you may delete those blank columns at the right of your visiable columns",'red'))
        return variables
    
    # TODO: convert?
    def _title2variable(self,title):
        return title.lower().replace(' ','_')
    #TODO: ?
    def _variable2title(self,variable):
        return variable.replace('_',' ').title()
    
    def __str__(self):
        return self.sheet_title
    
    # hash only care about variables and values
    def __hash__(self) -> int:
        return hash(','.join([node for node in self.data]))
    
    def __len__(self):
        return len(self.data)
    
    #TODO: has same value. __eq__ only cares about has same schema, instead of values. So, has same value will compare value
    def has_same_value(self,another):
        pass
    
    # == > < All this operations do not consider value. They only compare sheet variables
    # == return True if self and another has same variables. Only care about variables
    def __eq__(self, another: object) -> bool:
        # check if sheet has same column variables, which means same data structure
        if another==None: return False
        if self.data==[] and another==[]: return True
        if self.column_variables!=another.column_variables: return False 
        return True 
    
    # # > return True if every another object's items is in self, and the length of self is greater than the other's
    def __gt__(self,another:object)->bool:
        flags=[]
        for variable in another.column_variables:
            flags.append(True) if variable in self.column_variables else flags.append(False)
        flags.append(len(self.column_variables)>len(another.column_variables))
        return all(flags)  
    
    # + union two objects (self | another)'s two lists(column_titles, column_variables), and return a new object
    def __add__(self,another:object):
        obj=copy.deepcopy(self) #deep copy self to obj, to avoid messing up self object
        # get titles united. list the OrderedDict union result for remove duplication 
        # get variables
        obj.column_variables=list(OrderedDict.fromkeys(self.column_variables+another.column_variables)) #字典keys相加去重复
        titles=[self.column_titles.get(v) or another.column_titles.get(v) for v in obj.column_variables] # get new set of titles
        obj.column_titles=OrderedDict(zip(obj.column_variables,titles)) # re-bind to new set of variables
        another.column_titles,another.column_variables= obj.column_titles, obj.column_variables #让another和obj一样的titles和variables
        
        # expand obj and another to the new union. As a result, they will be in same number of columns
        for o in obj.data:
            for p in obj.column_variables:
                if not getattr(o,p,None): # if the property has no value, set the property as None.
                    setattr(o,p,None)
                    
        for o in another.data:
            for p in another.column_variables: # here obj.column_variables are expaned.
                if not getattr(o,p,None):
                    setattr(o,p,None)

        # Now self and another are in same dimension in columns。 
        temp_data=[]
        for node_obj in obj.data: # 对每一个obj里面的数据 去寻找是否和another里面的是相同记录
            for node_another in another.data:
                if node_obj.is_same_record(node_another): # if same record
                    node_obj+=another.data.pop(another.data.index(node_another)) # pop up the same one and merge
                    temp_data.append(node_obj) #将merge过的记录添加到临时list中
                else:   
                    if node_obj not in temp_data:   #如果不是同一条记录，而且在临时列表中没有，添加，
                        temp_data.append(node_obj) 

        obj.data=temp_data+another.data # append all different rows to obj.data。 
        #此事obj。data数据都有了，但是order有可能发生改变，所以下面需要对obj的data进行重构，以variables的顺序作为统一标准。        
        # 根据obj.data中node的variable排序，重新构建obj。
        new_data=[]
        for d in obj.data:
            values=[getattr(d,p,None) for p in obj.column_variables] #以variable取出对应的value
            pair=OrderedDict(zip(obj.column_variables,values))  #zip variable和value，编程有序字典
            new_data.append(TableNode(**pair)) #重新构建TableNode obj到临时data列表
        obj.data=new_data       
        return obj
    
    # - operator: 1st: minus only allowed if self and another have same column schema(same variables). 2st, if top 3 variables are same, the row will be removed
    def __sub__(self,another:object):
        obj=copy.deepcopy(self) #deep copy self to obj, to avoid messing up self object
        # check if has same column schema, if not raise an error
        if self.column_variables!=another.column_variables:
            raise ValueError(f"{self.column_titles} is not same as {another.column_variables}, so could not minus")
        # check for same row, if yes, remove it
        for obj_node in self.data: # use self.data because obj.data is changing...
            for another_node in another.data:
                if obj_node.is_same_record(another_node):
                    obj.data.pop(obj.data.index(obj_node))
        
        return obj
    
    # in: return True if self's variables contains another's
    def __contain__(self,another: object):
        for x in another.column_variables:
            if x not in self.column_variables: return False
        return True 
    
    def createTableNodes(self,rows):
        for row in rows:
            row_data=OrderedDict(zip(self.column_variables,row)) # zip and make data as a dict
            self.data.append(TableNode(**row_data)) # create a InfoNode object
            
    def showTableNodes(self,seperator=','):
        for row in self.data:
            info=[info for info in row.__dict__.values()]
            info=[ str(i) if i is not None else '' for i in info] #avoid None
            print(seperator.join(info))
    
    
    def copy(self,another: object):
        obj=copy.deepcopy(self)
        # for some tables, has to be specially processed
        if another.name in ["personid","address","phone","eraddress","contact"]:
            # loop another.data
            for ad in another.data:
                # loop obj.data
                for index,od in enumerate(obj.data): 
                    # if another.data's variable ==obj.data's variable_type, then copy
                    if ad.variable_type==od.variable_type and ad.display_type==od.display_type: # using display_type is only for working_address, which has multiple value in er.xlsx
                        obj.data[index]=od.copy(ad)
                        break
            return obj
        #for general tables
        for ad in another.data:
            # if has same schema
            if self.column_variables==another.column_variables:
                # if another not in original one, just append another's rows to original one.
                if ad not in obj.data: obj.data.append(ad)
            # if has different schema
            else:
                # get self's column variable,and get value from another, then make a TableNode object and insert to self.data
                kwargs={}
                for key in obj.column_variables:
                    kwargs[key]=getattr(ad,key,None)
                copied_obj=TableNode(**kwargs)
                obj.data.append(copied_obj)
        return obj
    
    #get common variables in self and another, and return new object
    def common(self,another: object):
        obj=copy.deepcopy(self)
        # get titles united. list the OrderedDict union result for remove duplication 
        obj.column_titles=[{k:v} for k,v in self.column_titles.items() if k in another.column_titles.keys()]
        # get variables
        obj.column_variables=[x for x in self.column_variables if x in another.column_variables]
        #get values
        obj.data=[x for x in self.data if x in another.data]
        return obj
        
    # Iterator
    def __iter__(self):
        return self

    def __next__(self):
        try:
            item = self.data[self.index]
        except IndexError:
            raise StopIteration()
        self.index += 1
        return item
        
