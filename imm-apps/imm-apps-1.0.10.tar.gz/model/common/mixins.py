from functools import reduce
from pydantic import validator
from datetime import date
from model.common.utils import Duration

# Compare if self obj and another obj is same with compare all property and its value
class EqMixin(object):
    def __eq__(self,another):
        for k,v in self.__dict__.items():
            if v != getattr(another,k,None):
                return False
        return True

class KwargsMixin(object):
    def _getInput(self,global_dict,excel_obj):
        """
        Prerequisite of this mixin
        1. excel_obj is the one that all input excels combined, no sheet has same name
        2. Final level model is constructed with all sheets/tables, no specific single varialbe
        3. Only InfoSheet and TableList two data structure in the final level model
        """
        input_kwargs={}
        # According to the prerequisite described above, all the referrenced scheme are defined in 'definitions'. 
        # key is Model name, and after lower(), it is also excel sheet name and the property defined in this class. They are same. This is the requirement.
        for k in self.schema()['definitions'].keys(): 
            # globals() returns a dict inlcuding all global classes, methods, ....
            klass=global_dict.get(k)  
            # use k.lower (it's a sheet name here) to get sheet data
            sheet_data=excel_obj.dict.get(k.lower(),None)   
            # only two types, one is list of model objects,another is model object
            if not isinstance(sheet_data,list):
                # assign the input kwargs. Here k.lower() is class's property. klass is the model, on which the app create an obj
                input_kwargs[k.lower()]=klass(**sheet_data)
            else:
                input_kwargs[k.lower()]=[klass(**d) for d in sheet_data]
        return input_kwargs

class MakeExcelMixin(object):
    def _generateExcel(self,global_dict,excel_obj,excel_file):    
        sheets=[]
        tables=[]
        # 获得每一sheet对应class，并获得它的properties list
        for k in self.schema()['definitions'].keys(): 
            # globals() returns a dict inlcuding all global classes, methods, ....
            klass=global_dict.get(k) #get the class
            variables=list(klass.__fields__.keys()) # get all variables in the shhet or table
            sheet_table_name=k.lower() # k.lower is the sheet / table name according to convention
            if 'info-'+sheet_table_name in excel_obj.sheet_names:
                sheets.append(excel_obj.getSheet(sheet_table_name,variables)) # get sheet object 
            if 'table-'+sheet_table_name in excel_obj.table_names:
                tables.append(excel_obj.getTable(sheet_table_name,variables)) # get table object
                
        # 根据最终更新了variables的sheets和talbes，生成新的excel文件
        excel_obj.makeExcel(excel_file,sheets=sheets,tables=tables)

# 处理所包含start_date 和 end_date的记录。 
class DurationMixin(object):
    @property
    def start_from(self):
        return self.start_date.strftime('%b %Y')

    @property
    def end_to(self):
        return self.end_date.strftime('%b %Y') if self.end_date else "Present"
    
    @property
    def lengthOfYears(self):
        return Duration(self.start_date,self.end_date).years
    