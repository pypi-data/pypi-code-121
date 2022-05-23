import os 
import numpy as np 
import tkinter as tk
from tkinter import filedialog
import re 
import datetime 
import shutil 
import string
from scipy.signal import kaiserord, lfilter, firwin, welch, hanning

class FileHandler():

    def __init__(self, workdir = os.getcwd(), foldername = "none", projectname = 'AnJAM2_v1.0'):
        self.projectname = projectname 
        self.foldername  = foldername
        self.workdir     = workdir

    ## data reader function 
    def reader(self, filenames = [], verbose = True, datatype = "float32"):
        readdir = self.testpath()
        root = tk.Tk()
        root.withdraw()
        fileDir = readdir
        if not filenames:
            filenames = filedialog.askopenfilenames(parent=root,initialdir=fileDir,title='Please select a directory')
        else : 
            if isinstance(filenames, list):
                for i in range(len(filenames)) : 
                    filenames[i] = os.path.join(readdir, filenames[i])
            else : 
                filenames = os.path.join(readdir, filenames)
                filenames = [filenames]
        data = []
        dictdata = {}
        if verbose:
            start_time = datetime.datetime.now()
        for filename in filenames:
            filename = filename.replace('\\', '/')
            with open(filename, 'r') as file:
                data = file.readlines()
                dict_data = {"int16" : np.int16, "uint16": np.uint16, 
                             "int8"  : np.int8 , "uint8" : np.uint8}                       
                if datatype == "float32":
                    for i in range(len(data)):
                        data[i] = int(data[i][:-1], 2) 
                    data = sfl2fix(data)
                else : 
                    for i in range(len(data)):
                        data[i] = dict_data[datatype](int(data[i][:-1], 2))
            substring = '/'
            matches = re.finditer(substring, filename)
            matches_positions = [match.start() for match in matches]
            index = matches_positions[-1]
            dictdata[filename[index + 1: -4]] = data
        if verbose:
            end_time = datetime.datetime.now()
            print("Time to reading data : " + str(end_time - start_time))
        return dictdata


    ### data writer function      
    def writer(self, datadict, filenames, datatype = "float32"):
        lebels = list(datadict.keys())
        writedir = self.testpath()
        filedir = []
        if not isinstance(filenames, list):
            filenames = [filenames]
        for filename in filenames: 
            filedir.append( writedir + '/' + filename )
        for label, dir in list(zip(lebels, filedir)): 
            newdata = datadict[label]
            with open(dir, 'w') as file:
                datatypedict = {"float32": 32, "int16": 16}
                for element in newdata:
                    element = np.binary_repr(int(element), datatypedict[datatype])
                    file.write(element + "\n") 


    def testpath(self):
        dir = self.workdir
        dir = dir.replace('\\', '/')
        filename = self.foldername 
        filenamelen = len(filename)
        index = dir.find(filename)
        findprjname = dir[:index + filenamelen]
        generateddir = findprjname + '/' + self.projectname + '.srcs/sim_1'
        checkpath = generateddir + '/TestFiles'
        if not os.path.isdir(checkpath):
            os.mkdir(checkpath)
        return checkpath



    def filenamegen(self, filetype, inouttype, filedescription, filenumber, filereim, codec, plusedir = False, help = True):
        if help : 
            print("File type : include the name of the software which generate the file forexample matlab or vivado")
            print("Inouttype : declare that your data is input or output of the meintioned software for example in")
            print("Filedescription : declare file data type and a short discription of it for example when we have float32 weight we type ")
            print("floww (### NOTE THAT THE LENGTH OF THIS TERM CAN ONLY EQUAL TO 6)")
            print("Filenumber : shows the number of generated file")
            print("File reim : shows that your data is real or imag")
            print("Codec : shows the coded of the file for example some files codec is .txt")
            print("PluseDir add Testfolder path beside of the generated filename")
        diflen = 6 - len(filedescription)
        if diflen < 0 :
            print("your description length must be lower then 6 !!!")
            return -1
        else :
            filedescription = ("X" * diflen) + filedescription.upper()
            filetype = filetype[0].upper() + filetype[1:3]
            inouttype = inouttype[0].upper() + inouttype[1:3]
            if filenumber < 10 : 
                filenumber = '0' + str(filenumber)
            else : 
                filenumber = str(filenumber)
            filereim = filereim[0].upper() + filereim[1:]
            filename = filetype + "_" + inouttype + "_" + filedescription + "_" + filenumber + "_" + filereim + codec 
            if plusedir: 
                testpath = self.testpath()
                filename = testpath + '/' + filename 
                return filename
            else:
                return filename


'''
    functions which used outside the class 
'''
# this functin convert floatArray to fix one 
def sfl2fix(floatArr):
    floatArr = np.array(floatArr, dtype = np.float32 )
    # if len(floatArr.shape) == 0 :
    floatArr = np.append(floatArr, 1)
    Arrshape = floatArr.shape
    bitlen = 32
    newFloatArr = np.zeros(Arrshape, dtype = np.float32)
    sign = np.zeros(Arrshape, dtype = np.float32)
    logithresh = 2**(bitlen - 1) - 1
    greater = np.where(floatArr > logithresh)
    less_equal = np.where(floatArr <= logithresh)
    newFloatArr[greater] = floatArr[greater] - (logithresh + 1)
    newFloatArr[less_equal] = floatArr[less_equal]
    sign[greater] = -1
    sign[less_equal] = 1
    expPrime = np.floor((newFloatArr / (2**23)))
    exp = expPrime - 127;
    Mantissa = np.abs(expPrime - newFloatArr / (2**23))
    fixArr = np.multiply(Mantissa + 1, 2**(exp))
    fixArr = np.multiply(sign, fixArr)
    fixArr = fixArr[:-1] 
    return fixArr

# this one is the inverse transform on the sfl2fix function
def fix2sfl(fixArr):
    fixArr = np.array(fixArr, dtype = np.float32)
    Arrsize = fixArr.shape
    
    if len(Arrsize) == 0 :
        if fixArr != 0 :
            sign = fixArr / abs(fixArr)
            fixArr = abs(fixArr)   
        else : 
            fixArr = 1
            floatArr = 0
            sign = 0
    else :
        sign = np.ones(Arrsize)
        negativeSigns = np.where(fixArr < 0)
        notzeros = np.where(fixArr != 0)
        sign[negativeSigns] = -1
        floatArr = np.zeros(Arrsize)
        fixArr = np.abs(fixArr[notzeros])
    exp = np.floor(np.log2(fixArr))
    expPrime = exp + 127
    Mantissa = np.true_divide(fixArr, 2**(exp)) - 1
    floatArrcalc = (expPrime*2**23) + np.floor(Mantissa*2**23)
    if len(Arrsize) == 0 :
        if sign == -1 :
            floatArr = floatArrcalc + 2**31
        else : 
            floatArr = floatArrcalc
    else :
        floatArr[notzeros] = floatArrcalc
        floatArr[negativeSigns] = floatArr[negativeSigns] + 2**31
    return floatArr



def ca(sv_num):
    tap = [
    [2, 6],
    [3, 7],
    [4, 8],
    [5, 9],
    [1, 9],
    [2, 10],
    [1, 8],
    [2, 9],
    [3, 10],
    [2 ,3],
    [3, 4],
    [5 ,6],
    [6 ,7],
    [7 ,8],
    [8 ,9],
    [9, 10],
    [1, 4],
    [2, 5],
    [3, 6],
    [4 ,7],
    [5, 8],
    [6 ,9],
    [1, 3],
    [4, 6],
    [5, 7],
    [6 ,8],
    [7 ,9],
    [8 ,10],
    [1, 6],
    [2, 7],
    [3 ,8],
    [4 ,9],
    [5 ,10],
    [4 ,10],
    [1 ,7],
    [2 ,8],
    [4 ,10]]
    tap = np.array(tap)
    s = np.array([0, 0, 1, 0, 0, 0, 0, 0, 0, 1])
    n = len(s)
    g1 = np.array( [1 for i in range(n)])
    L = 2**n - 1
    t = np.array([0, 1, 1, 0, 0, 1, 0, 1, 1, 1])
    q = np.array([1 for i in range(n)])
    tap_sel = tap[sv_num - 1, :]
    g2 = []
    g = []
    for inc in range(L):
        g2.append(sum(q[tap_sel - 1])%2)
        g.append((g1[n - 1] + g2[inc])%2)
        g1 = np.hstack((sum(np.multiply(g1, s))%2, g1[:-1]))
        q = np.hstack((sum(np.multiply(q, t))%2, q[:-1]))
    return g

def upsample(vec, uprate):
    kernel = np.ones((1, int(uprate)))
    up = np.kron(vec, kernel)
    up = up[:][0]
    return(up)

def filterdesign(Fs,Fpass, Fstop, Astop, sig):
    nyq_rate = Fs
    width = Fpass/nyq_rate
    ripple_db = Astop
    N, beta = kaiserord(ripple_db, width)
    cutoff_hz = Fstop
    taps = firwin(N, cutoff_hz/nyq_rate, window=('kaiser', beta))
    filtered_x = lfilter(taps, 1.0, sig)
    filt_len = N
    return(filt_len, filtered_x)

def pow2db(np_vec):
    return 10*np.log10(np_vec)










