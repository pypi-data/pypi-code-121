import xml.etree.ElementTree as ET
from source.tablesheet import TableNode
from source.excel import Excel
from model.common.convert import NameCodeConvert
from model.data.country import country
from model.data.language import language
from model.data.other import phone_type,tr_canada_status,tr_marital_status,tr_form_study_level,tr_form_study_field,tr_portal_study_level,tr_portal_study_field,marital_stauts_5645
from model.data.city import canada_city,canada_province

class PdfFormModel():
    """
    This model is for get information for TR vis or permit pdf xml, and save it to xlsx
    """
    def __init__(self,xml_file,model) -> None:
        self.data_model=model.get('data_model')
        self.convert_model=model.get('convert_model')
        self.remove_model=model.get('remove_model')
        self.tree=ET.ElementTree(file=xml_file)
        self.root=self.tree.getroot()
        self.data={}    # data from pdf xml, and then foe excel file after some operations
        self._getData() # get raw data from pdf xml    
        self._convert() # convert country, language, etc...
        self._assembl() # use temp variables to assemble excel needed variables
        self._remove() # remove not needed variables
    
    def _getSubItem(self,element,variable_xpath_pairs):
        temp_dict={}
        for variable,xpath in variable_xpath_pairs.items():
            try:
                temp_dict[variable]=element.find(xpath).text
            except:
                print(f"{xpath} is invalid xpath")
        return temp_dict

    def _getData(self):
        for sheet,source_pair in self.data_model.items():
            if sheet not in ['occupation','children','siblings']: 
                self.data[sheet]=self._getSubItem(self.root,source_pair)
            else:
                self._getSpecial()
            
    
    def _getSpecial(self):
        pass

    # convert some items to excel format 
    def _execConvert(self,pairs:dict,convert_item):
        for sheet, items in pairs.items():
            for item in items:
                # change value dict with converted country name
                sheet_data = self.data.get(sheet)
                if isinstance(sheet_data,list):
                    for i,sheet_item in enumerate(sheet_data):
                        code=sheet_data and sheet_data[i].get(item)
                        if code: self.data[sheet][i][item]=NameCodeConvert(convert_item).getName(code)
                else:
                    code=sheet_data and sheet_data.get(item)
                    if code: self.data[sheet][item]=NameCodeConvert(convert_item).getName(code)
        
    def _convert(self):
        global_variables=globals()
        for pairs, model in self.convert_model.items():
            model = global_variables[pairs[:-6]]  # get model by pairs name remove '_pairs'
            self._execConvert(self.convert_model[pairs], model)

        canada_city_pairs = {
            'sp': ["city"],
            'wp': ["employment_city"],
            'visa': ["city"],
            'vrincanada': ["city"],
            'spincanada': ["city"],
            'wpincanada': ["work_city"],
        }
        self._convert_city(canada_city_pairs, canada_city)
    
    def _convert_city(self,canada_city_pairs,canada_city):
        the_cities={}
        for cities in canada_city.values():
            for city, code in cities.items():
                the_cities[city]=code
        self._execConvert(canada_city_pairs,the_cities)
        
    def _assembl(self):
        # for English or French
        self.data['personal']['which_one_better']='English' if self.data['personal']['which_one_better']=='01' else "French"
        trcase_trcasein='trcase' if 'trcase' in self.data.keys() else 'trcasein'
        self.data[trcase_trcasein]['service_in']='English' if self.data[trcase_trcasein]['service_in']=='01' else "French"
        
        # assembly dob 
        self.data['personal']['dob']=self.data['personal'].get('dob_year')+"-"+self.data['personal'].get('dob_month')+"-"+self.data['personal'].get('dob_day')
        dob_y,dob_m,dob_d=self.data['marriage'].get('pre_sp_dob_year'),self.data['marriage'].get('pre_sp_dob_month'),self.data['marriage'].get('pre_sp_dob_day')
        self.data['marriage']['pre_sp_dob']=dob_y+"-"+dob_m+"-"+dob_d  if all([dob_y,dob_m,dob_d]) else None
        
        self._cor_assemble()
        self._id_assemble()
        self._address_assemble()
        self._phone_assemble()
        # self._work_permit_assemble()
        self._education_assemble()
        self._occupation_assemble()
        
    # countries of residence
    def _cor_assemble(self):
        cor_dict=self.data['cor']
        cor_current={
            'country':cor_dict['current_cor_country'],
            'status':cor_dict['current_cor_status'],
            'other':cor_dict['current_cor_other'],
            'start_date':cor_dict['current_cor_start_date'],
            'end_date':cor_dict['current_cor_end_date']
            }
        cor_pre1={
            'country':cor_dict['previous_cor_country1'],
            'status':cor_dict['previous_cor_status1'],
            'other':cor_dict['previous_cor_other1'],
            'start_date':cor_dict['previous_cor_start_date1'],
            'end_date':cor_dict['previous_cor_end_date1']
            }
        cor_pre2={
            'country':cor_dict['previous_cor_country2'],
            'status':cor_dict['previous_cor_status2'],
            'other':cor_dict['previous_cor_other2'],
            'start_date':cor_dict['previous_cor_start_date2'],
            'end_date':cor_dict['previous_cor_end_date2']
            }
        # re-sort the order of cor 
        cor=[]
        for c in [cor_current,cor_pre1,cor_pre2]:
            d={}
            for key in ['start_date','end_date','country','status']:
                d[key]=c[key]
            cor.append(d)
        self.data['cor']=cor

    # ids 
    def _id_assemble(self):
        passport={'variable_type':'passport',**self.data['passport']}
        nid={'variable_type':'id',**self.data['national_id']}
        us_pr={
            'variable_type':'pr',
            'number':self.data['us_pr']['number'],
            'expiry_date':self.data['us_pr']['expiry_date']
            }
        self.data['personid']=[passport,nid,us_pr]
        [self.data.pop(x) for x in ['passport','national_id','us_pr']]

    # address 
    def _address_assemble(self):
        m_dict=self.data['mailing_address']
        r_dict=self.data['residential_address']
        m={'variable_type':'mailing_address',**m_dict}
        if r_dict['same_as_mailing']=='Y':
            r=m
        else:
            r={'variable_type':"residential_address",**r_dict}
        self.data['address']=[m,r]
        [self.data.pop(x) for x in ['mailing_address','residential_address']]
        # convert country and province
        for i,addr in enumerate(self.data['address']):
            self.data['address'][i]['country']=NameCodeConvert(country).getName(addr['country']) 
            self.data['address'][i]['province']=NameCodeConvert(canada_province).getName(addr['province']) 
    
     # phone 
    def _phone_assemble(self):
        temp_phone=[]
        for p_type in ['phone','altphone','fax']:
            d=self.data[p_type]
            if d.get('number'): #如果没有号码，就位空
                d['variable_type']='fax' if not d.get('variable_type') else d['variable_type']
                temp_phone.append({ k:v for k,v in d.items() if k in ['variable_type','country_code','number','ext']})
        [self.data.pop(x) for x in ['phone','altphone','fax']]
        self.data['phone']=temp_phone        

     # work permit TODO: 这个不应该在里面，应该是1295的特别的。 
    def _work_permit_assemble(self):
        temp_wp={}
        for d in [self.data['detailed_work'],self.data['intended_location'],self.data['intended_job']]:
            temp_wp={**temp_wp,**{ k:v for k,v in d.items()}}
        [self.data.pop(x) for x in ['detailed_work','intended_location','intended_job']]
        self.data['wp']=temp_wp
        
    # education
    def _education_assemble(self):
        self.data['education']['start_date']=self.data['education']['start_date_year']+'-'+self.data['education']['start_date_month']+'-01'
        self.data['education']['end_date']=self.data['education']['end_date_year']+'-'+self.data['education']['end_date_month']+'-01'
        # re-sort education's order
        temp={}
        for k in ['start_date','end_date','school_name','education_level','field_of_study','city','province','country']:
            temp[k]=self.data.get('education').get(k,None)
        self.data['education']=temp

    def _remove(self):
        for k, v in self.remove_model.items():
            [self.data[k].pop(item) for item in v]
            
    # occupation
    def _occupation_assemble(self):
        temp=[]
        for occupation in self.data['occupations']:
            occupation['start_date']=occupation['start_date_year']+'-'+occupation['start_date_month']+'-01' if all([occupation['start_date_year'],occupation['start_date_month']]) else ""
            occupation['end_date']=occupation['end_date_year']+'-'+occupation['end_date_month']+'-01' if all([occupation['end_date_year'],occupation['end_date_month']]) else ""
            occupation['country']=NameCodeConvert(country).getName(occupation['country']) # convert country code to country name
            occupation['province']=NameCodeConvert(canada_province).getName(occupation['province']) # convert province code to province name
            temp.append(occupation)
        temp1=[]
        for t in temp:
            d={}
            for k in ['start_date','end_date','job_title','company','city','province','country']:
                d[k]=t[k]
            temp1.append(d) 
            
        self.data['employment']=temp1    
    
    # get same xx_type
    def _getTableNodeWithType(self,table_node_list,the_type):
        try:
            for node in table_node_list:
                if node["variable_type"]==the_type:
                    return node
        except:
            return None
    
    # excel_file should be an existed excel file matching the 1294 program
    def _makeExcel(self,excel_file,protection):
        
        excel_obj=Excel(excel_file) #if path.isfile(excel_file) else self.new_excel_obj

        for sheet_name, sheet_dict in self.data.items():
            # 如果不是sheet 下一个
            if sheet_name not in excel_obj.sheets.keys():
                continue
            
            for key,value in sheet_dict.items():
                # 如果excel表中有对应的sheet和字段
                if key in excel_obj.sheets[sheet_name].data.keys():     
                    excel_obj.sheets[sheet_name].data[key].value=value
        
        for table_name,table_obj in excel_obj.tables.items():
            # this three tables will be processed independently
            if (table_name in ['personid','address','phone']):
                for index,value in enumerate(table_obj.data):
                    if value:
                        node=self._getTableNodeWithType(self.data.get(table_name),value.variable_type)
                        for k in value.__dict__.keys():
                            value=node.get(k) if node else None
                            if k not in ['variable_type','display_type']: setattr(excel_obj.tables[table_name].data[index],k,value)
            # others are normal                
            else:
                # 现在在每张表里，取出sel.data[table_name]的table_node数据字典，做成tablenode,放到表里的data中。
                node_data=self.data.get(table_name)
                if isinstance(node_data,dict):
                    excel_obj.tables[table_name].data.append(TableNode(**node_data))
                elif isinstance(node_data,list):
                    for node in node_data:
                        excel_obj.tables[table_name].data.append(TableNode(**node))
                else:
                    pass
        # 根据最终更新了variables的sheets和talbes，生成新的excel文件
        excel_obj.makeExcel(excel_file,protection=protection)





