import os

class filehandler:
    def isfile(self, file: str) -> bool:
        if os.path.isfile(os.path.join(os.getcwd(), os.path.basename(file))):
            return True
        else:
            return False

    def reader(self, rfile: str) -> tuple[str,int]:
        try:
            if os.path.getsize(rfile) > 0:
                with open(rfile, "r",encoding="utf-8") as f:
                    data=f.read()
                    f.close()
                return (data,len(data))
            else:
                print('Provided file is empty!')
                exit(1)
        except IOError as e:
            print(e)
            exit(1)

    def writer(self, data: str, wfile: str):
        with open(os.path.basename(wfile),"w", encoding="utf-8") as f:
            f.write(data)
            f.close()

    def readlines(self, rfile: str) -> tuple[list[str],int]:
        try:
            if os.path.getsize(rfile) > 0:
                with open(rfile, "r", encoding="utf-8") as f:
                    data=f.readlines()
                    f.close()
                return (data,len(data))
            else:
                print('Provided file is empty!')
                exit(1)
        except IOError as e:
            print(e)
            exit(1)