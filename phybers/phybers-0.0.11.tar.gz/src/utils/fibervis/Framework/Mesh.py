''' _calculateNormals ponderarlo por areas.
_loadMeshAttributes sin implementar (leia archivos .mesh.minf)
'''

from Framework.VisualizationBaseObject import *
from Framework.BoundingBox import BoundingBox
import nibabel as nib
import os
from pathlib import Path

pathname = os.path.dirname(__file__)
parent_path = str(Path(pathname).parents[0])

class Mesh(VisualizationBaseObject):
	''' Class for drawing mesh files
	'''

	def __init__(self, sPath, shaderDict, parent):
		''' Initialize a Mesh object.
		It copies references to the path and the gl program.
		Then it loads the information from the file (points, normals, faces).

		Sends the information to the GPU buffers.

		Initialize  all parameters.
		
		The drawable variable is set to True.

		Parameters
		----------
		sPath : str
			String containing path for the mesh file (.mesh)
		shaderProgram : GLint
			Reference to the gl program containing all the shaders

		'''

		super().__init__(parent, shaderDict)
		self.identifier = VisualizationObject.Mesh
		
		self.path = sPath
		self.fileName = sPath.split('/')[-1]

		self.points = None
		self.normals = None
		self.faces = None

		# Read the vertex and connectivity for the mesh		
		self._readMesh()

		# Creates VBOs & an EBO, then populates them with the point and normal data. The elements data goes into the EBO
		self._loadBuffers()

		self.triangleColor = np.array([0.7, 0.7, 0.7], dtype=np.float32)
		self.lineColor = np.array([0.0, 0.0, 0.0], dtype=np.float32)
		self.alpha = 0.5

		# Uniform location
		self.colorUniform = self.shader[self.selectedShader].glGetUniformLocation("meshColor")

		# Ready to draw
		self.drawable = True
		self.drawableLines = False

		# We set the boundingbox parameters
		x = self.points[:,0]
		y = self.points[:,1]
		z = self.points[:,2]

		xmin, xmax = x.min(),x.max()
		ymin, ymax = y.min(),y.max()
		zmin, zmax = z.min(),z.max()
		
		dims = np.array([xmax-xmin, ymax-ymin, zmax-zmin], dtype=np.float32)
		center = np.array([xmin, ymin, zmin], dtype=np.float32)

		self.boundingbox = BoundingBox(shaderDict, self, dims, center)

		self.back2frontSorting = True

		print("Loading ready:\n\t", self.faces.shape[0], " triangles.\n\t", self.points.shape[0], " vertex.")

		# Not effi
		self.calculateTriangleCentroid()


	def cleanOpenGL(self):
		print('Cleaning object: ', self)
		glDeleteVertexArrays(1, [self.vao])

		glDeleteBuffers(1, [self.vbo])
		glDeleteBuffers(1, [self.ebo])

		self.clean = True


	def _readMesh(self):
		''' It reads the information from self.path file.
		Also calculates the normals.
		Finally creates the ebo buffer.

		Allowed files: .mesh

		Parameters
		----------
		None

		Returns
		-------
		None

		'''

		extension = self.path.split('.')[-1]

		# Bundle file
		if extension == 'mesh':
			self._openMesh()

		elif extension == 'gii':
			self._openGIFTI()

		# Unsopported file
		else:
			raise TypeError('Unsupported file.')


	def _openMesh(self):
		''' This function reads vertex, faces and (if in file) normals.
		It then creates the numpy array for points, normals and ebo (elements).

		Parameters
		----------
		None

		Returns
		-------
		None

		'''
		
		print('Opening mesh file {}'.format(self.path))

		# This was programed with meshes with triangles an not tetrahedron in mind
		with open(self.path, "rb") as file:
			# We read the endianess and prepare endianess variables
			endian = 'little' if file.read(9) == b'binarDCBA' else 'big'
			dtype = '<'  if endian == 'little' else '>'

			textureTypeU32 = int.from_bytes(file.read(4), byteorder=endian)
			textureType = file.read(4)

			polygonDimension = int.from_bytes(file.read(4), byteorder=endian)
			numberOfTimeSteps = int.from_bytes(file.read(4), byteorder=endian)

			print('endian: ', endian, '\ntextureTypeU32: ', textureTypeU32, '\ntextureType: ', textureType, '\npolygonDimension: ', polygonDimension, '\nnumberOfTimeSteps', numberOfTimeSteps)

			vertexVectorTotal = []
			normalVectorTotal = []
			polyVectorTotal = []

			vertexVector = []
			normalVector = []
			polyVector = []

			for timeStep in range(numberOfTimeSteps):
				# Read instant to be read (unsigned int 32 bits)
				actualTS = int.from_bytes(file.read(4), byteorder=endian)
				print('instant: ', actualTS)
				if actualTS != timeStep:
					raise RuntimeError('Error with mesh file {0}. Current instant \'{1}\' does not match with instant readed: \'{2}\''.format(self.path, timeStep, actualTS))

				# Read number of vertices
				vertexVectorTotal.append(int.from_bytes(file.read(4), byteorder=endian))
				print('vertex_vector_total: ', vertexVectorTotal[-1])

				vertex = np.fromstring(file.read(4*vertexVectorTotal[-1]*polygonDimension), dtype=dtype+'f4')
				vertex = vertex.reshape((vertexVectorTotal[-1], polygonDimension))
				vertexVector.append(vertex)

				# Read number of normals
				normalVectorTotal.append(int.from_bytes(file.read(4), byteorder=endian))
				print('normal_vector_total: ', normalVectorTotal[-1])

				if normalVectorTotal[-1] == vertexVectorTotal[-1]:
					normals = np.fromstring(file.read(4*normalVectorTotal[-1]*polygonDimension), dtype=dtype+'f4')
					normals = normals.reshape(normalVectorTotal[-1], polygonDimension)
					normalVector.append(normals)

				# Read the texture coordinates, if different from 0 raise an error
				textureVectorTotal = int.from_bytes(file.read(4), byteorder=endian)
				print('texture_vector_total: ', textureVectorTotal)

				if textureVectorTotal != 0:
					raise RuntimeError('Mesh files with texture coordinates can not be read. Not implemented (./Framework/Mesh.py)')

				polyVectorTotal.append(int.from_bytes(file.read(4), byteorder=endian))
				print('poly_vector_total: ', polyVectorTotal[-1])

				poly = np.fromstring(file.read(4*polyVectorTotal[-1]*polygonDimension), dtype=dtype+'u4')
				poly = poly.reshape(polyVectorTotal[-1], polygonDimension)
				polyVector.append(poly)

				# If normals havent been given, we net to calculate them
				if normalVectorTotal[-1] != vertexVectorTotal[-1]:
					normalVectorTotal[-1] = vertexVectorTotal[-1]
					normals = Mesh._calculateNormals(vertexVector[-1], polyVector[-1])
					normalVector.append(normals)

			# This will raise an error when a mesh with more than 1 time step is read
			self.points = np.array(vertexVector).reshape(vertexVector[0].shape)
			self.normals = np.array(normalVector).reshape(normalVector[0].shape)
			self.faces = np.array(polyVector).reshape(polyVector[0].shape)


	def _openGIFTI(self):
		''' This function reads vertex, faces and (if in file) normals.
		It then creates the numpy array for points, normals and ebo (elements).

		Parameters
		----------
		None

		Returns
		-------
		None

		'''
		print('Opening gifti file {}'.format(self.path))

		giftiMesh = nib.load(self.path)

		if (len(giftiMesh.darrays) != 2):
			printi('!!!!!!!! darrays = ', len(giftiMesh.darrays))

		self.points = giftiMesh.darrays[0].data
		self.faces = giftiMesh.darrays[1].data

		# print(type(self.points))
		# print(type(self.faces))

		# nib.freesurfer.io.write_geometry("test.gii", self.faces, self.points, create_stamp=None, volume_info=None)
		self.normals = Mesh._calculateNormals(self.points, self.faces)


	def _calculateNormals(vertex, triangles):
		''' Anonymous function.
		It calculates the normal for each triangle and then calculates the average per vertex.
		'''

		normals = np.zeros(vertex.shape, dtype=np.float32)

		for triangle in triangles:
			# n = np.cross(vertex[triangle[1]]-vertex[triangle[0]],	vertex[triangle[2]]-vertex[triangle[0]])
			# n = n/np.linalg.norm(n)

			# normals[triangle] += n
			normals[triangle] += np.cross(vertex[triangle[1]]-vertex[triangle[0]],	vertex[triangle[2]]-vertex[triangle[0]])

		normals /= np.linalg.norm(normals, axis=1).reshape(normals.shape[0],1)

		return normals


	def _loadBuffers(self):
		''' It generates a VAO, VBO and EBO.
		It populates them with the vertex and normal (the VBO), also the faces (the EBO).

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

		self.vbo = glGenBuffers(1)
		self.ebo = glGenBuffers(1)

		# VBO
		bufferSize = self.points.nbytes + self.normals.nbytes
		glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
		glBufferData(GL_ARRAY_BUFFER, bufferSize, None, GL_STATIC_DRAW)	# Create empty buffer

		# Populate buffer with points
		glBufferSubData(GL_ARRAY_BUFFER, 
			0, 
			self.points.nbytes, 
			self.points.flatten())

		# Normals
		glBufferSubData(GL_ARRAY_BUFFER, 
			self.points.nbytes, 
			self.normals.nbytes, 
			self.normals.flatten())

		# EBO
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
		glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.faces.nbytes, None, GL_STATIC_DRAW)

		# Enable attributes
		positionAttribute =	self.shader[0].attributeLocation('vertexPos')
		normalAttribute =	self.shader[0].attributeLocation('vertexNor')

		# # Connect attributes
		glEnableVertexAttribArray(positionAttribute)
		glVertexAttribPointer(positionAttribute,3, GL_FLOAT, GL_FALSE, 3*fSize, None)

		glEnableVertexAttribArray(normalAttribute)
		glVertexAttribPointer(normalAttribute,	3, GL_FLOAT, GL_FALSE, 3*fSize, ct.c_void_p(self.points.nbytes))


	def _loadMeshAttributes(self):
		''' Not implemented
		'''

		ns = dict()
		exec(open(self.path + '.minf').read(), ns)
		self.attributes = ns['attributes']

		item = 0
		for i in self.attributes['transformations']:
			print(item)
			print(i)
			item += 1


	def setDrawLines(self, drawLines):
		self.drawableLines = drawLines


	def setAlpha(self, newAlpha):
		self.alpha = newAlpha


	def setColor(self, color):
		self.triangleColor[0] = color[0]
		self.triangleColor[1] = color[1]
		self.triangleColor[2] = color[2]


	def getRGB256(self):
		return self.triangleColor*255
		

	@propagateToChildren
	@drawable
	@config
	def draw(self, eye):
		'''  It has 2 decorators configuring the vao and seeing if the visualize flag is up.

		It calls the draw element.
		'''
		self.sortTriangles(eye, self.back2frontSorting)
		self.loadSortedEBO()
		opacityUniform = self.shader[self.selectedShader].glGetUniformLocation('opacity')

		# Draw lines
		if self.drawableLines:

			glUniform1f(opacityUniform, 1.0)
			glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
			glUniform3fv(self.colorUniform, 1, self.lineColor)
			glLineWidth(0.01)
			glDrawElements(GL_TRIANGLES, self.faces.size, GL_UNSIGNED_INT, None)
			glLineWidth(1.0)
			glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

		# Draw triangles
		# glDepthMask(GL_FALSE)
		glEnable(GL_POLYGON_OFFSET_FILL)
		glEnable(GL_BLEND)
		glEnable(GL_CULL_FACE)
		
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glPolygonOffset(1.0, 1.0)
		glUniform1f(opacityUniform, self.alpha)
		glUniform3fv(self.colorUniform, 1, self.triangleColor)

		glDrawElements(GL_TRIANGLES, self.faces.size, GL_UNSIGNED_INT, None)

		glDisable(GL_POLYGON_OFFSET_FILL)
		glDisable(GL_BLEND)
		glDisable(GL_CULL_FACE)
		# glDepthMask(GL_TRUE)

		self.boundingbox.draw()


	def createProgram():
		''' Anonymous function.
		It creates the shader programs for this specific class and returns the handler.
		'''

		vertexGLSL = [os.path.join(parent_path,'shaders','mesh.vs')]
		fragmentGLSL = [os.path.join(parent_path,'shaders','standardFragmentShader.fs')]
		return [Shader(vertexGLSL, fragmentGLSL)]




	## Testing concept
	def calculateTriangleCentroid(self):
		self.triangleCentroid = np.zeros(self.faces.shape, dtype=np.float32)

		for index in range(self.faces.shape[0]):
			self.triangleCentroid[index] = self.points[self.faces[index]].sum(axis=0)/3


	def sortTriangles(self, eye, back2front=True):
		relativeEye = (self.inverseModel * np.concatenate((eye, [1.0])).reshape((4,1)))[:3].ravel()
		
		tmp = np.copy(self.triangleCentroid)
		tmp -= relativeEye
		tmp = np.linalg.norm(tmp, axis=1)

		self.sorted = np.argsort(tmp)[::-1] if back2front == True else np.argsort(tmp)


	def loadSortedEBO(self):
		glBindVertexArray(self.vao)

		glBufferSubData(GL_ELEMENT_ARRAY_BUFFER, 
			0, 
			self.faces.nbytes, 
			self.faces[self.sorted].flatten())

	def setFront2BackSorting(self, flag):
		self.back2frontSorting = flag


	def validExtension():
		return ['mesh', 'gii']
