#----------------------------------------------------------------------#
# Python interface for reading HIPO files.
# Authors: M. McEneaney (2022, Duke University)
#----------------------------------------------------------------------#

import os
import glob
import sys
import shutil
import numpy as np
import numpy.ma as ma
import awkward as ak
import hipopybind

#----------------------------------------------------------------------#
# Basic  I/O behaviors

def open(filename,mode="r"):
    """
    Parameters
    ----------
    filename : string, required
    mode : string, optional
        File mode ("r" : read, "w" : write, "a" : append)
        Default : "r"

    Description
    -----------
    Open a HIPO file to read.
    """
    f = hipofile(filename,mode=mode)
    f.open()
    return f

def iterate(files,banks=None,step=100):
    """
    Parameters
    ----------
    files : list, required
        List of file names
    banks : list, optional
        List of bank names to read
        Default : None
    step : int
        Batch size for iterating through file events
        Default : 100

    Description
    -----------
    Iterate through a list of hipofiles reading all banks unless specific banks are specified.
    Iteration is broken into batches of step events.
    """
    f = hipochain(files,banks,step=step)
    return f


def create(filename):
    """
    Parameters
    ----------
    filename : string, required

    Description
    -----------
    Open a HIPO file to write (overwrites existing files).
    """
    f = hipofile(filename,mode="w")
    return f

def recreate(filename):
    """
    Parameters
    ----------
    filename : string, required

    Description
    -----------
    Open an existing HIPO file to write more banks.
    """
    f = hipofile(filename,mode="a")
    f.open() #NOTE: This just opens the reader.  To open the writer, call f.open() again explicitly after adding schema you want to write.
    return f

#----------------------------------------------------------------------#
# Classes: hipofile, hipofileIterator, hipochain, hipochainIterator

class hipofile:

    """
    Attributes
    ----------
    filename : string
        Full path name of HIPO file
    libpath : string
        Path to shared library file
    mode : string
        File mode ("r" : read, "a" : append, "w" : write)
    reader : hipopybind.Reader
        HIPO file reader
    writer : hipopybind.Writer
        HIPO file writer
    dict : hipopybind.Dictionary
        HIPO file schema dictionary
    event : hipopybind.Event
        HIPO event for reading and writing banks
    group : int
        Group number for current HIPO bank (unique)
    item : int
        Item number for current HIPO bank (not unique)
    dtypes : dict
        Dictionary to datatypes
    buffext : string
        Extension for buffer file
    buffname : string
        Name of buffer file
    """

    # Methods
    # -------
    # open
    # flush
    # close
    # goToEvent
    # nextEvent
    # addSchema
    # addEvent
    # writeEvent
    # writeAllBanks
    # writeBank
    # newTree
    # extend
    # write
    # hasBank
    # show
    # showBank
    # getBanks
    # readAllBanks
    # readBank
    # getGroup
    # getEntries
    # getNamesAndTypes
    # getNames
    # getTypes
    # getRows
    # getInts
    # getFloats
    # getDoubles
    # getShorts
    # getLongs

    def __init__(self,filename,mode="r"):
        """
        Parameters
        ----------
        filename : string, required
            Full path name of HIPO file
        mode : string, optional
            File mode ("r" : read, "w" : write, "a" : append)
            Default : "r"
        """
        self.filename   = filename
        self.reader     = hipopybind.Reader() if mode != "w" else None
        self.writer     = hipopybind.Writer() if mode != "r" else None
        self.dictionary = hipopybind.Dictionary()
        self.event      = hipopybind.Event()
        self.mode       = mode # "r" : read, "w" : write, "a" : append
        self.group      = 0
        self.item       = 1
        self.dtypes     = {}
        self.buffext    = "~"
        self.buffname   = None
        
    def open(self):
        """
        Description
        -----------
        Open a HIPO file to read, write (from scratch), or append data.
        IMPORTANT:  Make sure you add schema before opening a file to write!
        """
        if self.mode=="r":
            self.reader.open(self.filename)
            self.reader.readDictionary(self.dictionary)
        elif self.mode=="w": self.writer.open(self.filename)
        elif self.mode=="a" and self.buffname is None:

            # Open with reader first
            self.reader.open(self.filename)
            self.reader.readDictionary(self.dictionary)

            # Read all existing banks
            for schema in self.dictionary.getSchemaList():
                bank = hipopybind.Bank(self.dictionary.getSchema(schema))
                self.event.getStructure(bank)

            # Set group number to highest so far
            self.group = 0
            for schema in self.dictionary.getSchemaList():
                g = self.dictionary.getSchema(schema).getGroup()
                if self.group < g: self.group = g

            # Add existing banks to writer dictionary if in append mode
            if self.mode == "a": self.writer.addDictionary(self.dictionary)
            
            # Set buffername
            self.buffname = self.filename + self.buffext #NOTE: Separate code here so that you can call addSchema()

        elif self.mode=="a" and self.buffname is not None:
            # Now open with writer after adding schema to write
            self.writer.open(self.buffname)
            
    def flush(self):
        """
        Description
        -----------
        Write current HIPO writer buffer to file.
        """
        self.writer.flush()

    def close(self):
        """
        Parameters
        ----------
        mode : string, optional
            Default : "r"

        Description
        -----------
        Close osstream for an open file.
        """
        if self.mode=="r": pass #NOTE: Nothing to do here.
        if self.mode=="w":
            self.writer.close()
        if self.mode=="a":
            self.writer.close()
            shutil.copy(self.buffname,self.filename) #TODO: Check this
            os.remove(self.buffname) #TODO: Check this

    def goToEvent(self,event):
        """
        Parameters
        ----------
        event : int, required
            Integer number indicating event number in file (starts at 0)

        Returns
        -------
        boolean
            True if requested event exists, otherwise False

        Description
        -----------
        Move to requested HIPO event in a file in read mode.
        """
        self.status = self.reader.gotoEvent(event)
        self.reader.read(self.event) #TODO: This currently seg faults...
        return self.status

    def nextEvent(self):
        """
        Returns
        -------
        boolean
            True if next event exists else False

        Description
        -----------
        Move to next HIPO event from a file in read mode.
        """
        self.status = self.reader.next()
        self.reader.read(self.event)
        return self.status

    def addSchema(self, name, namesAndTypes, group=-1, item=1):
        """
        Parameters
        ----------
        name : string, required
            Bank name
        namesAndTypes : dictionary, required
            Map of column names to types ("D" : double, "F" : float, 
            "I" : int, "B" : byte, "S" : short, "L" : long)
        group : int, optional
            Group number for bank (unique)
            Default : -1
        item : int, optional
            Item number for bank (not unique)
            Default : 1

        Description
        -----------
        Add a schema structure to HIPO file writer dictionary for
        a bank you wish to write.  NOTE: Do this BEFORE opening the 
        file in write mode.
        """
        names = namesAndTypes.keys()
        types = namesAndTypes.values()
        schemaString = ",".join( ["/".join( [key,namesAndTypes[key]] ) for key in namesAndTypes] )
        if group <= self.group or group < 0:
            self.group += 1

        schema = hipopybind.Schema(name,max(self.group,group),item) #NOTE: Important to use this constructor here.
        schema.parse(schemaString)
        d = hipopybind.Dictionary()
        d.addSchema(schema)
        self.writer.addDictionary(d)

    def addEvent(self):
        """
        Description
        -----------
        Adds current hipo event to buffer and advances writer to next event.
        """
        self.writer.addEvent(self.event)

    def writeEvent(self):
        """
        Description
        -----------
        Writes current hipo event buffer to file.
        """
        self.writer.flush()

    def writeAllBanks(self):
        """
        Description
        -----------
        Write all existing banks to event for appending to file.
        """
        for schema in self.writer.getDictionary().getSchemaList():
            bank = hipopybind.Bank(self.writer.getDictionary().getSchema(schema))
            self.event.getStructure(bank)
            self.event.addStructure(bank)

    def writeBank(self, name, names, data, dtypes="D"):
        """
        Parameters
        ----------
        name : string, required
            Bank name
        names : list, required
            Column names
        data  : numpy.ndarray, required
            2D NumPy array of dimension (columns,rows)
        dtype : string, optional
            Data type ("D" : double, "F" : float, "I" : int, "B" : byte, "S" : short, "L" : long)
            Default : "D"

        Description
        -----------
        Fill an event bank with data and write to buffer.
        """
        schema = self.writer.getDictionary().getSchema(name)
        rows   = np.shape(data)[-1]
        bank   = hipopybind.Bank(schema,rows)

        # Add data to bank
        for idx, entry in enumerate(names):
            dtype = dtypes if len(dtypes)==1 else dtypes[idx]
            if dtype=="D":
                for i in range(rows):
                    bank.putDouble(entry,i,data[idx,i])
            elif dtype=="F":
                for i in range(rows):
                    bank.putFloat(entry,i,data[idx,i])
            elif dtype=="I":
                for i in range(rows):
                    bank.putInt(entry,i,data[idx,i])
            elif dtype=="B":
                for i in range(rows):
                    bank.putByte(entry,i,data[idx,i])
            elif dtype=="S":
                for i in range(rows):
                    bank.putShort(entry,i,data[idx,i])
            elif dtype=="L":
                for i in range(rows):
                    bank.putLong(entry,i,data[idx,i])
            else:
                raise TypeError

        # Add bank to event
        self.event.addStructure(bank)

    def newTree(self,bank,bankdict,group=None,item=None):
        """
        Parameters
        ----------
        bank : string, required
            Bank name
        bankdict : dictionary, required
            Dictionary of bank entry names to data types ("D", "F", "I")
        group : int, optional
            Group identifier for bank (must be unique)
            Default : None
        item : int, optional
            Item identifier for bank (does not have to be unique)
            Default : None

        Description
        -----------
        Mimics uproot newTree function.
        """
        group = self.group if group is None else group
        item  = self.item if item is None else item
        self.addSchema(bank,bankdict,group,item)
        self.dtypes[bank] = bankdict

    def extend(self,datadict):
        """
        Parameters
        ----------
        datadict : dictionary, required
            Dictionary of bank names to data arrays of shape (nEvents,nEntries,nRows)

        Description
        -----------
        Mimics uproot extend function. NOTE: dtype argument fixed until I figure out how to pass
        different types to C wrapper.
        """
        keys = list(datadict.keys())
        nEvents = len(datadict[keys[0]])

        # Write mode routine
        if self.mode == "w":
            for event in range(nEvents):
                for bank in datadict: # This requires datadict shape to be (nEvents,nNames,nRows)
                    self.writeBank(bank,list(self.dtypes[bank].keys()),datadict[bank][event],dtypes=list(self.dtypes[bank].values()))
                self.addEvent()
            self.writeEvent()

        # Append mode routine
        elif self.mode == "a":
            for event in range(nEvents):
                if not self.nextEvent():
                    print(" *** ERROR *** Tried to append more events than are in current file. Stopping.") #TODO: Implement logging and figure out how to append more events safely.
                    break
                for bank in datadict: # This requires datadict shape to be (nEvents,nNames,nRows)
                    self.writeBank(bank,self.dtypes[bank].keys(),datadict[bank][event],dtypes=list(self.dtypes[bank].values()))
                self.addEvent()
            self.writeEvent()

    def update(self,datadict):
        """
        Parameters
        ----------
        datadict : dictionary, required
            Dictionary of bank names to data arrays of shape (nEntries,nRows)

        Description
        -----------
        Append one set of event banks at a time and do not progress to the 
        next event automatically. NOTE: dtype argument fixed until I figure out how to pass
        different types to C wrapper.
        """
        # Append mode routine
        if self.mode == "a":
            for bank in datadict: # This requires datadict shape to be (nNames,nRows)
                self.writeBank(bank,self.dtypes[bank].keys(),datadict[bank],dtypes=list(self.dtypes[bank].values()))
            self.addEvent()
            self.writeEvent()

    def write(self):
        """
        Description
        -----------
        Alias for self.close()
        """
        self.close()

    def hasBank(self,bankName):
        """
        Parameters
        ----------
        bankName : string, required

        Description
        -----------
        Check if bank exists for current file.
        """
        return self.dictionary.hasSchema(bankName)

    def show(self):
        """
        Description
        -----------
        Print out all available bank names in open file.
        """
        print(self.dictionary)
    
    def showBank(self,bankName):
        """
        Parameters
        ---------
        bankName : string, required

        Description
        -----------
        Print out bank contents for current event.
        """
        print(self.dictionary.getSchema(bankName))

    def getBanks(self):
        """
        Returns
        -------
        list
            list of all bank names in the reader dictionary
        """
        return self.dictionary.getSchemaList()

    def readAllBanks(self):
        """
        Description
        -----------
        Read all existing banks to event for appending to file.
        """
        for schema in self.dictionary.getSchemaList():
            bank = hipopybind.Bank(self.dictionary.getSchema(schema))
            self.event.getStructure(bank)


    def readBank(self,bankName,verbose=False):
        """
        Parameters
        ----------
        bankName : string, required
        verbose : boolean, optional
            Print out loading message for each event if True

        Description
        -----------
        Setup to read bank contents for each event into memory.
        """
        if self.dictionary.hasSchema(bankName):
            bank = hipopybind.Bank(self.dictionary.getSchema(bankName))
            self.event.getStructure(bank)

    def getGroup(self):
        """
        Description
        -----------
        Get highest number group of all existing schema in reader for initiating file in append mode.
        """
        # Set group number to highest so far
        group = 0
        for schema in self.dictionary.getSchemaList():
            g = self.dictionary.getSchema(schema).getGroup()
            if group < g: group = g
        self.group = group
        return self.group


    def getEntries(self,bankName):
        """
        Parameters
        ----------
        bankName : string, required

        Description
        -----------
        Get number of entries in bank.  Make sure you read bank first 
        with readBank(bankName) method above.
        """
        return self.dictionary.getSchema(bankName).getEntries()

    def getNamesAndTypes(self,bankName):
        """
        Parameters
        ----------
        bankName : string, required

        Returns
        -------
        data : ctypes.c_char_p array
            ctypes c_char_p array containing the bank entries

        Description
        -----------
        Get a list of the entry names from the data table in the current event's bank.
        """
        bankdict = self.dictionary.getSchema(bankName).getSchemaString()
        bankdict = bankdict.split("}{")[1][:-1]
        bankdict = { entry.split("/")[0]:entry.split("/")[1] for entry in bankdict.split(",")}
        return bankdict
    
    def getNames(self,bankName):
        """
        Parameters
        ----------
        bankName : string, required

        Returns
        -------
        data : ctypes c_char_p array
            ctypes c_char_p array containing the bank entries

        Description
        -----------
        Get a list of the entry names from the data table in the current event's bank.
        """
        schema   = self.dictionary.getSchema(bankName)
        nEntries = schema.getEntries()
        return [schema.getEntryName(i) for i in range(nEntries)]

    def getTypes(self,bankName):
        """
        Parameters
        ----------
        bankName : string, required

        Returns
        -------
        data : ctypes c_char_p array containing the bank entries

        Description
        -----------
        Get a list of the entry types from the data table in the current event's bank.
        """
        dtypes = {1:"B", 2:"S", 3:"I", 4:"F", 5:"D", 8:"L" }
        schema   = self.dictionary.getSchema(bankName)
        nEntries = schema.getEntries()
        return [dtypes[schema.getEntryType(i)] for i in range(nEntries)]

    def getRows(self,bankName):
        """
        Parameters
        ----------
        bankName : string, required

        Description
        -----------
        Get number of rows in bank.  Make sure you read bank first 
        with readBank(bankName) method above.
        """
        bank = hipopybind.Bank(self.dictionary.getSchema(bankName))
        self.event.getStructure(bank)
        return bank.getRows()

    def getInts(self,bankName,item):
        """
        Parameters
        ----------
        bankName : string, required
        item : string, required
            Column name you wish to read in bank

        Returns
        -------
        data : ctypes int array
            ctypes int array containing the bank entries

        Description
        -----------
        Get a column of ints from the data table in the current event's bank.
        """
        bank = hipopybind.Bank(self.dictionary.getSchema(bankName))
        self.event.getStructure(bank)
        bankRows = bank.getRows()
        data = [bank.getInt(item,i) for i in range(bankRows)]
        return data

    def getFloats(self,bankName,item):
        """
        Parameters
        ----------
        bankName : string, required
        item : string, required
            Column name you wish to read in bank

        Returns
        -------
        data : cyptes float array
            ctypes float array containing the bank entries

        Description
        -----------
        Get a column of floats from the data table in the current event's bank.
        """
        bank = hipopybind.Bank(self.dictionary.getSchema(bankName))
        self.event.getStructure(bank)
        bankRows = bank.getRows()
        data = [bank.getFloat(item,i) for i in range(bankRows)]
        return data

    def getDoubles(self,bankName,item):
        """
        Parameters
        ----------
        bankName : string, required
        item : string, required
            Column name you wish to read in bank

        Returns
        -------
        data : ctypes double array
            ctypes double array containing the bank entries

        Description
        -----------
        Get a column of doubles from the data table in the current event's bank.
        """
        bank = hipopybind.Bank(self.dictionary.getSchema(bankName))
        self.event.getStructure(bank)
        bankRows = bank.getRows()
        data = [bank.getDouble(item,i) for i in range(bankRows)]
        return data


    def getShorts(self,bankName,item):
        """
        Parameters
        ----------
        bankName : string, required
        item : string, required
            Column name you wish to read in bank

        Returns
        -------
        data : ctypes short array
            ctypes short array containing the bank entries

        Description
        -----------
        Get a column of shorts from the data table in the current event's bank.
        """
        bank = hipopybind.Bank(self.dictionary.getSchema(bankName))
        self.event.getStructure(bank)
        bankRows = bank.getRows()
        data = [bank.getShort(item,i) for i in range(bankRows)]
        return data


    def getLongs(self,bankName,item):
        """
        Parameters
        ----------
        bankName : string, required
        item : string, required
            Column name you wish to read in bank

        Returns
        -------
        data : ctypes long array
            ctypes long array containing the bank entries

        Description
        -----------
        Get a column of longs from the data table in the current event's bank.
        """
        bank = hipopybind.Bank(self.dictionary.getSchema(bankName))
        self.event.getStructure(bank)
        bankRows = bank.getRows()
        data = [bank.getLong(item,i) for i in range(bankRows)]
        return data


    def getBytes(self,bankName,item):
        """
        Parameters
        ----------
        bankName : string, required
        item : string, required
            Column name you wish to read in bank

        Returns
        -------
        data : ctypes c_int array
            ctypes c_int array containing the bank entries

        Description
        -----------
        Get a column of bytes from the data table in the current event's bank.
        """
        bank = hipopybind.Bank(self.dictionary.getSchema(bankName))
        self.event.getStructure(bank)
        bankRows = bank.getRows()
        data = [bank.getByte(item,i) for i in range(bankRows)]
        return data


    def __iter__(self):
        return hipofileIterator(self)

class hipofileIterator:

    """
    Description
    -----------
    Iterator class for hipopy.hipopy.hipoFile class
    """

    def __init__(self,hipofile):
        self.hipofile = hipofile
        self.idx = 0

        if self.hipofile.mode != "w":
            self.hipofile.readAllBanks()#IMPORTANT!
            self.banks = self.hipofile.getBanks()
            self.verbose = False #NOTE: Not really necessary.
            self.items = {}
        
            # Read all requested banks
            for b in self.banks:
                self.hipofile.readBank(b,self.verbose)
                helper = self.hipofile.getNamesAndTypes(b) #NOTE: #TODO: This breaks down if you repeat with the file open.
                self.items[b] = helper

    def __next__(self):
        if self.hipofile.nextEvent(): #NOTE: #TODO: #DEBUGGING: Good for reading but need a different method for appending!
            self.idx += 1
            event = {}

            # Get bank data
            for bank in self.banks:
                for item in self.items[bank]:
                    data = []
                    if   self.items[bank][item]=="F": data = self.hipofile.getFloats(bank,item)
                    elif self.items[bank][item]=="I": data = self.hipofile.getInts(bank,item)
                    elif self.items[bank][item]=="D": data = self.hipofile.getDoubles(bank,item)
                    elif self.items[bank][item]=="L": data = self.hipofile.getLongs(bank,item)
                    elif self.items[bank][item]=="S": data = self.hipofile.getShorts(bank,item)
                    elif self.items[bank][item]=="B": data = self.hipofile.getBytes(bank,item)

                    # Add bank data to event dictionary
                    event[bank+"_"+item] = [np.array(data)]

            return event
        raise StopIteration

class hipochain:

    """
    Attributes
    ----------
    names : list
        List of file names in hipochain
    banks : list
        List of bank names to be read
    step : int
        Batch size for reading banks
    mode : string
        Currently fixed to always be in read mode ("r")
    verbose : boolean
        Currently fixed to always be False

    Description
    -----------
    Chains files together so they may be read continuously.
    """

    def __init__(self,names,banks=None,step=100,mode="r"):
        self.names   = names

        # Parse regex NOTE: Must be full or relative path from $PWD.  ~/... does not work.
        if type(self.names)==str:
            self.names = glob.glob(names)
        else:
            newnames = []
            for i in range(len(self.names)):
                files = glob.glob(self.names[i])
                if len(files)>0:
                    for file in files:
                        newnames.append(file)
            self.names = newnames

        self.banks   = banks
        self.step    = step
        self.mode    = "r"   #TODO: Does it make sense to just fix this?
        self.verbose = False #TODO: Do we really need this?

    def __iter__(self):
        return hipochainIterator(self)

class hipochainIterator:

    """
    Attributes
    ----------
    chain : hipopy.hipopy.hipochain
        Hipochain object overwhich to iterate
    idx : int
        Index of current file in hipochain
    counter : int
        Event counter for batching data
    file : hipopy.hipopy.hipoFile
        Current file in hipochain
    items : dict
        Dictionary of bank names to item names to read
    dict : dict
        Dictionary into which Hipo bank data is read

    Methods
    -------
    switchFile

    Description
    -----------
    Iterator for hipopy.hipopy.hipochain class
    """

    def __init__(self,chain):
        self.chain   = chain
        self.idx     = -1
        self.counter = 0
        self.file    = None
        self.items   = {}
        self.dict    = None

    def switchFile(self):
        """
        Description
        -----------
        Checks if next file in chain exists and then opens and reads requested banks if so.
        """
        # Open file
        self.idx += 1 #NOTE: Do this before everything below since we initiate at -1.
        if (self.idx>=len(self.chain.names)): return #NOTE: Sanity check
        self.file = hipofile(self.chain.names[self.idx],mode=self.chain.mode)
        self.file.open()
        
        if self.chain.banks is None: self.chain.banks = self.file.getBanks() #NOTE: This assumes all the files in the chain have the same banks.

        # Read all requested banks
        for b in self.chain.banks:
            self.file.readBank(b,self.chain.verbose)
            helper = self.file.getNamesAndTypes(b)
            self.items[b] = helper

    def __next__(self):
        """
        Description
        -----------
        Loops files reading requested banks if they exist 
        """

        if self.idx == -1: self.switchFile() # Load first file manually

        if self.idx<(len(self.chain.names)): #TODO: Check this condition.

            # Check if output array has been initialized
            if self.dict is None:
                self.dict = {}

            # Loop events in current file
            while self.file.nextEvent():

                # Get bank data
                for bank in self.chain.banks:
                    for item in self.items[bank]:
                        data = []
                        if   self.items[bank][item]=="F": data = self.file.getFloats(bank,item)
                        elif self.items[bank][item]=="I": data = self.file.getInts(bank,item)
                        elif self.items[bank][item]=="D": data = self.file.getDoubles(bank,item)
                        elif self.items[bank][item]=="L": data = self.file.getLongs(bank,item)
                        elif self.items[bank][item]=="S": data = self.file.getShorts(bank,item)
                        elif self.items[bank][item]=="B": data = self.file.getBytes(bank,item)

                        # Add bank data to batch dictionary
                        if not bank+"_"+item in self.dict.keys() : self.dict[bank+"_"+item] = [np.array(data)]
                        else: self.dict[bank+"_"+item].append(np.array(data))               

                # Check size of output array
                self.counter += 1
                if self.counter % self.chain.step == 0:
                    res       = self.dict
                    self.dict = None
                    return res

            # Switch the file AFTER you get through event loop above
            self.switchFile()

        # Final return for remainder
        if self.dict != None:
            res       = self.dict
            self.dict = None
            return res #TODO: Will this return last remainder that is not necessarily stepsize?
        
        # Final stop
        raise StopIteration
