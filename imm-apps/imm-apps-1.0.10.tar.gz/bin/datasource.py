# from context import BASEDIR
from source.excel import Excel
import argparse,json

def main():
    parser=argparse.ArgumentParser(description="For munipulate excel and get data source...")
    
    parser.add_argument("-e", "--excel", help="Input excel file name")
    parser.add_argument("-a", "--add", help="add up two excels, and output to another excel",nargs="+")
    parser.add_argument("-s", "--sub", help="sub two excels, and output to another excel",nargs="+")
    parser.add_argument("-t", "--to", help="Output excel file name")
    parser.add_argument("-po", "--protection_off", help="Protection off. default is On",action='store_true')
    parser.add_argument("-j", "--json", help="need json output",action='store_true')
    parser.add_argument("-d", "--dict", help="need dict output",action='store_true')
    
    
    args = parser.parse_args()
    protection=False if args.protection_off else True

    if args.add and args.to:
        if len(args.add)!=2:
            raise ValueError("Must two excel files after -a ")
        e1=Excel(args.add[0])
        e2=Excel(args.add[1])
        try:
            e=e1+e2
            e.makeFormatedExcel(args.to,protection=protection)
            if args.json:
                print(e.json)
            if args.dict:
                print(e.dict)  
        except ValueError as e:
            print(str(e))
            
    if args.sub and args.to:
        if len(args.sub)!=2:
            raise ValueError("Must two excel files after -a ")
        e1=Excel(args.sub[0])
        e2=Excel(args.sub[1])
        try:
            e=e1-e2
            e.makeFormatedExcel(args.to,protection=protection)
            if args.json:
                print(e.json)
            if args.dict:
                print(e.dict) 
            
        except ValueError as e:
            print(str(e)) 
    
    if args.excel and args.json:
        e=Excel(args.excel)
        print(json.dumps(e.json,indent=3,default=str))

if __name__=="__main__":
    main()



