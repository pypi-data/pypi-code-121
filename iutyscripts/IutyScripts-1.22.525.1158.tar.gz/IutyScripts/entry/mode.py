import os,sys

#mode = unit:entry at package dir
#mode = intergrate:entry at intergrate dir,instance is business test
#mode = packaging:entry at packaging,instance is demo


cur = os.path.abspath("./")

def addPathAsRoot(p):
    pth = os.path.abspath(p)
    if not pth in sys.path:
        sys.path.insert(0,pth)

unit = False
if os.path.exists("./unit"):
    addPathAsRoot("../")
    unit = True

intergrate = False
if cur.endswith("intergrate"):
    addPathAsRoot("../")
    intergrate = True

packaging = False
if os.path.exists("./packaging"):
    addPathAsRoot("../")
    packaging = True


def test():
    print("debug mode:{}".format(unit))
    print("intergrate mode:{}".format(intergrate))
    print("packaging mode:{}".format(packaging))

if __name__ == "__main__":
    test()
