
import array

class Ring:
    def __init__(self, size):
        self._maxSize=size  #Array's max size
        self._readOffset=0  #Array's read offset pos
        self._writeOffset=0 #Array's write offseet pos
        self._ringBuffer=[None]*self._maxSize   #Init array
        self._valueCount=0  #Total this array's value count

    '''
        Get this buffer's size
    '''
    def getSize(self):
        return self._maxSize

    '''
        Total count with value in the buffer
    '''
    def getCount(self):
        return self._valueCount

    '''
        Judge this buffer is full
    '''
    def IsFull(self):
        if self._valueCount== self._maxSize:
            return True
        return False
    
    '''
        Judge this buffer is empty
    '''
    def IsEmpty(self):
        if self._valueCount==0:
            return True
        return False

    '''
        Push value in the array
    '''
    def Push(self,value):
        if self._writeOffset<self._maxSize:
            if self._ringBuffer[self._writeOffset]==None:
                self._ringBuffer[self._writeOffset]=value
                self._valueCount+=1
                self._writeOffset+=1
                if self._writeOffset>=self._maxSize:
                    self._writeOffset=0
                #if write offset equals read offset and the array's index is full after read pos,set write offset is zero
                if self._writeOffset==self._readOffset:
                    if self._readOffset > 0:
                        if self._maxSize - self._readOffset -1  == self._valueCount:
                            self._writeOffset=0
                return True
        return False

    '''
        pop the array's value by offset
    '''
    def Pop(self):
        if self._readOffset<self._maxSize:
            result=self._ringBuffer[self._readOffset]
            if result != None:
                self._ringBuffer[self._readOffset]=None
                self._valueCount-=1
                self._readOffset+=1
                #if array after read offset is full
                if self._maxSize - self._readOffset - 1 == self._valueCount:
                    #if array before read offset is full
                    if self._writeOffset==0 and self._ringBuffer[0] == None:
                        #set write offset is read offset
                        self._writeOffset=self._readOffset
                if self._readOffset>=self._maxSize:
                    self._readOffset=0
                return result
        return False

    '''
        clear the array's value 
    '''
    def Clear(self):
        self._ringBuffer=None
        self._readOffset=0
        self._maxSize=0
        self._writeOffset=0
        self._valueCount=0

    