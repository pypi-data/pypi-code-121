from pydantic import BaseModel
from typing import Optional,List,Union
from collections import namedtuple


class LanguageBase(BaseModel):
    reading:Optional[Union[int,float]]
    writting:Optional[Union[int,float]]
    listening:Optional[Union[int,float]]
    speaking:Optional[Union[int,float]]
    test_type:Optional[str]
    
    
    def __str__(self):
        return str(self.test_type)+f"(R:{self.reading} W:{self.writting} L: {self.listening} S: {self.speaking})"

class Languages(object):
    def __init__(self, language_list: List[LanguageBase]) -> None:
        self.languages=language_list
    
    def getSpecifiedLanguage(self,test_type):
        language=[language for language in self.languages if language.test_type==test_type]
        return language[0] if language else None
    
    @property
    def PreferredLanguage(self):
        for language_type in ['IELTS','CELPIP','TEF','TCF']:
            language=self.getSpecifiedLanguage(language_type)
            if language: return language
