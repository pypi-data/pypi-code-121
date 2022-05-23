from OpenGL.GL import *

class Shader:
	""" Shader class for GLSL programs
	"""
	def __init__(self, vShader,  fShader, gShader=None):
		"""
		Parameters
		----------
		vShader : str or tuple
			String containing shader source code path (or tuple with paths)
			for the vertex shader
		fShader : str or tuple
			String containing shader source code path (or tuple with paths)
			for the fragment shader
		gShader : str or tuple
			String containing shader source code path (or tuple with paths)
			for the geometry shader

		"""
		self.program = glCreateProgram()
		shaders = []

		# vertex shaders
		if type(vShader) is list:
			shaders += [self._addShader(vertex, GL_VERTEX_SHADER) for vertex in vShader]
		else:
			shaders.append(self._addShader(vShader, GL_VERTEX_SHADER))

		# fragment shaders
		if type(fShader) is list:
			shaders += [self._addShader(fragment, GL_FRAGMENT_SHADER) for fragment in fShader]
		else:
			shaders.append(self._addShader(fShader, GL_FRAGMENT_SHADER))
			
		# geometry shaders
		if type(gShader) is list:
			shaders += [self._addShader(geometry, GL_GEOMETRY_SHADER) for geometry in gShader]
		elif gShader is not None:
			shaders.append(self._addShader(gShader, GL_GEOMETRY_SHADER))
			
		glLinkProgram(self.program)

		# check if got linked
		if glGetProgramiv(self.program, GL_LINK_STATUS) != GL_TRUE:
			info = glGetProgramInfoLog(self.program)
			glDeleteProgram(self.program)
			for shaders_id in shaders:
				glDeleteShader(shaders_id)
			raise RuntimeError('Error linking program: %s' % (info))

		for shaders_id in shaders:
			glDeleteShader(shaders_id)

	def _addShader(self, source_path, shader_type):
		""" Helper function for compiling a GLSL shader

		Parameters
		----------
		source_path : str
			String containing shader source path

		shader_type : valid OpenGL shader type
			Type of shader to compile

		Returns
		-------
		value : int
			Identifier for shader if compilation is successful

		"""
		try:
			shader_id = glCreateShader(shader_type)
			with open(source_path, "r") as file:
				source = file.read()
				glShaderSource(shader_id, source)
			glCompileShader(shader_id)
			
			if glGetShaderiv(shader_id, GL_COMPILE_STATUS) != GL_TRUE:
				info = glGetShaderInfoLog(shader_id)
				raise RuntimeError('\n\tFile {1}:\n\tShader compilation failed:\n\t\t{0}'.format(info, source_path))
			
			glAttachShader(self.program, shader_id)
			return shader_id
		except:
			glDeleteShader(shader_id)
			raise

	def glGetUniformLocation(self, name):
		""" Helper function to get location of an
		OpenGL uniform variable

		Parameters
		----------
		name : str
			Name of the variable for which location
			is to be returned

		Returns
		-------
		value : int
			Integer describing location

		"""
		uniform = glGetUniformLocation(self.program, name)

		if uniform == -1:
			raise RuntimeError('Uniform not found: {0}'.format(name))
		else:
			return uniform

	def attributeLocation(self, name):
		""" Helper function to get location of an
		OpenGL attribute variable
  
		Parameters
		----------
		name : str
			Name of the variable for which location is
			to be returned

		Returns
		-------
		value : int
			Integer describing location

		"""
		attribute = glGetAttribLocation(self.program, name)

		if attribute == -1:
			raise RuntimeError('Attribute not found: {0}'.format(name))
		else:
			return attribute

	def glUseProgram(self):
		""" Bipass for the function glUseProgram
		"""
		
		glUseProgram(self.program)