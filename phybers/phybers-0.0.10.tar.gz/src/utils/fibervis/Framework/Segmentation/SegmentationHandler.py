''' to-do
		configOpengl
		exportbundlefile
'''

from Framework.VisualizationBaseObject import *
from Framework.Bundle import Bundle
from Framework.BoundingBox import BoundingBox
import Framework.CExtend.cfuncs as cfuncs

from Framework.Tools.utilities import findIntegersMultiplierFor

import math

# DELETE
from Framework.Tools.performance import *
#
import os
from pathlib import Path

pathname = os.path.dirname(__file__)
parent_path = str(Path(pathname).parents[1])

class SegmentationHandler(VisualizationBaseObject):
	'''
	'''

	def __init__(self, bundle, shaderDict):
		'''
		'''
		super().__init__(bundle, shaderDict)
		self.identifier = VisualizationObject.Segmentation
		self.segmentationIdentifier = None

		if not isinstance(bundle, Bundle):
			raise TypeError('Not a bundle.')

		# self.parent = bundle
		# self.shader = shaderProgram[type(self)]

		# OpenGL buffer references
		self.vao = 0
		self.vbo = bundle.vbo
		self.ebo = bundle.ebo

		# Atlas color table, loads when the atlas is loaded
		self.colorTableTexture = bundle.colorTableTexture
		self.validBundleColorTexDims = bundle.validBundleColorTexDims

		# Matrixs
		self.model = bundle.model
		
		self.inverseModel = bundle.inverseModel
		self.scaleMat = bundle.scaleMat
		self.translateMat = bundle.translateMat
		self.rotationMat = bundle.rotationMat

		self.points = bundle.points
		# self.elements = np.copy(bundle.elements)
		self.eboSize = bundle.elements.size
		self.fiberSizes = bundle.fiberSizes

		self.bundlesName = bundle.bundlesName
		self.curvescount = bundle.curvescount
		self.bundlesStart = np.append(bundle.bundlesStart, self.curvescount).astype(np.int32)

		# Flags
		self.drawable = False


	def cleanOpenGL(self):
		print('Cleaning object: ', self)
		glDeleteVertexArrays(1, [self.vao])

		glDeleteBuffers(1, [self.vboV2F])

		glDeleteTextures([self.validFiberTexture])

		self.clean = True


	def configOpenGL(self):
		pass


	# @averageTimeit
	@timeit
	def segmentSubject(self):
		''' This function has to be implemented by all segmentation subclass.

		It will create an ebo or load the data that segments the bundle using an atlas.

		It also has to set the colors for the segmentation, by calling self._loadColorTexture()
		'''
		self.segmentMethod()
		
		self.updateFiberValidator()


	def segmentMethod(self):
		''' This function has to be implemented by all segmentation subclass.

		It will create an ebo or load the data that segments the bundle using an atlas.

		It also has to set the colors for the segmentation, by calling self._loadColorTexture()
		'''
		raise TypeError('Segmentation method is not implemented in class: ', type(self))


	def updateFiberValidator(self):
		glActiveTexture(GL_TEXTURE1)
		glBindTexture(GL_TEXTURE_2D, self.validFiberTexture)

		# glTexSubImage2D(GL_TEXTURE_2D, 0, GL_R8UI, *self.validFiberTexDims, 0, GL_RED_INTEGER, GL_UNSIGNED_BYTE, self.fiberValidator)
		glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, *self.validFiberTexDims, GL_RED_INTEGER, GL_UNSIGNED_BYTE, self.fiberValidator)


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

		# VBO position
		glBindBuffer(GL_ARRAY_BUFFER, self.vbo[0])
		
		positionAttribute =	self.shader[0].attributeLocation('vertexPos')
		glEnableVertexAttribArray(positionAttribute)
		glVertexAttribPointer(positionAttribute,3, GL_FLOAT, GL_FALSE, 0, None)

		# VBO normals
		glBindBuffer(GL_ARRAY_BUFFER, self.vbo[1])
		
		normalAttribute =	self.shader[0].attributeLocation('vertexNor')
		glEnableVertexAttribArray(normalAttribute)
		glVertexAttribPointer(normalAttribute,	3, GL_FLOAT, GL_FALSE, 0, None)

		# VBO colors
		glBindBuffer(GL_ARRAY_BUFFER, self.vbo[2])

		colorAttribute =	self.shader[0].attributeLocation('vertexCol')
		glEnableVertexAttribArray(colorAttribute)
		glVertexAttribPointer(colorAttribute,	1, GL_INT, GL_FALSE, 0, None)
		
		# EBO
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)


	def loadUniforms(self):
		'''This function is called always before drawing. It makes sure that the current class will be visualized with the uniforms specified for it.

		Parameters
		----------
		None

		Returns
		-------
		None

		'''
		
		glUniformMatrix4fv(self.shader[self.selectedShader].glGetUniformLocation("M"), 1, GL_TRUE, self.model.getA())

		glUniform1i(self.shader[self.selectedShader].glGetUniformLocation('texture1DMax'), self.validFiberTexDims[0])
		glUniform1i(self.shader[self.selectedShader].glGetUniformLocation('bundleTex1DMax'), self.validBundleColorTexDims[0])


	def buildVertex2Fiber(self):
		self.vertex2Fiber = np.empty(self.parent.points.size//3, dtype=np.int32)

		offset = 0
		for i in range(len(self.parent.fiberSizes)):
			self.vertex2Fiber[offset:offset+self.parent.fiberSizes[i]] = i
			offset += self.parent.fiberSizes[i]


	def vboAndLinkVertex2Fiber(self):
		glBindVertexArray(self.vao)

		self.vboV2F = glGenBuffers(1)

		glBindBuffer(GL_ARRAY_BUFFER, self.vboV2F)
		glBufferData(GL_ARRAY_BUFFER, self.vertex2Fiber.nbytes, self.vertex2Fiber, GL_STATIC_DRAW)

		# Enable attributes
		v2FAttribute = self.shader[0].attributeLocation('vertex2Fib')

		# Connect attributes
		glEnableVertexAttribArray(v2FAttribute)
		glVertexAttribPointer(v2FAttribute, 1, GL_INT, GL_FALSE, 0, None)


	def defaultFiberValidator(self):
		return np.ones(self.validFiberTexDims[1]*self.validFiberTexDims[0], dtype=np.uint8)


	def configFiberValidator(self):
		maxTexDim = glGetIntegerv(GL_MAX_TEXTURE_SIZE)

		if maxTexDim*maxTexDim < self.curvescount:
			raise ValueError('Fiber data set to big for GPU, need to change rander mode...')
		self.validFiberTexDims = (maxTexDim, int(math.ceil(self.curvescount/maxTexDim)))
		# self. validFiberTexDims = findIntegersMultiplierFor(self.curvescount, maxTexDim)

		self.fiberValidator = self.defaultFiberValidator()

		self.validFiberTexture = glGenTextures(1)

		glActiveTexture(GL_TEXTURE1)

		glBindTexture(GL_TEXTURE_2D, self.validFiberTexture)

		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)

		bgColor = np.array([1,1,1,1], dtype=np.float32)
		glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, bgColor)

		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

		glTexImage2D(GL_TEXTURE_2D, 0, GL_R8UI, self.validFiberTexDims[0], self.validFiberTexDims[1], 0, GL_RED_INTEGER, GL_UNSIGNED_BYTE, self.fiberValidator)



	def setAlpha(self, newAlpha):
		self.alpha = newAlpha


	@propagateToChildren
	@drawable
	@config
	def draw(self):

		glActiveTexture(GL_TEXTURE0)
		glBindTexture(GL_TEXTURE_2D, self.colorTableTexture)

		glActiveTexture(GL_TEXTURE1)
		glBindTexture(GL_TEXTURE_2D, self.validFiberTexture)

		glUniform1i(self.shader[self.selectedShader].glGetUniformLocation('colorTable'), 0)
		glUniform1i(self.shader[self.selectedShader].glGetUniformLocation('fiberValidator'), 1)

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
		Default shader program for segmentation.
		It creates the shader programs for this specific class and returns the handler.
		'''

		vertexGLSL = [os.path.join(parent_path,'shaders','segmentation.vs')]
		fragmentGLSL = [os.path.join(parent_path,'shaders','standardFragmentShader.fs')]
		geometryGLSL = [os.path.join(parent_path,'shaders','segmentation.gs')]
		return [Shader(vertexGLSL, fragmentGLSL, geometryGLSL)]


	def exportFile(self, outfile):
		extension = outfile.split('.')[-1]

		# Bundle file
		if extension == 'bundles':
			self.exportBundleFile(outfile)

		# Trk file
		elif extension == 'trk':
			self.exportTrkFile(outfile)

		# Unsopported file
		else:
			raise TypeError('Unsupported file extension: ', extension)

	
	# Works only for classes that use fiberValidator array
	def exportBundleFile(self, outfile):
		if self.fiberValidator[:self.curvescount].sum() == 0:
			return

		bundleCount = np.zeros(len(self.bundlesName), dtype=np.int32)

		cfuncs.ROISegmentationExportbundlesdata(
			(outfile+'data').encode('utf-8'),
			len(self.bundlesName),
			self.bundlesStart.ctypes.data,
			self.fiberSizes.ctypes.data,
			bundleCount.ctypes.data,
			self.points.ctypes.data,
			self.fiberValidator.ctypes.data)

		ncount = (self.fiberValidator[:self.curvescount] != 0).sum()

		# wrtie minf file
		minf = """attributes = {\n    'binary' : 1,\n    'bundles' : %s,\n    'byte_order' : 'DCBA',\n    'curves_count' : %s,\n    'data_file_name' : '*.bundlesdata',\n    'format' : 'bundles_1.0',\n    'space_dimension' : 3\n  }\n"""

		bundlesstr = []
		offset = 0

		for name, bundleSize in zip([self.bundlesName[i] for i in range(len(self.bundlesName)) if bundleCount[i] != 0], bundleCount[bundleCount != 0]):
			bundlesstr.append(name)
			bundlesstr.append(offset)
			offset += bundleSize
		
		bundlesstr = str(bundlesstr)
		bundlesstr = bundlesstr[0] + ' ' + bundlesstr[1:-1] + ' ' + bundlesstr[-1]

		with open(outfile, 'w') as file:
			file.write( minf % ( bundlesstr, ncount ) )


	def exportTrkFile(self, outfile):
		''' This method should create a trk file using the vbo, ebo and the segmentation data (not defined yet).
		'''
		raise TypeError('Exporting trk for this segmentation method is not implemented. Class: ', type(self))
