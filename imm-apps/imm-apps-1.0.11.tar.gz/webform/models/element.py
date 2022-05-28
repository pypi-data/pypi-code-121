from cProfile import label
from enum import Enum
from pydantic import BaseModel
from abc import ABC,abstractmethod
from typing import Union,Optional
from models.definition import Action
from dotenv import dotenv_values


class Element(ABC,BaseModel):
    action_type:str
    id:Optional[str]
    
    @abstractmethod
    def make(self):
        pass

class InputElement(Element):
    label:str
    value:str
    length:Optional[int]
    required:Optional[bool]
    disabled:Optional[bool]
    
    def make(self):
        return {
            'action_type':self.action_type,
            "label":self.label,
            "id":self.id,
            "value":self.value,
            "length":self.length,
            "required":self.required,
            "disabled":self.disabled
        }


class AreatextElement(InputElement):
    pass

class SelectElement(Element):
    label:str
    value:str
    
    def make(self):
        return {
            'action_type':self.action_type,
            "label":self.label,
            "id":self.id,
            "value":self.value
        }

class CheckboxElement(Element):
    label:str
    def make(self):
        return {
            'action_type':self.action_type,
            'label':self.label,
            'id':self.id
        }

# Radio element 
# class RadioElement(Element):
#     group_label:str
#     id:str
#     id_label:str
#     value: bool
#     children:Union[list,None]


# Yes/No radio element
class RadioYesNoElement(Element):
    yes_id:str
    no_id:str
    value: bool
    def make(self):
        return {
            "action_type":self.action_type,
            "id": self.yes_id if self.value else self.no_id,
            "label":"Yes" if self.value else "No"
        }

# Yes/No/null radio element
class RadioYesNoNullElement(Element):
    yes_id:str
    no_id:str
    null_id:str
    value: Union[bool,None]
    def make(self):
        match self.value:
            case True:
                id_label="Yes";
                new_id=self.yes_id;
            case False:
                id_label="No";
                new_id=self.no_id;
            case None:
                id_label="Not Applicable";
                new_id=self.null_id;
        return {
            "action_type":self.action_type,
            "id":new_id,
            "label":id_label,
        }

class ButtonElement(Element):
    label:str
    id:str
    # children:Union[list,None]
    
    def make(self):
        return {
            'action_type':self.action_type,
            "label":self.label,
            "id":self.id
        }

class TurnPage(Element):
    label:str
    def make(self):
        return {
            "action_type":Action.Turnpage.value,
            "label":self.label,
            "id":self.id
    }


class LoginElement(Element):
    rcic:str
    portal:str
    account_element_id:str
    password_element_id: str
    login_button_id:str
    success_element_id:str

    def make(self):
        config = dotenv_values(".env")
        account_key=self.rcic.upper()+"_"+self.portal.upper()+"_ACCOUNT"
        password_key=self.rcic.upper()+"_"+self.portal.upper()+"_PASSWORD"
        return {
            'action_type':self.action_type,
            "account": config.get(account_key),
            "password": config.get(password_key),   #TODO: 后续需要考虑加密，然后在js中解密
            "account_element_id":self.account_element_id,
            "password_element_id": self.password_element_id,
            "login_button_id":self.login_button_id
        }

class SecurityElement(Element):
    question_element_id: str
    answer_element_id: str
    continue_element_id: str
    success_element_id: str
    security_answers:dict
    
    def make(self):
        return {
            'action_type':self.action_type,
            "question_element_id":self.question_element_id,
            "answer_element_id": self.answer_element_id,
            "continue_element_id": self.continue_element_id,
            "success_element_id": self.success_element_id,
            "security_answers":self.security_answers
        }

class DependantSelectElement(Element):
    select1:SelectElement
    select2:SelectElement
    def make(self):
        return {
            "action_type":self.action_type,
            "select1":self.select1,
            "select2":self.select2
        }
