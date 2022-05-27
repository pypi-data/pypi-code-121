from .imageFile import *
from .pathPattern import *
import os
import cv2
import re

class MovieFile(ImageFile):
    def __init__(self, path:str, frameShape=None, sampleType=None, frameRate=None):
        super(MovieFile, self).__init__(path)
        self.path = path
        self.frameRate = frameRate
        self.frameShape = frameShape
        self.sampleType = sampleType
        self.rawFormat = 'scientifica' # dcclab
        self.movieHandle = None
        self.videoWriter = None
        self.cachedData = None
        try:
            self.cachedData = self.timeSeriesData()
        except:
            pass

    @property
    def isUsingOpenCV(self):
        return isinstance(self.movieHandle, cv2.VideoCapture)

    @property
    def bytesPerSample(self):
        return self.sampleType.itemsize

    @property
    def samplesPerPixel(self):
        return self.frameShape[2]

    @property
    def frameSize(self):
        return self.frameShape[0]*self.frameShape[1]*self.frameShape[2]*self.bytesPerSample
    
    def save(self, path, timeData = None):
        if timeData is None:
            timeData = self.cachedData

        self.beginWriting(path, timeData)
        for i in range(timeData.shape[3]):
            timestepData = timeData[:,:,:,i].astype(np.uint8)
            timestepData.squeeze()
            self.writeNextFrame(timestepData)
        self.endWriting()

    def timeSeriesData(self):
        if self.cachedData is None:
            self.beginReading()
            try:
                while (1):
                    if self.appendNextFrame() is None:
                        break
            finally:
                self.endReading()

        return self.cachedData

    def beginReading(self):
        self.cachedData = None
        if PathPattern(self.path).extension == 'raw':
            if self.rawFormat is None:
                self.rawFormat = self.discoverRawFormat()

            self.movieHandle = open(self.path, "rb")
        else:
            self.movieHandle = cv2.VideoCapture(self.path)
            self.frameRate = self.movieHandle.get(cv2.CAP_PROP_FPS)

    def readNextFrame(self) -> np.ndarray:
        frameData = None
        if self.isUsingOpenCV:
            success, frameData = self.movieHandle.read()
            if self.frameShape is None:
                self.frameShape = frameData.shape
        else:
            if (self.frameShape is None) or (self.sampleType is None):
                raise ValueError("Not enough information: You must set frameShape and sampleType")

            if self.rawFormat is None:
                self.rawFormat = self.discoverRawFormat()

            if self.rawFormat == 'scientifica':
                frameData = self.readRawScientificaFrame()
            elif self.rawFormat == 'dcclab':
                frameData = self.readRawDCCLabFrame()
            else:
                raise ValueError("Invalid raw format {0}: scientifica or dcclab".format(self.rawFormat))
        return frameData

    def discoverRawFormat(self) -> str:
        (baseName, _) = os.path.splitext(self.path)
        iniPath = "{0}.ini".format(baseName)
        if os.path.exists(iniPath):
            file = open(iniPath)
            for line in file:
                match = re.search(r"x\.pixels\s+=\s+(\d+)", line)
                if match is not None:
                    self.width = int(match.groups()[0])
                match = re.search(r"y\.pixels\s+=\s+(\d+)", line)
                if match is not None:
                    self.height = int(match.groups()[0])
            
            self.frameRate = 30
            self.sampleType = np.uint16
            file.close()

            return 'scientifica'
        else:
            return 'dcclab'

    def readRawScientificaFrame(self) -> np.ndarray:
        frameData = None
        binaryData = self.movieHandle.read(self.frameSize)
        if len(binaryData) == self.frameSize:
            frameData = np.frombuffer(binaryData,dtype=self.sampleType)
            # Data is stored y first, then x, interleaved channels
            frameData = np.reshape(frameData, (self.frameShape[1],self.frameShape[0],self.frameShape[2]))
            # Swap after reading
            frameData = frameData.swapaxes(0,1)

        return frameData

    def readRawDCCLabFrame(self) -> np.ndarray:
        frameData = None
        binaryData = self.movieHandle.read(self.frameSize)
        if len(binaryData) == self.frameSize:
            frameData = np.frombuffer(binaryData,dtype=self.sampleType)
            # Data is stored x,y interleaved channels
            frameData = np.reshape(frameData, (self.frameShape[0],self.frameShape[1],self.frameShape[2]))

        return frameData

    def appendNextFrame(self) -> np.array:
        frameData = self.readNextFrame()

        if frameData is not None:
            frameDataExpanded = np.expand_dims(frameData, 3)
            if self.cachedData is None:
                self.cachedData = frameDataExpanded
            else:
                self.cachedData = np.concatenate((self.cachedData,frameDataExpanded),3)
        
        return frameData

    def endReading(self):
        if self.isUsingOpenCV:
            self.movieHandle.release()
            self.movieHandle = None
        else:
            self.movieHandle.close()

    def beginWriting(self, path, frameData):
        if self.frameRate is None:
            raise ValueError("No frame rate determined. You must set frameRate")

        width, height, channels, timeSteps = frameData.shape

        fourcc = 0 # no compression
        pathPattern = PathPattern(path)
        if pathPattern.extension == 'mov' or pathPattern.extension == 'mp4':
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        self.videoWriter = cv2.VideoWriter(path, fourcc, self.frameRate, (width, height))

    def writeNextFrame(self, frame):
        if frame.shape == self.frameShape:
            if frame.shape[2] == 1:
                frame = np.concatenate([frame, frame, frame], 2)

            # OpenCV considers y,x,c, not x,y,c
            # Most supported formats want 8 bit values
            frame = np.swapaxes(frame, 0,1).astype(np.uint8)
            self.videoWriter.write(frame)
        else:
            raise ValueError("Wrong shape: {0} expected {1}".format(frame.shape, self.frameShape))

    def endWriting(self):
        self.videoWriter.release()
