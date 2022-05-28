from model.tr.d1294 import data_model, convert_model,remove_model
from model.tr.pdfformmodel import PdfFormModel


class F1294Model(PdfFormModel):
    
    def __init__(self,xml_file):
        # pass the globals variables to base class
        model={'data_model':data_model,'convert_model':convert_model,'remove_model':remove_model}
        super().__init__(xml_file,model)

    def _getSpecial(self):
        # work
        occupation_info = [
            e for e in self.tree.iterfind('Page3/Occupation')][0]
        occupations = []
        for i in [1, 2, 3]:
            occupation_item = occupation_info.find('OccupationRow'+str(i))
            occupation = self._getSubItem(
                occupation_item, data_model['occupation'])
            occupations.append(occupation)

        self.data['occupations'] = occupations


