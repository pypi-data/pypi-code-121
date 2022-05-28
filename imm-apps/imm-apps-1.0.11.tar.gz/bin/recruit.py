# import context
import argparse,os
from termcolor import colored
from model.recruit.joboffer import JobofferModel, JobofferModelDocxAdapater
from model.recruit.jobad import JobadModel,JobadModelDocxAdapater
from model.recruit.recruitmentsummary import RecruitmnetSummaryModel,RecruitmnetSummaryDocxAdaptor

def creatExcel(model,excel_file):
    model(output_excel_file=excel_file)
    print(colored(f'{excel_file} is not existed, so we created the excel file based on your data structure.','green'))
    print(colored('Please fill the excel with data and do it again','yellow'))
    
def generateDocx(source_excel,model,adapter,outpout,template_no):
    context=model(excels=[source_excel])
    context=adapter(context)
    context.make(outpout,template_no)

models={
    "ja":{"model":JobadModel,'adaptor':JobadModelDocxAdapater},
    "jo":{"model":JobofferModel,'adaptor':JobofferModelDocxAdapater},
    "rs":{"model":RecruitmnetSummaryModel,'adaptor':RecruitmnetSummaryDocxAdaptor},
} 

    
def main():
    """ arguments:
        -e: excel file as source
        -t: output word file name
        -d: to generate docs--> ja: job advertisement docx, jo: job offer docx,rs: recruitment summary docx
    """
    parser=argparse.ArgumentParser(description="used for processing recruitment documents")
    parser.add_argument("-e", "--excel", help="input excel file name including the data for your specific stream")
    parser.add_argument("-t", "--to", help="input docx file name for output")
    parser.add_argument("-tn", "--template_no", help="input template number (1,2)")
    parser.add_argument("-d", "--document", help="input which kind of document to generate. type list: ja: job ad, jo: job offer, rs: recruitment summary")
    args = parser.parse_args()
    
    
    if args.document and args.document not in models.keys():
        print(colored(f"{args.document} is not a valid document type. Valid type list is: ci, ert, eet, jd, jof, rep",'red'))
        return 
    
    # if input excel file, then generate it
    if args.excel and not os.path.isfile(args.excel):
        model=models[args.document]['model']
        creatExcel(model,args.excel)
        print(colored(f'{args.excel} is created...','green'))
        return 
    
    if args.excel and args.to and args.document:
        model=models[args.document]['model']
        adaptor=models[args.document]['adaptor']
        generateDocx(args.excel,model,adaptor,args.to,args.template_no)
        return 
    print(colored('Wrong command/flag combination, type recruit -h for help','red'))
        
if __name__=='__main__':
    main()



