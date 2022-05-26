from docxtpl import DocxTemplate
from termcolor import colored

class WordMaker():
    """This class makes word file based on template and filling in the data of context
    """    
    def __init__(self,template,context,output):
        self.document=DocxTemplate(template)
        self.context=context
        self.output=output
    
    def make(self):
        self.document.render(self.context)
        self.document.save(self.output) 
        print(colored(f'{self.output} has been saved...','green'))
