from typing import overload
from typing import TypeVar

File = TypeVar["java.io.File"]

class FReflection_CombinedVariableClassLoader(ClassLoader):
	"""I know this is probably bad practice, but lets be real, this whole library is bad practice, So I can make it
worse, right? at least this should work better than 'try/catch' 'ing using ClassLoader#loadClass(java.lang.String) to search through every URLClassLoader that FReflection#loadJarFile(java.lang.String) would make, or how I was previously doing it by pre-loading and caching
all the classes to a Map This class is a modification to Christian d'Heureuse's JoinClassLoader , under the Apache-2.0 license to change it from a Class array to a Set , to allow for modifications to the ClassLoader contained in the classLoader.\n
	Since: 1.2.8 
	"""

	@overload
	def __init__(self, parent: ClassLoader) -> None:
		pass

	@overload
	def addClassLoader(self, jarPath: File, loader: ClassLoader) -> bool:
		pass

	@overload
	def hasJar(self, path: File) -> bool:
		pass

	pass


