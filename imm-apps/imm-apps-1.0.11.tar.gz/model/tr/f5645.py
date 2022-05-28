from model.tr.pdfformmodel import PdfFormModel
from model.tr.d5645 import data_model, convert_model,remove_model

class F5645Model(PdfFormModel):
    def __init__(self,xml_file):
        # pass the globals variables to base class
        model={'data_model':data_model,'convert_model':convert_model,'remove_model':remove_model}
        super().__init__(xml_file,model)
        self._reorder()
        
    def _getSpecial(self):
        # child 
        children=self.tree.iterfind('page1/SectionB/Child')
        children_list=[]
        for child in children:
            child_item=self._getSubItem(child,data_model['children'])
            children_list.append(child_item)
        self.data['children']=children_list
        
        #siblings
        siblings=self.tree.iterfind('page1/SectionC/Child')
        siblings_list=[]
        for sibling in siblings:
            sibling_item=self._getSubItem(sibling,data_model['siblings'])
            siblings_list.append(sibling_item)
        self.data['siblings']=siblings_list
        

    
    def _assembl(self):
        for sheet,value in self.data.items():
            if sheet=='applicant': continue
            if isinstance(value,dict):
                self.data[sheet]['accompany_to_canada']=value['accompany_to_canada_yes']
            elif isinstance(value,list):
                for index,d in enumerate(value):
                    self.data[sheet][index]['accompany_to_canada']=value[index]['accompany_to_canada_yes']
            else:
                pass
        
        self.data['family']=[
            {
                'relationship':'applicant',
                **self.data['applicant']
            },
            {
                'relationship':'spouse',
                **self.data['spouse']
            },
            {
                'relationship':'mother',
                **self.data['mother']
            },
            {
                'relationship':'father',
                **self.data['father']
            },
            *self.data['children'],
            *self.data['siblings']
        ]
        # re-order the dict to match execl
    
    def _remove(self):
        popup_pairs={
            'spouse':['accompany_to_canada_yes','accompany_to_canada_no'],
            'mother':['accompany_to_canada_yes','accompany_to_canada_no'],
            'father':['accompany_to_canada_yes','accompany_to_canada_no']
        }
        for k,v in popup_pairs.items():
            [self.data[k].pop(item) for item in v]
        [self.data.pop(key)  for key in ['children','siblings','spouse','applicant','mother','father']  ]
        for index,f in enumerate(self.data['family']):
            if f.get('relationship')!='applicant':
                self.data['family'][index].pop('accompany_to_canada_yes',None)
                self.data['family'][index].pop('accompany_to_canada_no',None)
        
    def _reorder(self):
        #get name not none members
        members=[ m for m in self.data['family'] if m.get('name')!=None]
        # get first last name and native language first last name
        for member in members:
            #get all names
            names=member['name'].replace(',',' ') # remove ',' 
            names=' '.join(names.split()) # replace multiple space with one. 
            names=names.split(' ') # split names 
            native_last_name,native_first_name=names[-1][0],names[-1][1:] # get native language name
            last_name,first_name=names[:-1][0],''.join(names[:-1][1:]) #get first and last name
            member['last_name']=last_name
            member['first_name']=first_name
            member['native_last_name']=native_last_name
            member['native_first_name']=native_first_name
            member.pop('name')
        # or-order the dict
        temp_list=[]
        for member in members:
            temp={}
            for k in ['last_name','first_name','native_last_name','native_first_name','marital_status','date_of_birth','birth_country','address','occupation','relationship','accompany_to_canada']:
                temp[k]=member.get(k)
            temp_list.append(temp)
        self.data['family']=temp_list
            
