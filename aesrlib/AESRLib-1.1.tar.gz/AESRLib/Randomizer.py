import base64
import random
from .FileHandler import filehandler
from .KMI import kmi

class randomize:
    def encrypt(self, file: str) -> tuple[str, int]:
        if filehandler.isfile(filehandler(),file):
            alpha = kmi.createalpha(kmi())
            rawlist = filehandler.readlines(filehandler(),file)[0]
            rawlist[len(rawlist)-1]+='\n'
            mapper = kmi.alphamap(kmi(), alpha)
            enclist = [None]*len(rawlist)
            akey = base64.b64encode(''.join(alpha).encode('utf-8')).decode('utf-8')+'\n'
            for i in range(len(rawlist)):
                enclist[i] = rawlist[i].translate(rawlist[i].maketrans(mapper))
            loc = random.randint(0, len(rawlist)-1)
            enclist.insert(loc, akey)
            enc = ''.join(enclist)
            return (enc, loc)

    def decrypt(self, ciphertext: list[str], loc: int) -> str:
        #encList=fileHandler.readLines(fileHandler(), ciphertext)[0]
        demapper = kmi.transalphamap(kmi(), ciphertext, loc)
        #ciphertext.remove(ciphertext[loc])
        declist = [None]*len(ciphertext)
        for i in range(len(ciphertext)):
            declist[i] = ciphertext[i].translate(ciphertext[i].maketrans(demapper))
        dec = ''.join(declist).replace(''.join(kmi().carray),'')
        return dec