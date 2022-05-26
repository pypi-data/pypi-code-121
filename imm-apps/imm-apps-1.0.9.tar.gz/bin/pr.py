# import context
from model.pr.m0008 import M0008Model
from model.pr.m5406 import M5406Model
from model.pr.m5562 import M5562Model
from model.pr.m5669 import M5669Model
import argparse,os
from termcolor import colored

def main():
    parser=argparse.ArgumentParser(description="used for processing permanent resident visa")
    parser.add_argument("-p", "--program", help="input program code: 0008 5669 5562 5406 ")
    parser.add_argument("-t", "--to", help="input excel file name for output")
    args = parser.parse_args()
    
    valid_programs={
        '0008':M0008Model,
        '5406':M5406Model,
        '5562':M5562Model,
        '5669':M5669Model
        }
    if args.program not in valid_programs.keys():
        print(colored(f'Your input program code {args.program} is not valid. ','red'))
        return
    
    if args.to: # and not os.path.isfile(args.to):
        valid_programs[args.program](output_excel_file=args.to)
        return 

    print(colored('Invalid command and flag combination... try pr -h for help','red'))
    
    
if __name__=='__main__':
    main()