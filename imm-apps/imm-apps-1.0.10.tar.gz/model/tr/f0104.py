from model.tr.d0104 import data_model
from model.tr.pdfformmodel import PdfFormModel


class F0104Model(PdfFormModel):
    
    def __init__(self,xml_file):
        # pass the globals variables to base class
        model={'data_model':data_model,'convert_model':{},'remove_model':{}}
        super().__init__(xml_file,model)

    def _getData(self):
        # work
        data_pairs={
            'employment':"Page1/EmploymentSub/EmploymentTbl",
            "education":"Page1/EducationSub/EducationTbl",
            "travel":"Page1/TravelSub/TravelTbl"
        }
        
        for key,parent_xpath in data_pairs.items():
            the_parent_xpath = [e for e in self.tree.iterfind(parent_xpath)][0]
            rows = []
            for i in range(1,100):
                employment_item =the_parent_xpath.find('Row'+str(i))
                if not employment_item:
                    break
                employment = self._getSubItem(employment_item, data_model[key])
                dates=self._getSubItem(employment_item,{'dates':"TimePeriodFrom"})
                employment={**dates,**employment}
                rows.append(employment)
            self.data[key] = rows

        # travel re-ordering
        travels=self.data['travel']
        temp=[]
        for travel in travels:
            travel={k:travel.get(k) for k in ['start_date','end_date','length','destination','purpose']}
            temp.append(travel)
        self.data['travel']=temp
        
    def _getSubItem(self,element,variable_xpath_pairs):
            temp_dict={}
            for variable,xpath in variable_xpath_pairs.items():
                try:
                    the_element = element.findall(xpath)
                    if len(the_element)>1:
                        start_date = the_element[0].text
                        temp_dict['start_date']=self._formatDate(start_date)
                        end_date = the_element[1].text
                        temp_dict['end_date']=self._formatDate(end_date)
                    elif len(the_element)==1:
                        value = the_element[0].text
                        temp_dict[variable]=value
                    else:
                        print(f"{xpath} is invalid xpath")    
                except:
                    print(f"{xpath} is invalid xpath")
            return temp_dict

    def _formatDate(self,input_date):
        y,m=input_date.split('-')[1],input_date.split('-')[0]
        return y+'-'+m+"-"+"01"
    
    def _convert(self):
        pass
    
    def _assembl(self):
        pass
    
    def _remove(self):
        pass
    