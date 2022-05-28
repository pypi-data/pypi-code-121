#!/Users/jacky/tools/venv/bin/python3.9

# This app is developed for daily pdf manupilation 
from pikepdf import Pdf
from pdf2image import convert_from_path
from glob import glob
import argparse,os,img2pdf,shutil
from PIL import Image
from datetime import datetime

# convert img to pdf
def convertImg2Pdf(img_path):
    image = Image.open(img_path)
    pdf_bytes = img2pdf.convert(image.filename)
    pdf_path=img_path.split('.')[0]+".pdf"
    file = open(pdf_path, "wb")
    file.write(pdf_bytes)
    image.close()
    file.close()
    print(f"Successfully coverted {img_path} to pdf file {pdf_path}")

def batchCovertImg2Pdf(input):
    imgs=sorted(glob(input))
    for img in imgs:
        convertImg2Pdf(img)

def convert2img(pdfFile,folder="./",dpi=70):
    pages=convert_from_path(pdfFile,dpi)
    imgFileName=pdfFile.split(".")[0]
    i=0
    for page in pages:
        fn=folder+imgFileName+'{0:03}'.format(i)+".jpg"
        page.save(fn,'JPEG')
        i+=1
    print(f"Successfully converted pdf to {i} images...")

def pdf2pdf(pdfFile,outputFile=None,dpi=70):
    # make a temp folder
    now=datetime.now()
    tmpFolder=str(now.year)+str(now.month)+str(now.day)+str(now.hour)+str(now.minute)+str(now.second)
    os.mkdir(tmpFolder)
    # convert to imgs
    convert2img(pdfFile,tmpFolder+"/",dpi)
    # convert imgs to pdfs
    imgs=sorted(glob(tmpFolder+"/*.jpg"))
    for img in imgs:
        convertImg2Pdf(img)
    # delete all imgs
    remove="rm "+tmpFolder+"/*.jpg"
    os.system(remove)
    # merge pdfs to pdf
    targetName=outputFile or pdfFile.split(".")[0]+"_flatterned"+".pdf"
    merge(tmpFolder+"/*.pdf",targetName)
    # delete tmp folder
    shutil.rmtree(tmpFolder)
    print(f"{pdfFile} has been flatterned to {targetName}...")

def split(fileName):
    pdf=Pdf.open(fileName)
    outputName=fileName.split('.')[0]
    for n,page in enumerate(pdf.pages):
        dst=Pdf.new()
        dst.pages.append(page)
        dst.save(outputName+f'{n:03d}.pdf')
    pages=len(pdf.pages)
    print(f"Successfully splitted {fileName} to {pages} pdf.")

def merge(input,targetName):
    if type(input)==str:
        files=sorted(glob(input))
    elif type(input)==list:
        files=input
    else:
        files=None
        print('Input source error! it must be either filter string or a file list...')
        return
    pdf=Pdf.new()
    version=pdf.pdf_version
    for file in files:
        src=Pdf.open(file)
        version=max(version,src.pdf_version)
        pdf.pages.extend(src.pages)
    pdf.remove_unreferenced_resources()
    pdf.save(targetName)
    fileNumber=len(files)
    print(f'Successfully merged {fileNumber} files to {targetName}.')

def reverse(fileName):
    pdf=Pdf.open(fileName,allow_overwriting_input=True)
    pdf.pages.reverse()
    pdf.save()
    pages=len(pdf.pages)
    print(f"Successfully reversed {pages}.")

def append(source,target):
    pdf_source=Pdf.open(source)
    pdf_target=Pdf.open(target,allow_overwriting_input=True)
    pdf_target.pages.extend(pdf_source.pages)
    pdf_target.save()
    pages=len(pdf_source.pages)
    print(f'Successfully appended {pages} pages from {source} to {target}.')


# copy source pages from start page to end page to an existing file, or to append to a new file
def insert(source,target,startPage=0,endPage=-1,position=0):
    pdf_source=Pdf.open(source)
    if int(endPage)>len(pdf_source.pages):
        print(f"The end page {endPage} is bigger than the total pages {len(pdf_source.pages)}")
        return
    fileExist=os.path.isfile(target)
    if fileExist:
        pdf_target,position=Pdf.open(target,allow_overwriting_input=True),position 
    else:
        pdf_target,position=Pdf.new(),0

    if int(position)>len(pdf_target.pages):
        print(f"The position {position+1} is bigger than the total pages {len(pdf_target.pages)}")
        return
    pages=0
    initial_position=int(position)
    position=int(position)
    for page in range(int(startPage),int(endPage)):
        pdf_target.pages.insert(position,pdf_source.pages[page])
        position+=1
        pages+=1
    print(f'Total {pages} pages inserted to position from {initial_position} to {position}.')
    pdf_target.save() if fileExist else pdf_target.save(target)

def delete(fileName,start,end):
    pdf=Pdf.open(fileName,allow_overwriting_input=True)
    for page in range(int(end)-int(start)+1):
        del pdf.pages[end-page-1]
    pdf.save()
    print(f"Successfully deleted {end-start} pages from {start} to {end}\nNow {fileName} has {len(pdf.pages)} pages left.")



def main():
    parser=argparse.ArgumentParser(description="For munipulate pdfs: split, merge, reverse, rotate,img double way process...")
    
    parser.add_argument("-s", "--split", help="split pdf to sigle page with name: oringe+001.pdf")
    parser.add_argument("-f", "--filter", help="get pdf selection by using filter (exp: '*.pdf'. '' is must!), and merge to target file. (must followed by -t filename) ")
    parser.add_argument("-l", "--list", help="get pdf selection by list file names, and merge to target file. (must followed by -t filename) ",nargs="+")
    parser.add_argument("-r", "--reverse", help="reverse the pages of the pdf")
    parser.add_argument("-a", "--append", help="append the source pdf to target pdf, must followed by -t finename")
    parser.add_argument("-i", "--insert", help="insert pages with start page and end page from source to target file before the specified position. (must followed by -t filename) ",nargs="+")
    parser.add_argument("-d", "--delete", help="delete pages from start to end",nargs="+")
    parser.add_argument("-t", "--to", help="target pdf file name",nargs="+")
    parser.add_argument("-ip", "--img2pdf", help="img to pdf, source img file name")
    parser.add_argument("-bip", "--batchimg2pdf", help="get picture selection by using filter (exp: '*.jpg'. '' is must!) ")
    parser.add_argument("-pi", "--pdf2img", help="pdf to img source pdf file name. img files will use pdf's name with .jpg")
    parser.add_argument("-pp", "--pdf2pdf", help="source pdf file name. convert pdf to img and then to pdf. Make it flatterned")
    parser.add_argument("-dpi", "--dpi", help="set dpi value")

    args = parser.parse_args()

    if args.split:
        split(args.split)
        return 
    if args.filter and args.to:
        merge(args.filter,args.to[0])
        return
    if args.list and args.to:
        merge(args.list,args.to[0])
        return
    if args.reverse:
        reverse(args.reverse)
        return
    if args.append and args.to:
        append(args.append,args.to[0])
        return
    if args.insert and args.to:
        start=int(args.insert[1])-1
        end=int(args.insert[2])
        position=int(args.to[1])-1 if len(args.to)>1 else 0
        insert(args.insert[0],args.to[0],start,end,position)
        return
    if args.delete:
        start=int(args.delete[1])
        end=int(args.delete[2])
        delete(args.delete[0],start,end)
        return 

    if args.img2pdf:
        convertImg2Pdf(args.img2pdf)
        return 

    if args.batchimg2pdf:
        batchCovertImg2Pdf(args.batchimg2pdf)
        return

    if args.pdf2img:
        convert2img(args.pdf2img)
        return 
    
    if args.pdf2pdf:
        dpi=args.dpi or 70
        pdf2pdf(args.pdf2pdf,args.to[0]) if args.to else  pdf2pdf(args.pdf2pdf,dpi=dpi)
        return 

if __name__=="__main__":
    main()
