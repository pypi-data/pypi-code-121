# Works with Atlas that contains 254 or less bundles... For more bundles fiberValidator should be uint16, not uint8

from Framework.Segmentation.SegmentationHandler import *
import Framework.CExtend.cfuncs as cfuncs

from Framework.Bundle import Bundle

import os
from pathlib import Path

pathname = os.path.dirname(__file__)
parent_path = str(Path(pathname).parents[1])

class Atlas(VisualizationBaseObject):
	def __init__(self, shaderDict, parent):
		super().__init__(parent, shaderDict[Bundle])
		self.identifier = VisualizationObject.Atlas

		self.fileName = 'Atlas'
		
		self.bundlesNames = []
		self.bundlesNFiber = []
		self.points = []
		self.colorTable = np.array([0.5,0.5,0.5,2.0], dtype=np.float32).reshape((1,4))

		self.bundlesData = []

		self.thresholdNames = []
		self.thresholds = None
		self.thresholdNFiber = []

		self.validBundles = []
		self.validBundlesIndex = []
		self.missingBundle = []
		self.missingThreshold = []

		# Ready to draw
		self.drawable = True

		self.boundingbox = BoundingBox(shaderDict, self, [0,0,0], [0,0,0])


	def addBundle(self, sPathList):

		newItems = len(self.children)

		for sPath in sPathList:
			if sPath in [k.path for k in self.children]:
				continue

			bundleHolder = Bundle(sPath, self.shader, self)
			bundleHolder.boundingbox.drawable = False

			self.children.append(bundleHolder)

		print("Loading ready:\nFiles added to Atlas:\t", [k.fileName for k in self.children[newItems:]])

		self.createSegmentationData()


	def removeBundle(self, bundleList):

		tmpFileNameList = [i.fileName for i in self.children]
		removedItems = sorted([tmpFileNameList.index(i) for i in bundleList], reverse=True)

		for rmIndex in removedItems:
			del self.children[rmIndex]

		# self.points = np.empty(self.points.size-removedPoints, dtype=np.float32)
		# np.concatenate([i.points for i in self.children], out=self.points)
		# # point bundles.points to atlas.points?

		# self.colorTable = np.empty(len(self.bundlesNames)*4, dtype=np.float32)
		# np.concatenate([i.colorTable for i in self.children], out=self.colorTable)			# Color for each Bundle

		# # We set the boundingbox parameters
		# x = self.points[0::3]
		# y = self.points[1::3]
		# z = self.points[2::3]

		# xmin, xmax = x.min(),x.max()
		# ymin, ymax = y.min(),y.max()
		# zmin, zmax = z.min(),z.max()
		
		# dims = np.array([xmax-xmin, ymax-ymin, zmax-zmin], dtype=np.float32)
		# center = np.array([xmin, ymin, zmin], dtype=np.float32)

		# self.boundingbox = BoundingBox(shaderDict, self, dims, center)

		print("Files removed from Atlas:\t", bundleList)

		self.createSegmentationData()


	def loadThresholdFile(self, thrFile):
		with open(thrFile) as file:
			lines = [line.rstrip('\n') for line in file]

			self.thresholdNames = []
			self.thresholds = np.empty(len([validLine for validLine in lines if len(validLine) != 0]), dtype=np.uint8)
			self.thresholdNFiber = []

			for l in lines:
				if len(l) == 0:
					continue

				name, threshold, nFiber = l.split()

				idx = len(self.thresholdNames)

				self.thresholdNames.append(name)
				self.thresholds[idx] = int(threshold)
				self.thresholdNFiber.append(int(nFiber))

		self.createSegmentationData()


	def calculateValidBundles(self):
		a = set(self.thresholdNames)
		b = self.bundlesNames

		onlyInA = a.difference(b)
		d = a.symmetric_difference(b)
		onlyInB = d.difference(a)

		self.validBundles = list(a.intersection(b))
		self.validBundlesIndex = sorted([self.bundlesNames.index(i) for i in self.validBundles])
		self.missingBundle = list(onlyInA)
		self.missingThreshold = list(onlyInB)


	def getValidBundles(self):
		validBundlesPacked = []

		for validBundleName in self.validBundles:
			validBundleFiberN = self.bundlesNFiber[self.bundlesNames.index(validBundleName)]
			validBundleHie = self.colorTable[self.bundlesNames.index(validBundleName)]
			validBundleThreshold = self.thresholds[self.thresholdNames.index(validBundleName)]

			validBundlesPacked.append((validBundleName, validBundleFiberN, validBundleHie, validBundleThreshold))

		return validBundlesPacked

	def getInvalidBundles(self):
		invalidBundlesPacked = []

		for invalidBundleName in self.missingBundle:

			validBundleFiberN = 0
			validBundleHie = 0
			validBundleThreshold = self.thresholds[self.thresholdNames.index(invalidBundleName)]

			invalidBundlesPacked.append((invalidBundleName, validBundleFiberN, validBundleHie, validBundleThreshold))

		for invalidBundleName in self.missingThreshold:

			validBundleFiberN = self.bundlesNFiber[self.bundlesNames.index(invalidBundleName)]
			validBundleHie = self.colorTable[self.bundlesNames.index(invalidBundleName)]
			validBundleThreshold = 0

			invalidBundlesPacked.append((invalidBundleName, validBundleFiberN, validBundleHie, validBundleThreshold))

		return invalidBundlesPacked




	def createSegmentationData(self):
		self.bundlesNames = [i for k in self.children for i in k.bundlesName]
		self.bundlesNFiber = [i for k in self.children for i in k.bundlesInterval[1:]-k.bundlesInterval[:-1]]
		self.points = [k.points[k.fiberSizes[:k.bundlesInterval[i]].sum()*3 : k.fiberSizes[:k.bundlesInterval[i+1]].sum()*3] for k in self.children for i in range(len(k.bundlesName))]

		self.colorTable = np.empty((len(self.bundlesNames)+1, 4), dtype=np.float32)
		np.concatenate([i.colorTable for i in self.children] + [np.array([0.5,0.5,0.5,2.0], dtype=np.float32).reshape((1,4))], out=self.colorTable)

		self.calculateValidBundles()

		self.fiber2Bundle = []

		totalSize = 0

		for i in  self.points:
			totalSize += i.size

		fiber2BundleHolder = np.empty(totalSize//3, dtype=np.uint8)

		offset = 0
		for i in range(len(self.points)):
			self.fiber2Bundle.append(fiber2BundleHolder[offset:offset+self.points[i].size//63])
			self.fiber2Bundle[-1][:] = i
			offset += self.points[i].size//3

		if not len(self.validBundlesIndex):
			return

		self.validPoints = np.concatenate([self.points[i] for i in self.validBundlesIndex])
		self.validFiber2Bundle = np.concatenate([self.fiber2Bundle[i] for i in self.validBundlesIndex])

		self.validThreshold = np.zeros(len(self.bundlesNames), dtype=np.uint8)

		for i in self.validBundlesIndex:
			self.validThreshold[i] = self.thresholds[self.thresholdNames.index(self.bundlesNames[i])]

		self.calculateBoundingBox()


	def calculateBoundingBox(self):

		# We set the boundingbox parameters
		x = self.children[0].points[0::3]
		y = self.children[0].points[1::3]
		z = self.children[0].points[2::3]

		xmin, xmax = x.min(),x.max()
		ymin, ymax = y.min(),y.max()
		zmin, zmax = z.min(),z.max()

		for bundle in self.children[1:]:
			x = bundle.points[0::3]
			y = bundle.points[1::3]
			z = bundle.points[2::3]

			xmin_i, xmax_i = x.min(),x.max()
			ymin_i, ymax_i = y.min(),y.max()
			zmin_i, zmax_i = z.min(),z.max()

			if xmin_i < xmin:
				xmin = xmin_i
			if xmax_i > xmax:
				xmax = xmax_i

			if ymin_i < ymin:
				ymin = ymin_i
			if ymax_i > ymax:
				ymax = ymax_i

			if zmin_i < zmin:
				zmin = zmin_i
			if zmax_i > zmax:
				zmax = zmax_i

		dims = np.array([xmax-xmin, ymax-ymin, zmax-zmin], dtype=np.float32)
		center = np.array([xmin, ymin, zmin], dtype=np.float32)

		self.boundingbox.updateBBModel(dims, center)


	def loadAndApplyMatrix(self, matrixFile):
		extension = matrixFile.split('.')[-1]

		# numpy matrix file
		if extension == 'npy':
			transform = Bundle.loadNumpyMatrix(matrixFile)

		# brain visa (trm) matrix file
		elif extension == 'trm':
			transform = Bundle.loadTrmMatrix(matrixFile)

		# Unsopported file
		else:
			raise TypeError('Unsupported matrix file.', extension)

		for child in self.children:
			if isinstance(child, Bundle):
				child.applyMatrix(transform)

		self.createSegmentationData()



class AtlasBasedParallelSegmentation(SegmentationHandler):
	fiberLengthTimes3 = 21*3

	def __init__(self, bundle, shaderDict):
		super().__init__(bundle, shaderDict)

		self.segmentationIdentifier = SegmentationTypes.AtlasBased
		
		self.fileName = 'Atlas based segmentation' # temporal

		self.atlas = Atlas(shaderDict, self)

		self.alpha = 0.8

		self.colorTableTexture = None
		self._loadColorTexture()

		self.configFiberValidator()

		# Creates VBOs & an EBO, then populates them with the point, normal and color data. The elements data goes into the EBO
		self._loadBuffers()
		self.buildVertex2Fiber()
		self.vboAndLinkVertex2Fiber()

		# Check if bundle has fixed point size per fiber (21 vertex per fiber)
		if (self.fiberSizes != 21).sum():
			print('Resampling...')
			self.fixedPoints = np.empty(self.curvescount*self.fiberLengthTimes3, dtype=np.float32)
			cfuncs.reSampleBundle(
				self.points.ctypes.data, 
				self.fiberSizes.ctypes.data, 
				self.curvescount, 
				self.fixedPoints.ctypes.data,
				self.fiberLengthTimes3//3)
			print('Done.')
		else:
			self.fixedPoints = self.points

		self.segmentedBundles = []
		self.validBundles = []

		self.boundingbox = BoundingBox(shaderDict, self, bundle.boundingbox.dims, bundle.boundingbox.center)


	def cleanOpenGL(self):
		super().cleanOpenGL()

		glDeleteTextures([self.colorTableTexture])



	def defaultFiberValidator(self):
		return np.zeros(self.validFiberTexDims[1]*self.validFiberTexDims[0], dtype=np.uint8)


	def segmentMethod(self):

		self.fiberValidator[:self.curvescount] = len(self.atlas.bundlesNames)
		self.validBundles = self.atlas.validBundles
		
		self.updateColorTexture()

		cfuncs.AtlasBasedSegmentation(
			self.atlas.validPoints.ctypes.data,					# ctypes.c_void_p,			# float *atlas_data				vector with all the 3d points for the atlas
			self.atlas.validPoints.size,						# ctypes.c_int,				# unsigned int atlas_data_size	size of the vector with all the points for the atlas
			self.fixedPoints.ctypes.data,						# ctypes.c_void_p,			# float *subject_data 			vector with all the 3d points for the subject
			self.fixedPoints.size,								# ctypes.c_int,				# unsigned int subject_data_size 	size of the vector with all the points for the subject
			self.fiberLengthTimes3, 							# ctypes.c_int,				# unsigned short int ndata_fiber	number of points per fiber (*3) so 21 points = 63
			self.atlas.validThreshold.ctypes.data,				# ctypes.c_void_p,			# unsigned char *thresholds		vector with the thresholds for each fascicle on the atlas
			self.atlas.validFiber2Bundle.ctypes.data,			# ctypes.c_void_p,			# unsigned int *bundle_of_fiber	vector of atlas_points_size with id for the fascicle that correspondence
			self.fiberValidator.ctypes.data)					# ctypes.c_void_p)			# unsigned char *assignment 		size nfibers_subject. And all data set to 254 - result vector

		self.segmentedBundles = [(self.atlas.bundlesNames[self.atlas.validBundlesIndex[i]], (self.fiberValidator[:self.curvescount] == i).sum(), i) 
									for i in range(len(self.atlas.validBundles)) 
									if (self.fiberValidator[:self.curvescount] == i).sum() != 0]

		# np.save("D:/Desktop/labels", self.fiberValidator[:self.curvescount])


	def updateAtlas(self, newBundles=None, deleteBundles=None, thresholdFile=None, applyMatrixFile=None):
		if newBundles:
			self.atlas.addBundle(newBundles)

		if deleteBundles:
			self.atlas.removeBundle(deleteBundles)

		if thresholdFile:
			self.atlas.loadThresholdFile(thresholdFile)

		if applyMatrixFile:
			self.atlas.loadAndApplyMatrix(applyMatrixFile)


	def _loadColorTexture(self):
		''' It generates a texture (if not already). Then makes the texture0 the active one and loads the color table as a 1D texture.

		Parameters
		----------
		None

		Returns
		-------
		None

		'''
		maxTexDim = glGetIntegerv(GL_MAX_TEXTURE_SIZE)

		if maxTexDim*maxTexDim < len(self.atlas.bundlesNames)+1:
			raise ValueError('To many bundles inside the atlas... Color texture not big enought.')
		self.validBundleColorTexDims = findIntegersMultiplierFor(len(self.atlas.bundlesNames)+1, maxTexDim)

		if self.colorTableTexture == None:
			self.colorTableTexture = glGenTextures(1)

		glActiveTexture(GL_TEXTURE0)
		glBindTexture(GL_TEXTURE_2D, self.colorTableTexture)
		
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
		
		bgColor = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
		glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, bgColor)
		
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

		# glTexImage1D(GL_TEXTURE_1D, 0, GL_RGBA, 1, 0, GL_RGBA, GL_FLOAT, self.atlas.colorTable.flatten())
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, *self.validBundleColorTexDims, 0, GL_RGBA, GL_FLOAT, self.atlas.colorTable.flatten())


	def updateColorTexture(self):
		maxTexDim = glGetIntegerv(GL_MAX_TEXTURE_SIZE)

		if maxTexDim*maxTexDim < len(self.atlas.bundlesNames)+1:
			raise ValueError('To many bundles inside the atlas... Color texture not big enought.')
		self.validBundleColorTexDims = findIntegersMultiplierFor(len(self.atlas.bundlesNames)+1, maxTexDim)

		glActiveTexture(GL_TEXTURE0)
		glBindTexture(GL_TEXTURE_2D, self.colorTableTexture)

		# glTexImage1D(GL_TEXTURE_2D, 0, GL_RGBA, len(self.atlas.bundlesNames)+1, 0, GL_RGBA, GL_FLOAT, self.atlas.colorTable.flatten())
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, *self.validBundleColorTexDims, 0, GL_RGBA, GL_FLOAT, self.atlas.colorTable.flatten())


	def _loadBuffers(self):
		''' It generates a VAO, VBO and EBO.
		It populates them with the vertex, normal and colors (the VBO), also the elements (the EBO).

		It finishes when the buffers are linked with attributes on the vertex shader.
		
		Parameters
		----------
		None

		Returns
		-------
		None

		'''

		# Reference for vbos, ebos and attribute ptrs
		self.vao = glGenVertexArrays(1)
		glBindVertexArray(self.vao)

		# self.ebo = glGenBuffers(1)

		# VBO positions
		glBindBuffer(GL_ARRAY_BUFFER, self.vbo[0])

		positionAttribute =	self.shader[0].attributeLocation('vertexPos')
		glEnableVertexAttribArray(positionAttribute)
		glVertexAttribPointer(positionAttribute,3, GL_FLOAT, GL_FALSE, 0, None)

		# VBO normals
		glBindBuffer(GL_ARRAY_BUFFER, self.vbo[1])

		normalAttribute =	self.shader[0].attributeLocation('vertexNor')
		glEnableVertexAttribArray(normalAttribute)
		glVertexAttribPointer(normalAttribute,	3, GL_FLOAT, GL_FALSE, 0, None)

		# EBO
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)



	def exportBundleFile(self, outfile):
		if len(self.segmentedBundles) == 0:
			return

		bundlesSelected = np.array([i[2] for i in self.segmentedBundles], dtype=np.uint8)

		cfuncs.AtlasBasedSegmentationExportbundlesdata(
			(outfile+'data').encode('utf-8'),
			len(self.segmentedBundles),
			bundlesSelected.ctypes.data,
			self.fiberSizes.ctypes.data,
			self.points.ctypes.data,
			self.fiberSizes.size,
			self.fiberValidator.ctypes.data)

		# wrtie minf file
		minf = """attributes = {\n    'binary' : 1,\n    'bundles' : %s,\n    'byte_order' : 'DCBA',\n    'curves_count' : %s,\n    'data_file_name' : '*.bundlesdata',\n    'format' : 'bundles_1.0',\n    'space_dimension' : 3\n  }\n"""

		bundlesstr = []
		offset = 0

		for name, bundleSize, notUsed in self.segmentedBundles:
			bundlesstr.append(name)
			bundlesstr.append(offset)
			offset += bundleSize
		
		bundlesstr = str(bundlesstr)
		bundlesstr = bundlesstr[0] + ' ' + bundlesstr[1:-1] + ' ' + bundlesstr[-1]

		with open(outfile, 'w') as file:
			file.write( minf % ( bundlesstr, offset ) )


	def loadUniforms(self):
		super().loadUniforms()

		glUniform1i(self.shader[self.selectedShader].glGetUniformLocation('notAssigned'), len(self.validBundles))

		glUniform1i(self.shader[self.selectedShader].glGetUniformLocation('colorTable'), 0)
		glUniform1i(self.shader[self.selectedShader].glGetUniformLocation('fiberValidator'), 1)


	@propagateToChildren
	@drawable
	@config
	def draw(self):
		glActiveTexture(GL_TEXTURE0)
		glBindTexture(GL_TEXTURE_2D, self.colorTableTexture)

		glActiveTexture(GL_TEXTURE1)
		glBindTexture(GL_TEXTURE_2D, self.validFiberTexture)

		# Collided fiber
		glUniform1f(self.shader[self.selectedShader].glGetUniformLocation("alpha"), 5.0)
		glDrawElements(GL_LINE_STRIP, self.eboSize, GL_UNSIGNED_INT, None)
	
		# Transparent fiber
		if self.alpha >= 0.01:
			glEnable(GL_BLEND)
			glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
			glUniform1f(self.shader[self.selectedShader].glGetUniformLocation("alpha"), self.alpha)
			glDrawElements(GL_LINE_STRIP, self.eboSize, GL_UNSIGNED_INT, None)
			glDisable(GL_BLEND)

		self.boundingbox.draw()


	def createProgram():
		''' Anonymous function.
		Default shader program for atlas segmentation.
		It creates the shader programs for this specific class and returns the handler.
		'''

		vertexGLSL = [os.path.join(parent_path,'shaders','atlasbasedsegmentation.vs')]
		fragmentGLSL = [os.path.join(parent_path,'shaders','standardFragmentShader.fs')]
		geometryGLSL = [os.path.join(parent_path,'shaders','atlasbasedsegmentation.gs')]
		return [Shader(vertexGLSL, fragmentGLSL, geometryGLSL)]
