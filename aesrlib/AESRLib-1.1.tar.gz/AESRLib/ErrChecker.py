import re
import sys

class errorscan:
    """ def nTry(self,ismodify=None) -> int:
        if not os.path.exists('nt'):
            f=open('nt','x',encoding="utf-8")
            f.close()
        with open('nt', 'r',encoding="utf-8") as f:
            erc = f.read(1)
            f.close()
        if (erc == '' or erc is None):
            erc=0
        erc=int(erc)
        if ismodify:
            with open('nt','w',encoding="utf-8") as f:
                f.write(str(erc + 1))
                f.close()
        return erc """
    def iscompatible(self, ver: str='3.10.0') -> bool:
        mjth,mith,pth=[int(x) for x in ver.split('.')]
        ptn=re.search(r"(\d+).(\d+).(\d+)", sys.version)
        major,minor,patch=int(ptn.group(1)),int(ptn.group(2)),int(ptn.group(3))
        if major>=mjth and minor>=mith and patch>=pth:
            return True
        else:
            return False

class faultcheck:
    def faulttest(self) -> bool:
        return False

    def ismatched(self, pwd1: str, pwd2: str) -> bool:
        return pwd1==pwd2

    def validate(self, pwd: str) -> bool:
        if len(pwd)>=6 and re.search(r"\@|\#|\$|\%|\^|\&|\*|\+|\(|\)|\?|\<|\>|\{|\}|\[|\]|\-|\:|\;|\.|\~|\!|\=|\`|\,",pwd)!=None and re.search(r"\d+",pwd)!=None:
            return True
        else:
            return False