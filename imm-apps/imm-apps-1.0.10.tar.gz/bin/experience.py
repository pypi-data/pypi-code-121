# import context
import argparse,os
from termcolor import colored
from model.experience.resume import ResumeModel,ResumeModelDocxAdapater
from model.experience.ec import EmploymentModel,EmploymentModelDocxAdapater

def creatExcel(model,excel_file):
    model(output_excel_file=excel_file)
    print(colored(f'{excel_file} is not existed, so we created the excel file based on your data structure.','green'))
    print(colored('Please fill the excel with data and do it again','yellow'))
    
def generateDocx(source_excel,model,adapter,outpout,template_num=None):
    context=model(excels=[source_excel])
    context=adapter(context)
    context.make(outpout,template_num) if template_num else  context.make(outpout)

models={
    "rs":{"model":ResumeModel,'adaptor':ResumeModelDocxAdapater},
    "ec":{"model":EmploymentModel,'adaptor':EmploymentModelDocxAdapater},
} 

    
def main():
    """ arguments:
        -e: excel file as source
        -t: output word file name
        -d: --> rs: resume, ec: employment certificates
        -tn: resume template number
    """
    parser=argparse.ArgumentParser(description="used for processing lmia application")
    # parser.add_argument("-s", "--stream", help="input stream code. 5593 for pr, 5626 for HWS or 5627 for LWS ")
    parser.add_argument("-e", "--excel", help="input excel file name including the data for your specific stream")
    parser.add_argument("-t", "--to", help="input docx file name for output")
    parser.add_argument("-d", "--document", help="input which kind of document to generate. type list: rs: resume, ec: employment certificates")
    parser.add_argument("-tn", "--template_no", help="resume template number (1-5)")
    args = parser.parse_args()

    
    if args.excel and args.to and args.document:
        try: 
            model=models[args.document]['model']
            adaptor=models[args.document]['adaptor']
        except KeyError as e:
            print(colored(f"{e} is not a valid document type. Valid type list is: rs, ec",'red'))
            return 
        # if input excel file, then generate it
        if not os.path.isfile(args.excel):
            if args.document!='ec': 
                creatExcel(model,args.excel)
            else:
                print(colored(f'{args.excel} is not existed.','red'))
                print(colored('You can use personal excel pa.xlsx and fill the employment rows, and then try again...','blue'))
            return 
        generateDocx(args.excel,model,adaptor,args.to,args.template_no)
    
if __name__=='__main__':
    main()



