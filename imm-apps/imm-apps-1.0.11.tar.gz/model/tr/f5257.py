from model.tr.d5257 import data_model, convert_model,remove_model
from model.tr.pdfformmodel import PdfFormModel


class F5257Model(PdfFormModel):
    
    def __init__(self,xml_file):
        # pass the globals variables to base class
        model={'data_model':data_model,'convert_model':convert_model,'remove_model':remove_model}
        super().__init__(xml_file,model)
            
    
    def _getSpecial(self):
        # work 
        occupation_info=[e for e in self.tree.iterfind('Page3/Occupation')][0]
        occupations=[]
        for i in [1,2,3]:
            occupation_item=occupation_info.find('OccupationRow'+str(i))
            occupation=self._getSubItem(occupation_item,data_model['occupation'])
            occupations.append(occupation)

        self.data['occupations']=occupations

        
#     def _convert(self):
#         # 1 convert countries
#         country_pairs={
#             "trcase":["applying_country"],
#             "personal":['country_of_birth','citizen'],
#             'passport':['country'],
#             'national_id':['country'],
#             'education':['country'],
#             'cor':['current_cor_country','previous_cor_country1','previous_cor_country2']
#         }
#         language_pairs={
#             'personal':['native_language']
#         }
#         other_pairs={
#             'phone':["variable_type"],
#             'altphone':["variable_type"]
#         }
#         canada_city_pairs={
#             # 'sp':["city"]
#         }
#         tr_canada_status_pairs= {
#             'cor':['current_cor_status','previous_cor_status1','previous_cor_status2']
#         }
#         tr_marital_status_pairs={
#             'marriage':['marital_status']
#         }
        
#         tr_pre_marital_status_pairs={
#             'marriage':['pre_relationship_type']
#         }
        
#         self._execConvert(country_pairs,country)
#         self._execConvert(language_pairs,language)
#         self._execConvert(other_pairs,phone_type)
#         self._execConvert(canada_city_pairs,canada_city)
#         self._execConvert(tr_canada_status_pairs,tr_canada_status)
#         self._execConvert(tr_marital_status_pairs,tr_marital_status)
#         self._execConvert(tr_pre_marital_status_pairs,tr_marital_status)
    
#     def _assembl(self):
#         # for English or French
#         self.data['personal']['which_one_better']='English' if self.data['personal']['which_one_better']=='01' else "French"
#         # assembly dob 
#         self.data['personal']['dob']=self.data['personal'].get('dob_year')+"-"+self.data['personal'].get('dob_month')+"-"+self.data['personal'].get('dob_day')
#         dob_y,dob_m,dob_d=self.data['marriage'].get('pre_sp_dob_year'),self.data['marriage'].get('pre_sp_dob_month'),self.data['marriage'].get('pre_sp_dob_day')
#         self.data['marriage']['pre_sp_dob']=dob_y+"-"+dob_m+"-"+dob_d  if all([dob_y,dob_m,dob_d]) else None
        
#         self._cor_assemble()
#         self._id_assemble()
#         self._address_assemble()
#         self._phone_assemble()
#         # self._work_permit_assemble()
#         self._education_assemble()
#         self._occupation_assemble()
        
#     def _remove(self):
#         popup_pairs={
#             'personal':['dob_year','dob_month','dob_day'],
#             'marriage':['pre_sp_dob_year','pre_sp_dob_month','pre_sp_dob_day']
#         }
#         for k,v in popup_pairs.items():
#             [self.data[k].pop(item) for item in v]
            
#     def show(self,sheet):
#         # show off
#         if isinstance(sheet,dict):
#             for variable, text in sheet.items():
#                 print(variable,text)
#         elif isinstance(sheet,list):
#             for i in range(len(sheet)):
#                 for variable, text in sheet[i].items():
#                     print(variable,text)
                    
#     # countries of residence
#     def _cor_assemble(self):
#                 # assemble countries of residence
#         cor_dict=self.data['cor']
#         cor_current={
#             'country':cor_dict['current_cor_country'],
#             'status':cor_dict['current_cor_status'],
#             'other':cor_dict['current_cor_other'],
#             'start_date':cor_dict['current_cor_start_date'],
#             'end_date':cor_dict['current_cor_end_date']
#             }
#         cor_pre1={
#             'country':cor_dict['previous_cor_country1'],
#             'status':cor_dict['previous_cor_status1'],
#             'other':cor_dict['previous_cor_other1'],
#             'start_date':cor_dict['previous_cor_start_date1'],
#             'end_date':cor_dict['previous_cor_end_date1']
#             }
#         cor_pre2={
#             'country':cor_dict['previous_cor_country2'],
#             'status':cor_dict['previous_cor_status2'],
#             'other':cor_dict['previous_cor_other2'],
#             'start_date':cor_dict['previous_cor_start_date2'],
#             'end_date':cor_dict['previous_cor_end_date2']
#             }
#         # re-sort the order of cor 
#         cor=[]
#         for c in [cor_current,cor_pre1,cor_pre2]:
#             d={}
#             for key in ['start_date','end_date','country','status']:
#                 d[key]=c[key]
#             cor.append(d)
#         self.data['cor']=cor

#     # ids 
#     def _id_assemble(self):
#         passport={'variable_type':'passport',**self.data['passport']}
#         nid={'variable_type':'id',**self.data['national_id']}
#         us_pr={
#             'variable_type':'pr',
#             'number':self.data['us_pr']['number'],
#             'expiry_date':self.data['us_pr']['expiry_date']
#             }
#         self.data['personid']=[passport,nid,us_pr]
#         [self.data.pop(x) for x in ['passport','national_id','us_pr']]

#     # address 
#     def _address_assemble(self):
#         m_dict=self.data['mailing_address']
#         r_dict=self.data['residential_address']
#         m={'variable_type':'mailing_address',**m_dict}
#         if r_dict['same_as_mailing']=='Y':
#             r=m
#         else:
#             r={'variable_type':"residential_address",**r_dict}
#         self.data['address']=[m,r]
#         [self.data.pop(x) for x in ['mailing_address','residential_address']]
    
#      # phone 
#     def _phone_assemble(self):
#         temp_phone=[]
#         for p_type in ['phone','altphone','fax']:
#             d=self.data[p_type]
#             if d.get('number'): #如果没有号码，就位空
#                 d['variable_type']='fax' if not d.get('variable_type') else d['variable_type']
#                 temp_phone.append({ k:v for k,v in d.items() if k in ['variable_type','country_code','number','ext']})
#         [self.data.pop(x) for x in ['phone','altphone','fax']]
#         self.data['phone']=temp_phone        

#      # work permit 
#     def _work_permit_assemble(self):
#         temp_wp={}
#         for d in [self.data['detailed_work'],self.data['intended_location'],self.data['intended_job']]:
#             temp_wp={**temp_wp,**{ k:v for k,v in d.items()}}
#         [self.data.pop(x) for x in ['detailed_work','intended_location','intended_job']]
#         self.data['wp']=temp_wp
        
#     # education
#     def _education_assemble(self):
#         self.data['education']['start_date']=self.data['education']['start_date_year']+'-'+self.data['education']['start_date_month']+'-01'
#         self.data['education']['end_date']=self.data['education']['end_date_year']+'-'+self.data['education']['end_date_month']+'-01'
#         # re-sort education's order
#         temp={}
#         for k in ['start_date','end_date','school_name','education_level','field_of_study','city','province','country']:
#             temp[k]=self.data.get('education').get(k,None)
#         self.data['education']=temp
#     # occupation
#     def _occupation_assemble(self):
#         temp=[]
#         for occupation in self.data['occupations']:
#             occupation['start_date']=occupation['start_date_year']+'-'+occupation['start_date_month']+'-01' if all([occupation['start_date_year'],occupation['start_date_month']]) else ""
#             occupation['end_date']=occupation['end_date_year']+'-'+occupation['end_date_month']+'-01' if all([occupation['end_date_year'],occupation['end_date_month']]) else ""
#             occupation['country']=NameCodeConvert(country).getName(occupation['country']) # convert country code to country name
#             temp.append(occupation)
#         temp1=[]
#         for t in temp:
#             d={}
#             for k in ['start_date','end_date','job_title','company','city','province','country']:
#                 d[k]=t[k]
#             temp1.append(d) 
            
#         self.data['employment']=temp1    
    
#     # get same xx_type
#     def _getTableNodeWithType(self,table_node_list,the_type):
#         try:
#             for node in table_node_list:
#                 if node["variable_type"]==the_type:
#                     return node
#         except:
#             return None
    
#     # excel_file should be an existed excel file matching the 5257 program
#     def _makeExcel(self,excel_file,protection):
        
#         new_excel_obj=Excel(excel_file) #if path.isfile(excel_file) else self.new_excel_obj
#         # 根据表格的sheets/tables来处理。 
#         for sheet_name, sheet_obj in new_excel_obj.sheets.items():
#             for variable,variable_obj in sheet_obj.data.items():
#                 sheet=self.data.get(sheet_name)
#                 value=sheet.get(variable) if sheet else None
#                 new_excel_obj.sheets[sheet_name].data[variable].value=value
        
#         for table_name,table_obj in new_excel_obj.tables.items():
#             # this three tables will be processed independently
#             if (table_name in ['personid','address','phone']):
#                 for index,variable_obj in enumerate(table_obj.data):
#                     if variable_obj:
#                         node=self._getTableNodeWithType(self.data.get(table_name),variable_obj.variable_type)
#                         for k in variable_obj.__dict__.keys():
#                             value=node.get(k) if node else None
#                             if k not in ['variable_type','display_type']: setattr(new_excel_obj.tables[table_name].data[index],k,value)
#             # others are normal                
#             else:
#                 # 现在在每张表里，取出seld.data[table_name]的table_node数据字典，做成tablenode,放到表里的data中。
#                 node_data=self.data.get(table_name)
#                 if isinstance(node_data,dict):
#                     new_excel_obj.tables[table_name].data.append(TableNode(**node_data))
#                 elif isinstance(node_data,list):
#                     for node in node_data:
#                         new_excel_obj.tables[table_name].data.append(TableNode(**node))
#                 else:
#                     pass
#         # 根据最终更新了variables的sheets和talbes，生成新的excel文件
#         new_excel_obj.makeExcel(excel_file,protection=protection)

        
        
# #TODO: 明天需要做：
# # 1.  继续整理数据格式到excel。
# # 2. 根据5257模型中的sheet，生成excel文件，根据excel文件的sheets/tables，来这里找数据，然后给自己赋值。 然后保存



