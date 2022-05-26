# import context
import argparse
import os
from termcolor import colored
from .common import ExcelMaker,valid_programs,XmlReader        
    
def generate_file(program_code,excel_file):
    em=ExcelMaker(program_code)
    em.makeExcelBasedOnModel(excel_file)
    print(colored(f'{excel_file} is created...','green'))
    
def main():
    parser=argparse.ArgumentParser(description="used for processing temporary resident visa, study permit, and work permit both in Canada or outside of Canada")
    parser.add_argument("-p", "--program", help="input program code. 5257 for trv, 1294 or 1295 for sp or wp outside of Canada. 5708/5709/5710 for vr/sp/wp in Canada ")
    parser.add_argument("-x", "--xml", help="input xml file name")
    parser.add_argument("-t", "--to", help="input excel file name for output")
    args = parser.parse_args()
    
    if args.program not in valid_programs:
        print(colored(f'Your input program code {args.program} is not valid. ','red'))
        return
    
    if args.to and not os.path.isfile(args.to):
        generate_file(args.program,args.to)
        return 
            
    if args.program and args.xml and args.to:
        xr=XmlReader(args.program)
        xr.readXmlData2Excel(args.xml,args.to)
        print(colored(f'Excel file {args.to} is filled with {args.xml} data','green'))
        return 

    print(colored('Invalid command and flag combination... try trv -h for help','red'))
    
    
if __name__=='__main__':
    main()



