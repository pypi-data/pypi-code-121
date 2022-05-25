import os,datetime,abc,struct,time
import random
from IutyLib.encription.encription import getfilemd5,des_descrypt,des_encrypt

class Code:
    @staticmethod
    def getFormat(s):
        if type(s) == str:
            return 's'
        if type(s) == float:
            return 'f'
        if type(s) == int:
            return 'i'
        if type(s) == datetime.date:
            return 'd'
        if type(s) == datetime.datetime:
            return 't'

    @staticmethod
    def getStringStream(data):
        bs = str.encode(data)
        st = bytes([len(bs)])
        return st+bs
        
    @staticmethod
    def getFloatStream(data):
        return struct.pack('f',data)
        
    @staticmethod
    def getIntStream(data):
        return struct.pack('I',data)
        
    @staticmethod
    def getDateStream(data):
        return bytes([data.year-1900]) + bytes([data.month]) + bytes([data.day])
    
    @staticmethod
    def getDateTimeStream(data):
        return bytes([data.year-1900]) + bytes([data.month]) + bytes([data.day]) + bytes([data.hour]) + bytes([data.minute]) + bytes([data.second])
        
    
    @staticmethod
    def getStream(format,data):
        if format == 's':
            return Code.getStringStream(data)
        if format == 'f':
            return Code.getFloatStream(data)
        if format == 'i':
            return Code.getIntStream(data)
        if format == 'd':
            return Code.getDateStream(data)
        if format == 't':
            return Code.getDateTimeStream(data)

    @staticmethod
    def getStringData(file):
        lenth = int(file.read(1)[0])
        stream = file.read(lenth)
        return bytes.decode(stream)
        
    @staticmethod
    def getFloatData(file):
        stream = file.read(4)
        return struct.unpack('f',stream)[0]
        
    @staticmethod
    def getIntData(file):
        stream = file.read(4)
        return struct.unpack('I',stream)[0]
        
    @staticmethod
    def getDateData(file):
        stream = file.read(3)
        
        return datetime.date(stream[0]+1900,stream[1],stream[2])
        
    @staticmethod
    def getDateTimeData(file):
        stream = file.read(6)
        
        return datetime.datetime(int(stream[0])+1900,int(stream[1]),int(stream[2]),
        int(stream[3]),int(stream[4]),int(stream[5]))
    
    @staticmethod
    def getData(format,file):
        if format == 's':
            return Code.getStringData(file)
        if format == 'f':
            return Code.getFloatData(file)
        if format == 'i':
            return Code.getIntData(file)
        if format == 'd':
            return Code.getDateData(file)
        if format == 't':
            return Code.getDateTimeData(file)


class ByteFile:
    #for stock, data[0] must a datetime.date
    def __init__(self,title,path,pattern,root = ".//",isserial = True):
        
        self.title = title
        self.root = root
        
        for p in path:
            self.root = self.root + p + "//"
            if not os.path.exists(self.root):
                os.mkdir(self.root)
        
        self.pattern = "." + pattern
        self.isserial = isserial
        self.value = []
        #if isserial:
            #self.value = self.getData()
        
        
    def getFile(self):
        for file in os.listdir(self.root):
            if (file[0:len(self.title)] == self.title):
                if (os.path.isfile(self.root+file)) & (file.endswith(self.pattern)):
                    return file
        return None
        
    def getAllTitle(self):
        titles = []
        for file in os.listdir(self.root):
            if (os.path.isfile(self.root+file) & (file[-4:]==self.pattern)):
                titles.append(file.split('#')[0])
        return titles
    
    def creat(self,data):
        formatstr = ''
        for s in data[0]:
            formatstr += Code.getFormat(s)
        fullpath = '{0}{1}#{2}#{3}'.format(self.root,self.title,formatstr,self.pattern)
        f = open(fullpath,'ab')
        f.close()
        
    def append(self,data):
        if type(data) == type(None):
            print ('error in {0}'.format(self.title))
        path = self.root + self.getFile()
        if self.isserial:
            f = open(path,'ab')
        else:
            f = open(path,'wb')
        for dt in data:
            for d in dt:
                stream = Code.getStream(Code.getFormat(d),d)
                f.write(stream)
        f.close()
        
    def appendData(self,data):
        if len(data) == 0:
            return
        
        appends = []
        if self.getFile() == None:
            self.creat(data)
        if (not self.isserial) | (len(self.value) == 0):
            appends = data
        else:
            lastdata = self.value[-1]
            for d in data:
                if d[0] > lastdata[0]:
                    appends.append(d)
        self.append(appends)
        
    def getData(self,refesh = False):
        if not refesh:
            if len(self.value)>0:
                return self.value
        if self.getFile() == None:
            return []
        path = self.root + self.getFile()
        f = open(path,'rb')
        rtn = []
        format = self.getFile().split('#')[1]
        filelen = f.seek(0,2)
        f.seek(0)
        while (f.seek(0,1)<filelen):
            cell = []
            data = None
            for fm in format:
                data = Code.getData(fm,f)
                
                cell.append(data)
            rtn.append(tuple(cell))
        self.value = rtn
        f.close()
        return rtn

    def removeData(self,days):
        data = self.getData()

        date = datetime.date.today() - datetime.timedelta(days)
        newdata = []
        for i in range(0,len(data)):
            if data[i][0] < date:
                newdata.append(data[i])
        self.delete()
        self.appendData(newdata)

        
    def delete(self):
        if self.getFile() != None:
            os.remove(self.root + self.getFile())
    
    def removeFiles(self):
        for file in os.listdir(self.root):
            os.remove(os.path.join(self.root,file))

class StringFile:
    def __init__(self,root = './/',title = 'txt'):
        self.title = title
        self.root = root
        pass
    
    def getFile(self):
        date = datetime.date.today().strftime('%y-%m-%d')
        for file in os.listdir(self.root):
    
            if (os.path.isfile(self.root+file)) & (file[0:len(date + '.' + self.title)] == date + '.' + self.title):
                return file
        return None
    
    def creat(self):
        date = datetime.date.today().strftime('%y-%m-%d')
        fullpath = self.root + date + '.' + self.title
        f = open(fullpath,'a')
        f.close()
    
    def append(self,message):
        if self.getFile() == None:
            self.creat()
        path = self.root + self.getFile()
        f = open(path,'a')
        f.write(message+"\n")
        f.close()
        pass

class CsvFile:
    def __init__(self,name,root="./",formatter = "csv"):
        filename = "{}.{}".format(name,formatter)
        self.fullpath = os.path.join(root,filename)
        
        pass
    
    def getInputValue(value):
        val = "{}".format(value[0])
        for i in range(1,len(value)):
            val += ",{}".format(value[i])
        rtn = val + "\n"
        return rtn
    
    def getInputValues(values):
        ds = ""
        for value in values:
            ds += CsvFile.getInputValue(value)
        return ds
    
    def append(self,value):
        fs = open(self.fullpath,"a",encoding="UTF-8")
        line = CsvFile.getInputValue(value)
        fs.write(line)
        fs.close()
        pass
    
    def appends(self,values):
        fs = open(self.fullpath,"a",encoding="UTF-8")
        ds = CsvFile.getInputValues(values)
        fs.write(ds)
        fs.close()
    
    def delete(self):
        if os.path.exists(self.fullpath):
            os.remove(self.fullpath)
        pass
    
    def getData(self):
        data0 = []
        if os.path.exists(self.fullpath):
            fs = open(self.fullpath,"r",encoding="UTF-8")
            data0 = fs.readlines()
        data = []
        for d in data0:
            dr = d.replace("\n","")
            di = dr.split(',')
            data.append(di)
        return data


if __name__ == "__main__":
    csv = CsvFile("test")
    csv.append(["No.","Value","Comment"])
    csv.appends([[0,1,"c1"],[1,2,"c2"]])
    print(csv.getData())
