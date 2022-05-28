# from context import BASEDIR
from source.excel import Excel
from bin.common import ExcelMaker,valid_programs
import argparse
from functools import reduce
from termcolor import colored
import json

def main():
    parser=argparse.ArgumentParser(description="For munipulate excel and get data source...")
    
    parser.add_argument("-e", "--excel", help="Input excel name")
    parser.add_argument("-a", "--add", help="add up excels(can be more than 2), and output to another excel",nargs="+")
    parser.add_argument("-s", "--sub", help="sub excels(can be more than 2), and output to another excel",nargs="+")
    parser.add_argument("-c", "--copy", help="copy later excels' common contents to first excel(can be more than 2), and output to another excel",nargs="+")
    parser.add_argument("-t", "--to", help="Output file name")
    parser.add_argument("-po", "--protection_off", help="Protection off. default is On",action='store_true')
    parser.add_argument("-j", "--json", help="need json output",action='store_true')
    parser.add_argument("-d", "--dict", help="need dict output",action='store_true')
    parser.add_argument("-p", "--program", help="input program code. 5257 for trv, 1294 or 1295 for sp or wp outside of Canada. 5708/5709/5710 for vr/sp/wp in Canada ")
    
    
    args = parser.parse_args()
    protection=False if args.protection_off else True

    if args.add and args.to:
        if len(args.add)<2:
            raise ValueError("Must more than two excel files after -a ")
        try:
            excel_objs=list(map(lambda x:Excel(x), args.add))
            e=reduce(lambda a,b:a+b, excel_objs)
            e.makeExcel(args.to,protection=protection)
            print(colored(f'{args.to} saved',"green"))
            if args.json:
                print(e.json)
            if args.dict:
                print(e.dict)  
        except Exception as e:
            print(colored(f'{str(e)}','red'))
            
    if args.sub and args.to:
        if len(args.sub)<2:
            raise ValueError("Must more than two excel files after -a ")
        try:
            excel_objs=list(map(lambda x:Excel(x), args.sub))
            e=reduce(lambda a,b:a-b, excel_objs)
            e.makeExcel(args.to,protection=protection)
            print(colored(f'{args.to} saved',"green"))
            if args.json:
                print(e.json)
            if args.dict:
                print(e.dict) 
            
        except Exception as e:
            print(colored(f'{str(e)}','red'))
    
    if args.copy and args.to:
        if len(args.copy)<2:
            raise ValueError("Must  more than two excel files after -c ")
        try:
            excel_objs=list(map(lambda x:Excel(x), args.copy))
            e=reduce(lambda a,b:a.copy(b), excel_objs)
            e.makeExcel(args.to,protection=protection)
            print(colored(f'{args.to} saved',"green"))
            if args.json:
                print(e.json)
            if args.dict:
                print(e.dict) 
            
        except Exception as e:
            print(colored(f'{str(e)}','red'))
        
            
    if args.program and args.to:
        if args.program not in valid_programs:
            print(f'Your input program code {args.program} is not valid. ')
            return
        excel_file=ExcelMaker(args.program)
        excel_file.makeExcelBasedOnModel(args.to)
    
    if args.excel and args.to and args.json:
        excel=Excel(args.excel)
        with open(args.to,'w') as fp:
            json.dump(excel.dict,fp,indent=3,default=str)
        print(colored(f"{args.to} is saved","green"))
        
if __name__=="__main__":
    main()



