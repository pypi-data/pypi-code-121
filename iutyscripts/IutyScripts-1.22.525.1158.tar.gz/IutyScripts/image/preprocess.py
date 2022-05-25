from PIL import Image,ImageEnhance,ImageFilter,ImageStat
import sys,os
import cv2


def getImageBright(img):
    im = img.convert('L')
    stat = ImageStat.Stat(im)
    return stat.mean[0]

def getImageBlur(path):
    
    image = cv2.imread(path)
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    result = cv2.Laplacian(gray, cv2.CV_64F).var()
    return result

def bright(img,path,arg):
    
    value = 127
    try:
        value = float(arg[6:])
    except Exception as err:
        print("arg error in set bright, use default value 127")
    if (value > 255) | (value < 0):
        print("bright value {} error,it must lower than 255 and higher than 0")
        return
    lv = getImageBright(img)
    evalue = value/lv
    img = ImageEnhance.Brightness(img).enhance(evalue)
    saveImage(img,path)
    print("adjust the bright of image {} to {}".format(path,value))
    

def resize(img,path,arg):
    try:
        value = arg[6:].split('*')
        if len(value) != 2:
            raise Exception("value parse error,it must be width*height")
        width = int(value[0])
        height = int(value[1])
        img = img.resize((width, height),Image.ANTIALIAS)
        saveImage(img,path)
        print("resize image {} to width*height {}".format(path,arg[6:]))
    except Exception as err:
        print(err)
    
    pass



def blur(img,path,arg):
    value = 5.0
    try:
        value = float(arg[4:])
    except Exception as err:
        print("arg error in set minimum blur value, use default value 5.0")
    imgblur = getImageBlur(path)
    
    if imgblur < value:
        img = img.filter(ImageFilter.SHARPEN)
        saveImage(img,path)
        print("sharpen image {} because the blur {} is lower than {}".format(path,imgblur,value))
    pass


def loadImage(path):
    image = Image.open(path)
    return image

def saveImage(image,path):
    image.save(path)
    pass

def doTranspose(img,path,transarg):
    for method in methods:
        if transarg.startswith(method):
            methods[method](img,path,transarg)
    pass


def setTranspose(path):
    trans_args = sys.argv[1:]
    #print("Load image from path: {}".format(path))
    img = loadImage(path)
    dir_name = os.path.dirname(path)
    name = os.path.basename(path)
    fore_name = ""
    
    for trans_arg in trans_args:
        doTranspose(img,path,trans_arg)
        
        

def setImage():
    for path in os.listdir("./"):
        if os.path.isdir(path):
            continue
        
        if path.endswith(".bmp") | path.endswith(".jpg") | path.endswith(".png"):
            setTranspose(path)
            print('-'*30)
    pass

def showHelp():
    print("image dataset preprocess with formatter: .jpg, .png, .bmp")
    print('-'*20)
    print("cmd:")
    print("\tresize     \t:\t adjust picture width and height ,key down like resize200*120")
    print("\tbright[127] \t:\t adjust all pixel bright with average level default:127")
    
    
    print("\tblur[5.0] \t:\t sharpen image by blur < request blur,default minimum value:5.0")
    
    print('-'*20)

methods = {
    "resize":resize,
    "bright":bright,
    
    "blur":blur,
}

def main():
    if len(sys.argv) == 1:
        showHelp()
    else:
        setImage()
        
    pass

if __name__ == "__main__":
    
    main()
    pass