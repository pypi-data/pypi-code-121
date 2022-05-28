from docxtpl import DocxTemplate
from datetime import datetime


class WordTpl():

    def __init__(self,template,context,output):
       self.document=DocxTemplate(template)
       self.context=context
       self.output=output

    def render(self):
        self.document.render(self.context)
        self.document.save(self.output) 

context={
    "provider":{
        "name":"Jacky Zhang",
        "rcicNum":"R511623",
        "email":"noah.consultant@outlook.com",
        "phone":"7783215110",
        "address":"50-3306 Princeton Ave, Coquitlam, BC V3E 0M9"
    },
     "receiver":{
        "name":"Lily Zhao",
        "rcicNum":"R512623",
        "email":"lily_zhao@outlook.com",
        "phone":"7784445110",
        "address":"51-3306 Princeton Ave, Coquitlam, BC V3E 0M9"
    },
    "service":"BCPNP application",
    "client":"Liu Xiaoming",
    "price":5000,
    "gst":0.05,
    "terms":[
        {"subPrice":2500,"payDay":"the day of signing agreement"},
        {"subPrice":2500,"payDay":"the day of submission of the application"}
    ],
    "date":datetime.today().strftime("%Y-%m-%d")
}
def main():
    word=WordTpl('/Users/jacky/tools/templates/word/co-counsel agreement.docx',context,'lynn.docx')
    word.render()

if __name__=="__main__":
    main()

