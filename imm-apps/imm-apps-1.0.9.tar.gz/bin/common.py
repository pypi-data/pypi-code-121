valid_programs=['5257','1294','1295','5708','5709','5710','0104','5645']

class ModelImporter(object):
    def __init__(self,program_code) -> None:
        self.program_code=program_code
        
    def loadModel(self,model_type):
        module_prefix="m" if model_type=="DataModel" else "f"
        model_prefix="M" if model_type=="DataModel" else "F"
        module_path=f"model.tr.{module_prefix}{self.program_code}"
        class_list=[f"{model_prefix}{self.program_code}Model"]
        the_class=__import__(module_path,fromlist=class_list)
        return getattr(the_class,class_list[0])
    
class ExcelMaker(ModelImporter):
    def makeExcelBasedOnModel(self,output_excel):
        # 获取数据模型
        data_model=self.loadModel("DataModel")
        data_model(output_excel_file=output_excel)
        return output_excel

class XmlReader(ModelImporter):
    def readXmlData2Excel(self, xml_file,output_excel):
        #获取pdf表格模型
        form_model=self.loadModel('FormModel')
        form=form_model(xml_file)
        form._makeExcel(output_excel,protection=True)

