import env
from dcclab import *
import unittest
import os

class TestMovieFile(env.DCCLabTestCase):
    def testInit(self):
        self.assertIsNotNone(MovieFile(self.dataFile("testMovie.mov")))

    def testReadImageData(self):
        movie = MovieFile(self.dataFile("testMovie.mov"))
        timeData = movie.timeSeriesData()
        self.assertIsNotNone(timeData)
        self.assertTrue(len(timeData.shape) == 4)

    def testWriteImageDataAsAVI(self):
        movie = MovieFile(self.dataFile("testMovie.mov"))
        timeData = movie.timeSeriesData()
        tmpFile = self.tmpFile("output.avi")
        movie.save(tmpFile, timeData)
        self.assertTrue(Path(tmpFile).exists())
        self.assertTrue(os.path.getsize(tmpFile) > 0)

    def testWriteImageDataAsAVINoExplicitRead(self):
        movie = MovieFile(self.dataFile("testMovie.mov"))
        tmpFile = self.tmpFile("output.avi")
        movie.save(tmpFile)
        self.assertTrue(os.path.exists(tmpFile))
        self.assertTrue(os.path.getsize(tmpFile) > 0)

    def testWriteImageDataAsMOVNoExplicitRead(self):
        movie = MovieFile(self.dataFile("testMovie.mov"))
        self.assertIsNotNone(movie.frameRate)
        tmpFile = self.tmpFile("output2.mov")
        movie.save(tmpFile)
        self.assertTrue(os.path.exists(tmpFile))
        self.assertTrue(os.path.getsize(tmpFile) > 0)
        movieSaved = MovieFile(tmpFile)

    def testOsOpenAPI(self):
        file = open(self.dataFile("testMovie.raw"),"rb")
        self.assertIsNotNone(file)
        file.close()


    def testOsReadChunk(self):
        file = open(self.dataFile("testMovie.raw"),"rb")
        data = file.read(1000)
        self.assertIsNotNone(data)
        self.assertTrue(len(data) == 1000)
        file.close()

    def testOsReadLargeChunk(self):
        file = open(self.dataFile("testMovie.raw"),"rb")
        data = file.read(1024*512*3)
        self.assertIsNotNone(data)
        self.assertTrue(len(data) == 1024*512*3)
        file.close()

    def testOsReadLargeChunk(self):
        try:
            file = open(self.dataFile("testMovie.raw"),"rb")

            width = 1024
            height = 512
            spp = 3
            dt = np.dtype('int16').newbyteorder('<')
            bpp = dt.itemsize
            size = height*width*spp*bpp
            data = file.read(size)

            self.assertTrue(bpp == 2)
            self.assertIsNotNone(data)
            self.assertTrue(len(data) == size)

            numpyArray = np.frombuffer(data,dtype=dt)
            numpyArray.reshape(width, height, spp)
        except:
            self.fail("Exception")
        finally:
            file.close()

    def testReadRaw(self):
        sampleType = np.dtype('uint16').newbyteorder('<')
        frameShape = (1024,512,1)
        movie = MovieFile(self.dataFile("testMovie.raw"),
                          frameShape=frameShape,
                          sampleType=sampleType)

        self.assertIsNotNone(movie.cachedData)
        self.assertIsNotNone(movie.cachedData.shape == frameShape)

    def testReadRawLater(self):
        movie = MovieFile(self.dataFile("testMovie.raw"))
        movie.sampleType = np.dtype('uint16').newbyteorder('<')
        movie.frameShape = (1024,512,1)

        movie.beginReading()
        try:
            while (1):
                self.assertIsNotNone(movie.sampleType)
                frame = movie.appendNextFrame()
                self.assertIsNotNone(movie.sampleType)
                if frame is None:
                    break
                self.assertTrue(frame.shape == (1024,512,1),frame.shape)
        except:
            self.fail("Exception when reading")
        finally:
            movie.endReading()
        self.assertIsNotNone(movie.cachedData)

    def testReadRawWriteMov(self):
        sampleType = np.dtype('uint16').newbyteorder('<')
        frameShape = (1024,512,1)
        movie = MovieFile(self.dataFile("testMovie.raw"),
                          frameShape=frameShape,
                          sampleType=sampleType)
        movie.frameRate = 3.0
        self.assertIsNotNone(movie.cachedData)
        movie.save("/tmp/movie.mov")

    def testReadRawWriteAVI(self):
        sampleType = np.dtype('uint16').newbyteorder('<')
        frameShape = (1024, 512,1)
        movie = MovieFile(self.dataFile("testMovie.raw"),
                          frameShape=frameShape,
                          sampleType=sampleType)
        movie.frameRate = 3.0
        self.assertIsNotNone(movie.cachedData)
        movie.save("/tmp/movie.avi")

    def testReadRawLaterWriteAVI(self):
        movie = MovieFile(self.dataFile("testMovie.raw"))
        movie.sampleType = np.dtype('uint16').newbyteorder('<')
        movie.frameShape = (1024,512,1)
        movie.beginReading()
        try:
            while (1):
                frame = movie.appendNextFrame()
                if frame is None:
                    break
                self.assertTrue(frame.shape == (1024,512,1),frame.shape)
                self.assertTrue(movie.frameSize)
        except:
            self.fail("Exception when reading")
        finally:
            movie.endReading()
        self.assertIsNotNone(movie.cachedData)
        movie.frameRate = 10.0
        movie.save("/tmp/movie.avi")

    def testScientificaINI(self):
        self.assertTrue(os.path.exists(self.dataFile("testMovie.raw")))
        self.assertTrue(os.path.exists(self.dataFile("testMovie.ini")))
        movie = MovieFile(self.dataFile("testMovie.raw"))
        self.assertTrue(movie.discoverRawFormat() == 'scientifica')
        self.assertTrue(movie.frameRate == 30)
        self.assertTrue(movie.width == 1024)
        self.assertTrue(movie.height == 512)
        self.assertTrue(movie.sampleType == np.uint16)


if __name__ == '__main__':
    unittest.main()
