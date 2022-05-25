from PIL import Image,ImageEnhance,ImageFilter 
import sys,os

import matplotlib.pyplot as plt



def bright(img,arg):
    value = 1.0
    try:
        value = float(arg[6:])
    except Exception as err:
        print("arg error in set bright, use default value 1.0")
    img = ImageEnhance.Brightness(img).enhance(value)
    return img

def flip(img,arg):
    value = arg[4:]
    if (value == "") | (value == "h"):
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    elif value == "v":
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
    else:
        print("arg error in flip,do nothing in flip")
    return img

def rotate(img,arg):
    value = 0
    try:
        value = int(arg[6:])
    except Exception as err:
        print("arg error in set rotate, use default value 0")
    img = img.rotate(value)
    return img

def noise(img,arg):
    pass

def blur(img,arg):
    value = 0
    try:
        value = int(arg[4:])
    except Exception as err:
        print("arg error in set gaussian blur, use default value 0")
    img = img.filter(ImageFilter.GaussianBlur(radius=value)) 
    return img

def sharp(img,arg):
    value = 1
    try:
        value = int(arg[5:])
    except Exception as err:
        print("arg error in set sharpen times, use default value 1")
    for i in range(value):
        img = img.filter(ImageFilter.SHARPEN)
    return img

def loadImage(path):
    image = Image.open(path)
    return image

def saveImage(image,path):
    image.save(path)
    pass

def doTranspose(img,transarg):
    for method in methods:
        if transarg.startswith(method):
            img = methods[method](img,transarg)
            return img,transarg
    return img,None


def setTranspose(path):
    trans_args = sys.argv[1:]
    print("Load image from path: {}".format(path))
    img = loadImage(path)
    dir_name = os.path.dirname(path)
    name = os.path.basename(path)
    fore_name = ""
    
    for trans_arg in trans_args:
        img,method = doTranspose(img,trans_arg)
        if method:
            fore_name += method
            fore_name += "__"
    
    if len(fore_name) > 0:
        savepath = os.path.join(dir_name,fore_name+name)
        print("save image to path {}".format(savepath))
        
        saveImage(img,savepath)
        

def setImage():
    for path in os.listdir("./"):
        if os.path.isdir(path):
            continue
        if len(path.split('__')) > 1:
            continue
        if path.endswith(".bmp") | path.endswith(".jpg") | path.endswith(".png"):
            setTranspose(path)
            print('-'*30)
    pass

def showHelp():
    print("extension image dataset with formatter: .jpg, .png, .bmp")
    print('-'*20)
    print("cmd:")
    print("\tbright[1.0] \t:\t adjust all pixel bright with value default:pixels * 1.0")
    print("\tflip[h] \t:\t flip image on horizential(default),key down flipv means flip image on vertical ")
    print("\trotate[0] \t:\t rotate image anticlockwisely,default:0")
    print("\tblur[0] \t:\t adjust image by gaussian blur,default ratio:0")
    print("\tsharp[1] \t:\t adjust image by sharpen(3*3,-2,-2,-2,-2,32,-2,-2,-2,-2),default times:1")
    print('-'*20)

methods = {
    "bright":bright,
    "flip":flip,
    "rotate":rotate,
    #"noise":noise,
    "blur":blur,
    "sharp":sharp,
}

def main():
    if len(sys.argv) == 1:
        showHelp()
    else:
        setImage()
        
    pass

if __name__ == "__main__":
    """
    img = loadImage("./i.bmp")
    img.show()
    print(img)
    input()
    flip = fliph(img)
    flip.show(flip)
    input()
    saveImage(flip,"./i__flip.bmp")
    """
    main()
    pass