from model.tr.d5708 import data_model, convert_model,remove_model
from model.tr.pdfformmodel import PdfFormModel

class F5708Model(PdfFormModel):

    def __init__(self,xml_file):
            # pass the globals variables to base class
        model={'data_model':data_model,'convert_model':convert_model,'remove_model':remove_model}
        super().__init__(xml_file,model)        
    
    def _getSpecial(self):
        # work 
        occupations=[]
        for i in range(1,100):
            occupation_item=self.tree.find('Page3/Employment/EmpRec'+str(i))
            if occupation_item is None:
                break
            occupation=self._getSubItem(occupation_item,data_model['occupation'])
            occupations.append(occupation)

        self.data['occupations']=occupations

    
