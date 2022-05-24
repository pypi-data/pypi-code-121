import PyPDF2
import re

path = "/home/sauroman/angiography_data/runs/Feb04_14-14-30_sauromanPCclassification_config_angio_2/plots/train/conf_matrix_ext.pdf"

obj = PyPDF2.PdfFileReader(path)
num_pages = obj.getNumPages()
string = "F1"

for i in range(0, num_pages):
    pageObj = obj.getPage(i)
    text = pageObj.extractText() 
    # print(Text)
    ResSearch = re.search(string, text)
    print(ResSearch)