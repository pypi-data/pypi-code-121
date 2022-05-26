#!/Users/jacky/tools/venv/bin/python3.9

#!/Users/jacky/tools/venv/bin/python3.9
# This app is developed for daily files manupilation 
from glob import glob
import argparse,os,shutil,csv
from datetime import datetime


def collectNames(input):
    # get sorted file list by name
    names=sorted(glob(input))
    # create a tmp text file
    now=datetime.now()
    tmpFile=str(now.year)+str(now.month)+str(now.day)+str(now.hour)+str(now.minute)+str(now.second)+".txt"
    with open(tmpFile,"w") as f:
        for name in names:
            f.write(f"{name}\n")
    
    os.system(f'code {tmpFile}')
    return names,tmpFile

def batchChange(oldNames,txtFile):
    with open(txtFile,"r") as f:
        newNames=f.readlines()
    match=dict(zip(oldNames,newNames))
    for oldName,newName in match.items():
        newName=newName.replace("\n","")
        os.system(f"mv '{oldName}' '{newName}'")
        print(f'Successfully changed {oldName} to {newName}...')
    os.system(f"rm {txtFile}")
    print('Done!')



def main():
    parser=argparse.ArgumentParser(description="For munipulate pdfs: split, merge, reverse, rotate,img double way process...")
    
    parser.add_argument("-bc", "--batchchange", help="get matching files by using filter, and then change their filenames in a text editor (exp: '*.jpg'. '' is must!) ")


    args = parser.parse_args()

    if args.batchchange:
        names,txtFN=collectNames(args.batchchange)
        change=input('Are you ready to change?')
        if change[0].upper()=="Y":
            batchChange(names,txtFN)
            return
        else:
            os.system(f"rm {txtFN}")
            return 
    
if __name__=="__main__":
    main()
