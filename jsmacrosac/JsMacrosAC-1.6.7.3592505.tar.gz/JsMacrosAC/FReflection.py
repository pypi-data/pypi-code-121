from typing import overload
from typing import List
from typing import TypeVar
from .PerExecLibrary import PerExecLibrary
from .FReflection_CombinedVariableClassLoader import FReflection_CombinedVariableClassLoader
from .BaseScriptContext import BaseScriptContext
from .ProxyBuilder import ProxyBuilder
from .ClassBuilder import ClassBuilder
from .LibraryBuilder import LibraryBuilder
from .Mappings import Mappings
from .WrappedClassInstance import WrappedClassInstance

Field = TypeVar["java.lang.reflect.Field"]
T = TypeVar("T")
Method = TypeVar["java.lang.reflect.Method"]

class FReflection(PerExecLibrary):
	"""Functions for getting and using raw java classes, methods and functions.

An instance of this class is passed to scripts as the 'Reflection' variable.\n
	Since: 1.2.3 
	"""
	classLoader: FReflection_CombinedVariableClassLoader

	@overload
	def __init__(self, context: BaseScriptContext) -> None:
		pass

	@overload
	def getClass(self, name: str) -> Class:
		"""
		Since: 1.2.3 

		Args:
			name: name of class like 'path.to.class' 

		Returns:
			resolved class 
		"""
		pass

	@overload
	def getClass(self, name: str, name2: str) -> Class:
		"""Use this to specify a class with intermediary and yarn names of classes for cleaner code. also has support for
java primitives by using their name in lower case.\n
		Since: 1.2.3 

		Args:
			name: first try 
			name2: second try 

		Returns:
			a Class reference. 
		"""
		pass

	@overload
	def getDeclaredMethod(self, c: Class, name: str, parameterTypes: List[Class]) -> Method:
		"""
		Since: 1.2.3 

		Args:
			c: 
			parameterTypes: 
			name: 
		"""
		pass

	@overload
	def getDeclaredMethod(self, c: Class, name: str, name2: str, parameterTypes: List[Class]) -> Method:
		"""Use this to specify a method with intermediary and yarn names of classes for cleaner code.\n
		Since: 1.2.3 

		Args:
			c: 
			parameterTypes: 
			name: 
			name2: 

		Returns:
			a Method reference. 
		"""
		pass

	@overload
	def getMethod(self, c: Class, name: str, name2: str, parameterTypes: List[Class]) -> Method:
		"""
		Since: 1.6.0 

		Args:
			c: 
			parameterTypes: 
			name: 
			name2: 
		"""
		pass

	@overload
	def getMethod(self, c: Class, name: str, parameterTypes: List[Class]) -> Method:
		"""
		Since: 1.6.0 

		Args:
			c: 
			parameterTypes: 
			name: 
		"""
		pass

	@overload
	def getDeclaredField(self, c: Class, name: str) -> Field:
		"""
		Since: 1.2.3 

		Args:
			c: 
			name: 
		"""
		pass

	@overload
	def getDeclaredField(self, c: Class, name: str, name2: str) -> Field:
		"""Use this to specify a field with intermediary and yarn names of classes for cleaner code.\n
		Since: 1.2.3 

		Args:
			c: 
			name: 
			name2: 

		Returns:
			a Field reference. 
		"""
		pass

	@overload
	def getField(self, c: Class, name: str) -> Field:
		"""
		Since: 1.6.0 

		Args:
			c: 
			name: 
		"""
		pass

	@overload
	def getField(self, c: Class, name: str, name2: str) -> Field:
		"""
		Since: 1.6.0 

		Args:
			c: 
			name: 
			name2: 
		"""
		pass

	@overload
	def invokeMethod(self, m: Method, c: object, objects: List[object]) -> object:
		"""Invoke a method on an object with auto type coercion for numbers.\n
		Since: 1.2.3 

		Args:
			c: object (can be 'null' for statics) 
			objects: 
			m: method 
		"""
		pass

	@overload
	def newInstance(self, c: Class, objects: List[object]) -> T:
		"""Attempts to create a new instance of a class. You probably don't have to use this one and can just call '
new' on a Class unless you're in LUA, but then you also have the (kinda poorly
doccumented, can someone find a better docs link for me) LuaJava Library .\n
		Since: 1.2.7 

		Args:
			c: 
			objects: 
		"""
		pass

	@overload
	def createClassProxyBuilder(self, clazz: Class, interfaces: List[Class]) -> ProxyBuilder:
		"""proxy for extending java classes in the guest language with proper threading support.\n
		Since: 1.6.0 

		Args:
			interfaces: 
			T: 
			clazz: 
		"""
		pass

	@overload
	def createClassBuilder(self, cName: str, clazz: Class, interfaces: List[Class]) -> ClassBuilder:
		"""
		Since: 1.6.5 

		Args:
			interfaces: 
			T: 
			cName: 
			clazz: 
		"""
		pass

	@overload
	def getClassFromClassBuilderResult(self, cName: str) -> Class:
		"""
		Since: 1.6.5 

		Args:
			cName: 
		"""
		pass

	@overload
	def createLibraryBuilder(self, name: str, perExec: bool, acceptedLangs: List[str]) -> LibraryBuilder:
		pass

	@overload
	def loadJarFile(self, file: str) -> bool:
		"""Loads a jar file to be accessible with this library.\n
		Since: 1.2.6 

		Args:
			file: relative to the script's folder. 

		Returns:
			success value 
		"""
		pass

	@overload
	def loadCurrentMappingHelper(self) -> Mappings:
		"""
		Since: 1.3.1 

		Returns:
			the previous mapping helper generated with FReflection#loadMappingHelper(java.lang.String) 
		"""
		pass

	@overload
	def getClassName(self, o: object) -> str:
		"""
		Since: 1.3.1 

		Args:
			o: class you want the name of 

		Returns:
			the fully qualified class name (with "."'s not "/"'s) 
		"""
		pass

	@overload
	def loadMappingHelper(self, urlorfile: str) -> Mappings:
		"""
		Since: 1.3.1 

		Args:
			urlorfile: a url or file path the the yarn mappings '-v2.jar' file, or '.tiny' file. for example 'https://maven.fabricmc.net/net/fabricmc/yarn/1.16.5%2Bbuild.3/yarn-1.16.5%2Bbuild.3-v2.jar' , if same url/path as previous this will load from cache. 

		Returns:
			the associated mapping helper. 
		"""
		pass

	@overload
	def wrapInstace(self, instance: T) -> WrappedClassInstance:
		"""
		Since: 1.6.5 

		Args:
			instance: 
			T: 
		"""
		pass

	@overload
	def getWrappedClass(self, className: str) -> WrappedClassInstance:
		"""
		Since: 1.6.5 

		Args:
			className: 
		"""
		pass

	pass


