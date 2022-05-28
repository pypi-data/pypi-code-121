# import context
from model.bcpnp.companyinfo import CompanyInfoModel,CompanyInfoDocxAdaptor
from model.bcpnp.employeetraining import EmployeeTrainingModel,EmployeeTrainingDocxAdaptor
from model.bcpnp.recommendationletter import RecommendationLetterModel,RecommendationLetterDocxAdaptor
from model.bcpnp.employertraining import EmployerTrainingModel,EmployerTrainingDocxAdaptor
from model.bcpnp.jobdescription import JobDescriptionModel,JobDescriptionDocxAdaptor
from model.bcpnp.jobofferform import JobOfferFormModel,JobOfferFormDocxAdaptor
from model.bcpnp.repform import RepFormModel,RepFormDocxAdaptor
from termcolor import colored
import argparse,os

def creatExcel(model,excel_file):
    model(output_excel_file=excel_file)
    print(colored(f'{excel_file} is not existed, so we created the excel file based on your data structure.','green'))
    print(colored('Please fill the excel with data and do it again','yellow'))
    
def generateDocx(source_excel,model,adapter,outpout):
    context=model(excels=[source_excel])
    context=adapter(context)
    context.make(outpout)

models={
    "ci":{"model":CompanyInfoModel,'adaptor':CompanyInfoDocxAdaptor},
    "erl":{"model":RecommendationLetterModel,'adaptor':RecommendationLetterDocxAdaptor},
    "eet":{"model":EmployeeTrainingModel,'adaptor':EmployeeTrainingDocxAdaptor},
    "ert":{"model":EmployerTrainingModel,"adaptor":EmployerTrainingDocxAdaptor}, 
    "jd":{"model":JobDescriptionModel,'adaptor':JobDescriptionDocxAdaptor},
    "jof":{"model":JobOfferFormModel,'adaptor':JobOfferFormDocxAdaptor},
    "rep":{"model":RepFormModel,'adaptor':RepFormDocxAdaptor}
}    
def main():
    """ arguments:
    -e: excel file as source
    -t: output word file name
    -d: for generating which document, which includs: 
        ci: to generate company information
        ert: to generate employer training guide
        eet: to generate employee training guide
        jd: to generate job descriptin 
        jof: to generate job offer form xml 
        rep: to generate representative form xml
        all: to generate all above
    """
    parser=argparse.ArgumentParser(description='used for generating bcpnp required documents, for document types:')
    parser.add_argument("-e", "--excel", help="input excel file name including the data for your specific stream")
    parser.add_argument("-t", "--to", help="input docx file name for output, or input temp directory for batch generating all docxs")
    parser.add_argument("-d", "--document", help="input which kind of document to generate. type list: ci: flag for making company information\nert: Employer Training\neet:Employee Training\njd:Job Description\njof:Job Offer Form xml\nrep:Representative form xml\nall: to generate all above")
    args = parser.parse_args()

    if args.document and args.document not in models.keys() and args.document not in ['all']:
        print(colored(f"{args.document} is not a valid document type. Valid type list is: ci, ert, eet, jd, jof, rep",'red'))
        return 
        
    # if input excel file, then generate it
    if args.document and args.excel and not os.path.isfile(args.excel):
        creatExcel(models[args.document]['model'],args.excel)
        return 
    
    if args.to:
        if args.document.lower()=="all":
            generateAll(args.excel, args.to)
        else: 
            generate(args.excel,args.document,args.to)
        return 
    
    print(colored(f"Wrong command/flag combination, try bcpnp -h for help",'red'))

def generate(excel_file,doc_type,word_file):
    model=models[doc_type]['model']
    adaptor=models[doc_type]['adaptor']
    generateDocx(excel_file,model,adaptor,word_file)

def generateAll(excel_file,folder):
    for doc_type in models.keys():
        import os
        if not os.path.exists(folder):
            os.makedirs(folder)
        file_name=doc_type+".xml" if doc_type in ['jof','rep'] else doc_type+".docx"
        generate(excel_file,doc_type,folder+'/'+file_name)
        
if __name__=='__main__':
    main()



