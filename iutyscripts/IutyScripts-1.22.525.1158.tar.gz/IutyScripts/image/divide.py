import sys,shutil,os,random

def movFile(images,dirname):
    curpath = os.path.abspath("./")
    dirpath = os.path.join(curpath,dirname)
    if os.path.exists(dirpath):
        print("warning:{} is exists before create".format(dirpath))
    else:
        os.mkdir(dirpath)
    
    for image in images:
        imgpath = os.path.join(curpath,image)
        targetpath = os.path.join(curpath,dirname,image)
        print("move file {} to dir {}".format(image,dirname))
        shutil.move(imgpath,targetpath)

def getShuffle(ratios,total):
    seed = 17
    if len(sys.argv) > 1:
        arg_seed = sys.argv.pop(1)
        if arg_seed:
            try:
                seed = int(arg_seed)
            except:
                print("warning:parse seed failed,use default 17")
    
    listdir = os.listdir("./")
    files = []
    for item in listdir:
        if os.path.isfile(os.path.join("./",item)):
            files.append(item)
    
    random.seed(seed)
    random.shuffle(files)
    
    spl_s = 0
    
    for r in range(len(ratios)):
        spl_e = int(len(files)*(ratios[r]/total))+spl_s
        images = files[spl_s:spl_e]
        if r == len(ratios) -1:
            images = files[spl_s:]
        spl_s = spl_e
        dirname = "{}_{}".format(r+1,ratios[r])
        movFile(images,dirname)
        
    pass

def doMove():
    ratio = sys.argv.pop(1)
    if ratio:
        rs = ratio.split(':')
        ratios = []
        total = 0
        for r in rs:
            try:
                ri = int(r)
                ratios.append(ri)
                total += ri
            except:
                print("error:parse ratio failed")
                return
        getShuffle(ratios,total)
        print("divide process complete!")
    pass

def showHelp():
    print("divide dataset proportionately,ignore formatter")
    print('-'*20)
    print("param:")
    print("\t1st ratio \t:\tsuch as 7:3,1:1:1.")
    print("\t2nd [seed][17] \t:\t divide randomly with seed,default 17")
    print('-'*20)



def main():
    if len(sys.argv) == 1:
        showHelp()
    else:
        doMove()
        
    pass

if __name__ == "__main__":
    
    main()
    pass