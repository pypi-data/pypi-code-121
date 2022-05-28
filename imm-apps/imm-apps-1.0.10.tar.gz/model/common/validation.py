from pydantic import ValidationError
from termcolor import colored
import json

class Validation(object):
    def __init__(self,validator_model,excel_name,sheet) -> None:
        self.validate_pair=validator_model.validate_pair
        self.excel_name=excel_name
        self.sheet_name=sheet.name
        self.sheet=sheet
        self.validated_data=None
    @property
    def json(self):
        return json.dumps(self.validated_data,indent=3,default=str)
        
class SheetValidation(Validation):
    """SheetValidation validate a sheet object, and return validated data from validated_data dict

    Args:
        validator_model: A pydandic model, in which must have a validate_pair dict used for pointing the processing class 
        excel_name: an excel file
        sheet: a sheet object (SheetDict object)
    """
    def __init__(self,validator_model,excel_name,sheet):
        super().__init__(validator_model,excel_name,sheet)
        self.validated_data={}
        self.validate()
        
    def interpretError(self,e:ValidationError):
        print(colored(f"Erros in file {self.excel_name}-> info-{self.sheet_name} sheet",'red'))
        for err in e.errors():
            for variable in err['loc']:
                info_node=self.sheet.data.get(variable)
                if info_node !=None: 
                    print(colored(f"{info_node.description}",'green'),err['msg'],err['type'].replace('.',': '))
            
    def validate(self):
        try:
            # get data from sheet object
            data={variable: info_node_obj.value for variable, info_node_obj in self.sheet.data.items()}
            validatedData=(self.validate_pair[self.sheet_name](**data))
            self.validated_data = validatedData.dict()
        except ValidationError as e:
            self.interpretError(e)
    

class TableValidation(Validation):
    """TableValidation validate a table object, and return validated data from validated_data list

    Args:
        validator_model: A pydandic model, in which must have a validate_pair dict used for pointing the processing class 
        excel_name: an excel file
        sheet: a table object (TableDict object)
    """
    def __init__(self,validator_model,excel_name,sheet) -> None:
        super().__init__(validator_model,excel_name,sheet)
        self.validated_data=[]
        self.row_index=0
        self.validate()
            
    def interpretError(self,e:ValidationError):
        print(colored(f"Erros in file {self.excel_name}-> table-{self.sheet_name} sheet",'red'))
        for err in e.errors():
            for variable in err['loc']:
                index=self.sheet.column_variables.index(variable)
                variable_title=self.sheet.column_titles[index]
                print(colored(f"Row {self.row_index+4}: ",'red'),colored(f"{variable_title}",'green'),err['msg'],err['type'].replace('.',': '))
    
    def validate(self):
        try:
            for dataItem in self.sheet.data:
                validatedData=(self.validate_pair[self.sheet_name](**dataItem.__dict__))
                self.validated_data.append(validatedData.dict())
                self.row_index+=1
        except ValidationError as e:
            self.interpretError(e)
