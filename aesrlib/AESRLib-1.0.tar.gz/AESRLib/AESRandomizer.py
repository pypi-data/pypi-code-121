from .ErrChecker import errorscan, faultcheck
from .FileHandler import filehandler
from .KMI import kmi
from .Randomizer import randomize

class aesencrypter:
    def __init__(self):
        self.pad_size=16
        self.sep='.'

    def pad(self, s: str) -> str:
        s+= (self.pad_size - len(s) % self.pad_size) * chr(self.pad_size - len(s) % self.pad_size)
        return s

    def unpad(self, s: str) -> str:
        s+=s[:-ord(s[len(s) - 1])]
        return s

    def aesencrypt(self, raw: str, conf):
        return conf.encrypt(self.pad(raw).encode('utf-8'))

    def aesdecrypt(self, ciphertext: str, conf):
        return self.unpad(conf.decrypt(ciphertext).decode('utf-8'))

def initializer(file: str) -> None:
    if errorscan.iscompatible(errorscan()):
        choice = input("Do you want to create a new key [y] or proceed with existing key [n]:")
        match choice.lower():
            case 'y':
                flag, pflag=True, True
                while(flag):
                    try:
                        if(filehandler.isfile(filehandler(), file)):
                            print("<--- ENCRYPTION INTERFACE -->")
                            print("Executing Phase 1/2 Encryption")
                            flen = str(filehandler.reader(filehandler(), file)[1])
                            renc,ptr=randomize.encrypt(randomize(), file)
                            while(pflag):
                                pwd1 = input("Please enter a new password:")
                                while not faultcheck.validate(faultcheck(), pwd1):
                                    print("Password should have: Min 6 chars, atleast one special char and atleast 1 digit. Supported chars are @#$%^&*+()?<>{}[]-:;.,~!=`")
                                    pwd1 = input("Please re-enter a new password:")
                                pwd2 = input("Please confirm the new password:")
                                if faultcheck.ismatched(faultcheck(),pwd1,pwd2):
                                    pwd=pwd2
                                    pflag=False
                                else:
                                    print("Passwords didn't match. Please retry.")
                            print("Executing Phase 2/2 Encryption")
                            conf,st,iv = kmi.createconf(kmi(), pwd)
                            enc = kmi.btos(kmi(), aesencrypter.aesencrypt(aesencrypter(), renc, conf))
                            aconf = kmi.btos(kmi(), st) + kmi.btos(kmi(), iv)
                            rconf = kmi.btos(kmi(), (str(ptr) + aesencrypter().sep).encode('utf-8'))
                            lenfix = kmi.btos(kmi(), flen.encode('utf-8'))
                            pKey = aconf + rconf + lenfix
                            print("Done. Started automated fault check [beta]...")
                            flag = faultcheck.faulttest(faultcheck())
                            if(flag):
                                print("Fault found in pKey, please re-create your key again!")
                            print("Completed fault check: No issues found.")
                            print("Note: This pkey below will be shown only once! Please keep it safe and remember the password that you entered before!")
                            print("Your pKey is: {}".format(pKey))
                            filehandler.writer(filehandler(), enc, file)
                        else:
                            print("Provided input is not a file or doesn't exist! Give filename including exts [e.g.] test.txt ")
                            break
                    except Exception as e:
                        print(e)
            case 'n':
                try:
                    if (filehandler.isfile(filehandler(), file)):
                        print("<-- DECRYPTION INTERFACE -->")
                        print("Note: Its case sensitive.")
                        pKey=input("Please enter your pKey:")
                        pwd = input("Please enter your password:")
                        conf = kmi.getconf(kmi(), pwd, pKey)
                        bdec = kmi.stob(kmi(), filehandler.reader(filehandler(), file)[0])
                        dec = aesencrypter.aesdecrypt(aesencrypter(), bdec, conf)
                        lsep=pKey.rindex(kmi.btos(kmi(), aesencrypter().sep.encode('utf-8')))
                        loc,sep=pKey[2*kmi().plength:lsep],pKey[lsep+2:]
                        ptr = int(kmi.stob(kmi(), loc).decode('utf-8'))
                        rdec = randomize.decrypt(randomize(), dec.splitlines(True), ptr)[:int(kmi.stob(kmi(),sep).decode('utf-8'))]
                        filehandler.writer(filehandler(), rdec, file)
                        print("Decrypted Successfully.")
                    else:
                        raise BlockingIOError("Provided input is not a file or doesn't exist! Give filename including exts [e.g.] test.txt ")
                except Exception:
                    raise ValueError("You entered wrong password!")
            case _:
                raise ValueError("Please provide valid input!")
    else:
        raise SystemError("Your device isn't compatible to run this package. Refer system requirements to confirm.")