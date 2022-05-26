#!/Users/jacky/tools/venv/bin/python3.9
# coding=utf-8
# from pydantic import ValidationError
import json
from termcolor import colored
# from openpyxl import load_workbook, Workbook
import copy
from functools import total_ordering
from collections import OrderedDict


# info sheet data structure , in which 'variable','tag','description','value' are MUST.
class InfoNode(object):
    
    def __init__(self,*args,**kwargs) -> None:
        super().__init__()
        for k,v in kwargs.items():
            setattr(self,k,v)
    
    def __len__(self):
        return len(self.__dict__)
    
    #TODO: has same value. __eq__ only cares about has same schema, instead of values. So, has same value will compare value
    # def has_same_value(self,another):
    #     pass
    
    # Only care about variable and its value, if both same then True 
    def __eq__(self, another: object) -> bool:
        if another==None: 
            return False
        return True if self.variable==another.variable and self.value==another.value else False
    
    # + operator： if another has value, no matter self has value or not,  replace self’s value with another’s value, but if another has no value, keep self’s value. 
    def __add__(self,another:object):
        obj=copy.deepcopy(self)
        if obj.variable!=another.variable:
            raise TypeError(f'The two nodes ({obj.variable} {another.variable}) is different, can not add up')
        if another.value:
            obj.value=another.value
        return obj

    # - operator： if a node obj in self and in another, and if another has value, no matter self has value or not,  delete self’s node obj, but if another has no value, keep self’s node obj. 
    def __sub__(self,another:object):
        obj=copy.deepcopy(self)
        if obj.variable!=another.variable:
            raise TypeError(f'The two nodes ({obj.variable} {another.variable}) is different, can not minus ')
        if another.value:
            return None
        return obj
        
    def __hash__(self) -> int:
        return hash(self.variable+str(self.value))
    
    # return the variable name representing the object
    def __str__(self):
        return self.variable
    
    # return the string representing the class constructor method
    def __repr__(self):
        repr_str=[]
        for key, value in self.__dict__.items():
            repr_str.append('{} = "{}"'.format(key, value) ) if type(value)==str else repr_str.append('{} = {}'.format(key, value) )
        return f'InfoNode({",".join(repr_str)})'
    
# sheet data as a dict xx 
@total_ordering
class SheetDict(object):
    """[SheetDict class used for handle inside  of sheet and between of sheets level information]

    Args:
        2D list including three  rows of sheet title list, column title list, and variables list
        The data rows must include 'variable','tag','description', and 'value' four columns. 
        Other columns are optional. 

    Raises:
        StopIteration: [description]
        KeyError: ['description']

    Returns:
        SheetDict object
    """
    
    def __init__(self,rows) -> None:
        super().__init__()
        self.rows=rows
        self.sheet_title=self._getSheetTitle() # the first line is the sheet's title
        self.column_titles=self.rows.pop(0) # the second line is the display title
        variables=self._cleanTitles()
        # self.column_variables=[x and str(x).lower() for x in variables]# the third line in rows is this sheet's schema, used as title variables TODO: 不要小写？ 
        self.column_variables=[x and str(x) for x in variables]
        self.data=OrderedDict()  # contains the sheet's all variable and InfoNode objects ordered dict
        self._createInfoNodes(rows) #rows after poped three rows
        self.index=0
    
    def _getSheetTitle(self):
        st=self.rows.pop(0)
        st=st[0].split('\n')[0] if len(st)>0 else "A SheetDict object"
        return st
        
    def _cleanTitles(self):
        raw_variables=self.rows.pop(0)
        variables=[x for x in raw_variables if x!=None]
        if len(variables)<len(raw_variables): print(colored(f"There are some blank columns inside the info sheet {self.sheet_title}, you may delete those blank columns at the right of your visiable columns",'red'))
        return variables
        
    def __str__(self):
        return self.sheet_title
    
    # hash only care about variables and values
    def __hash__(self) -> int:
        return hash(','.join(['{} = {}'.format(key, value) for key, value in self.data.items()]))
    
    def __len__(self):
        return len(self.data)
    
    #TODO: has same value. __eq__ only cares about has same schema, instead of values. So, has same value will compare value
    def has_same_value(self,another):
        pass
    
    # define sheet data's collection methods, + -  == > < All this operations do not consider value. They only compare sheet variables
    # == return True if self and another has same variables. Only care about variables
    def __eq__(self, another: object) -> bool:
        if another==None: 
            return False
        if self is None:
            return False
        if self.data.keys()!=another.data.keys(): return False 
        # for k, v in self.data.items():
        #     if v.value != another.data[k].value: return False
        return True 
    
    # > return True if every another object's items is in self, and the length of self is greater than the other's
    def __gt__(self,another:object)->bool:
        flags=[]
        for variable in another.data:
            flags.append(True) if variable in self.data else flags.append(False)
        flags.append(len(self)>len(another))
        return all(flags)  
    
    # + union two sets (self | another), and return a new set
    def __add__(self,another:object):
        obj=copy.deepcopy(self) #deep copy self to obj, to avoid messing up self object
        # iterate another and insert or replace self's：
        for variable in another.data:
            if variable not in self.data:   #if node is not in self, add another’s node in self’s. 
                obj.data[another.data[variable].variable]=another.data[variable]
            else:   #if node is in self, add up two nodes. 
                obj.data[variable]+=another.data[variable]
            
        return obj
    
    # - set difference, return a new set with elements in self but not in another
    def __sub__(self,another:object):
        obj=copy.deepcopy(self) #deep copy self to obj, to avoid messing up self object
        for variable in self.data:
            # self and another are in same sheet name，sub the variables in self if it's in the another 
            if variable in another.data and another.data[variable].value:
                obj.data.pop(variable,None)
                # obj.data[variable]-=another.data[variable]
            # obj.data=[obj.data[x] for x in obj.data if x!=None]
        return obj
    
    # in: return True if self contains another, else False
    def __contains__(self,another:object):
        # if every another object's items is in self, then return True;
        flags=[]
        for variable in another.data:
            flags.append(True) if variable in self.data else flags.append(False)
        return all(flags)
    
    # Iterator
    def __iter__(self):
        return self

    def __next__(self):
        try:
            item = list(self.data.values())[self.index]
        except IndexError:
            raise StopIteration()
        self.index += 1
        return item
    
    def _createInfoNodes(self,rows):
        if len(rows)==0:
            self.data={}
        for row in rows:
            row_data=OrderedDict(zip(self.column_variables,row)) # zip and make data as a dict
            v=row_data.get('variable')  # get the variable as key
            self.data[v]=InfoNode(**row_data) # create a InfoNode object
            
    def showInfoNodes(self,seperator=','):
        for variable in self.data.values():
            info=[info for info in variable.__dict__.values()]
            info=[ i if i is not None else '' for i in info] #avoid None
            print(seperator.join(info))
    
    # This method returns all info variables or specific info notes specified in program    
    def getInfoNodes(self,program=None):
        if program:
            if program not in self.column_variables:
                raise KeyError(f'{program} is not a valid column name')
            # if a progam marked any word first letter is Y/y, it will be True, otherwise, it will be False
            return {k:v for k,v in self.data.items() if  getattr(v,program)!= None and getattr(v,program)[0].upper()=='Y'}
        return {k:v for k,v in self.data.items()}

    # get common variables in self and another, and return a new object
    def common(self,another: object):
        obj=copy.deepcopy(self) #deep copy self to obj, to avoid messing up self object
        # get two dicts' intersection set
        common_variables=set(self.data.keys()) & set(another.data.keys())
        for variable in self.data:
            if variable not in common_variables: 
                obj.data.pop(variable,None)
        return obj
    
    # copy: if self and another has common variables, then copy the value of another's shared variable to self 
    def copy(self,another):
        obj=copy.deepcopy(self)
        for k,v in another.data.items():
            if k in obj.data.keys(): obj.data[k]=v
        return obj




