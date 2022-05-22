from Framework.VisualizationBaseObject import *
import os
from pathlib import Path

pathname = os.path.dirname(__file__)
parent_path = str(Path(pathname).parents[0])

class BoundingBox(VisualizationBaseObject):
	def __init__(self, shaderDict, parent, dims, center, bbM=None):
		super().__init__(parent, shaderDict)
		if bbM is None:
			self.bbModel = glm.translateMatrix(center)*glm.scaleMatrix(dims)
		else:
			self.bbModel = bbM

		self.dims = np.array(dims, dtype=np.float32)
		self.center = np.array(center, dtype=np.float32)

		self._loadBuffers()

		# Ready to draw
		self.drawable = True


	def cleanOpenGL(self):
		print('Cleaning object: ', self)
		glDeleteVertexArrays(1, [self.vao])

		glDeleteBuffers(1, [self.vbo])
		glDeleteBuffers(1, [self.ebo])

		self.clean = True


	def _loadBuffers(self):
		self.vao = glGenVertexArrays(1)
		glBindVertexArray(self.vao)

		self.vbo = glGenBuffers(1)
		self.ebo = glGenBuffers(1)

		boundingbox = np.array([1,	1,	0,
								1,	1,	1,
								0,	1,	1,
								0,	1,	0,
								1,	0,	0,
								1,	0,	1,
								0,	0,	0,
								0,	0,	1], dtype=np.float32)

		boundingElements = np.array([	0, 1, 1, 2, 2, 3, 3, 6, 0, 3, 0, 4,
										1, 5, 2, 7, 4, 6, 4, 5, 5, 7, 6, 7], dtype=np.uint32)

		# VBO
		glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
		glBufferData(GL_ARRAY_BUFFER, boundingbox.nbytes, boundingbox, GL_STATIC_DRAW)

		# EBO
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
		glBufferData(GL_ELEMENT_ARRAY_BUFFER, boundingElements.nbytes, boundingElements, GL_STATIC_DRAW)

		# Enable attributes
		positionAttribute =	self.shader[0].attributeLocation('vertexPos')

		# # Connect attributes
		glEnableVertexAttribArray(positionAttribute)
		glVertexAttribPointer(positionAttribute, 3, GL_FLOAT, GL_FALSE, 0, None)


	def updateBBModel(self, dims, center):
		self.bbModel = glm.translateMatrix(center)*glm.scaleMatrix(dims)

		self.dims = np.array(dims, dtype=np.float32)
		self.center = np.array(center, dtype=np.float32)
		

	def loadUniforms(self):
		glUniformMatrix4fv(self.shader[self.selectedShader].glGetUniformLocation("bbM"), 1, GL_TRUE, self.bbModel.getA())
		glUniformMatrix4fv(self.shader[self.selectedShader].glGetUniformLocation("M"), 1, GL_TRUE, self.parent.model.getA())
		

	@drawable
	@config
	def draw(self):
		glDrawElements(GL_LINES, 24, GL_UNSIGNED_INT, None)


	def createProgram():
		''' Anonymous function.
		It creates the shader programs for this specific class and returns the handler.
		'''

		vertexGLSL = [os.path.join(parent_path,'shaders','boundingbox.vs')]
		fragmentGLSL = [os.path.join(parent_path,'shaders','standardFragmentShader.fs')]
		return [Shader(vertexGLSL, fragmentGLSL)]
