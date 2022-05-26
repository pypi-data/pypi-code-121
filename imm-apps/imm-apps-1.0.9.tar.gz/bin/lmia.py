# import context
import argparse,os
from termcolor import colored
from model.lmia.submissionletter import SubmissionLetterModel
from model.lmia.employertraining import EmployerTrainingModel
from model.recruit.recruitmentsummary import RecruitmnetSummaryModel,RecruitmnetSummaryDocxAdaptor
    
def main():
    """ arguments:
        -e: excel file as source
        -t: output word file name
        -d: --> sl: submission letter, et: employer training guideline, rs: recruitment summary 
    """
    parser=argparse.ArgumentParser(description="used for processing lmia application")
    # parser.add_argument("-s", "--stream", help="input stream code. 5593 for pr, 5626 for HWS or 5627 for LWS ")
    parser.add_argument("-e", "--excel", help="input excel file name including the data for your specific stream")
    parser.add_argument("-t", "--to", help="input docx file name for output")
    parser.add_argument("-d", "--document", help="input which kind of document to generate. type list: sl: submission letter et: employer training guideline, rs: recruitment summary ")
    args = parser.parse_args()

    if args.excel and args.to:
        match args.document: 
            case 'sl':
                # if input excel file, then generate it
                if not os.path.isfile(args.excel):
                    SubmissionLetterModel(output_excel_file=args.excel)
                    print(colored(f'{args.excel} is not existed, so we created the excel file based on your data structure.','green'))
                    print(colored('Please fill the excel with data and do it again','yellow'))
                    return 
                context=SubmissionLetterModel(excels=[args.excel])
                context.makeDocx(args.to)
    
            case 'et':
                # if input excel file, then generate it
                if not os.path.isfile(args.excel):
                    EmployerTrainingModel(output_excel_file=args.excel)
                    print(colored(f'{args.excel} is not existed, so we created the excel file based on your data structure.','green'))
                    print(colored('Please fill the excel with data and do it again','yellow'))
                    return 
                context=EmployerTrainingModel(excels=[args.excel])
                context.makeDocx(args.to)
        
            case 'rs':
                # if input excel file, then generate it
                if not os.path.isfile(args.excel):
                    RecruitmnetSummaryModel(output_excel_file=args.excel)
                    print(colored(f'{args.excel} is not existed, so we created the excel file based on your data structure.','green'))
                    print(colored('Please fill the excel with data and do it again','yellow'))
                    return 
                context=RecruitmnetSummaryModel(excels=[args.excel])
                RecruitmnetSummaryDocxAdaptor(context).make(args.to)
    
if __name__=='__main__':
    main()



