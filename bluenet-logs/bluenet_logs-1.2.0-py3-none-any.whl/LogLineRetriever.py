import os
import re
import logging

_LOGGER = logging.getLogger(__name__)

class LogLineRetriever:
	def __init__(self):
		self.logPattern = re.compile(".*?LOG[a-zA-Z]+\(\"([^\"]*)\"")
		self.rawLogPattern = re.compile(".*?_log\([^,]+,[^,]+,\s*\"([^\"]*)\"")

		self.logDefinedStringPattern = re.compile(".*?LOG[a-zA-Z]+\(([A-Z_]+)")
		self.rawLogDefinedStringPattern = re.compile(".*?_log\([^,]+,[^,]+,\s*([A-Z_]+)")

		self.sourceFilesDir = None

		self.cacheFiles = False

		# Key: filename
		# Data: all lines in file as list.
		self.bluenetFiles = {}

		# Key: filename hash.
		# Data: filename.
		self.fileNameHashMap = {}

		# A list with the full path of all the source files (and maybe some more).
		self.fileNames = []

	# We could also get all source files from: build/default/CMakeFiles/crownstone.dir/depend.internal
	def setSourceFilesDir(self, dir: str):
		if os.path.isdir(dir) == False:
			_LOGGER.warning(f"No such dir: {dir}")

		self.sourceFilesDir = dir

		self._cacheFileNames()
		self._cacheFileNameHashes()
		self._cacheFileContents()

	def getFileName(self, fileNameHash: int):
		fileName = self.fileNameHashMap.get(fileNameHash, None)
		if fileName is None:
			if self.cacheFiles:
				return None
			# For now, simply recheck all file names.
			# We could improve this by only searching for given hash and adding that to cache.
			self._cacheFileNames()
			self._cacheFileNameHashes()
			fileName = self.fileNameHashMap.get(fileNameHash, None)
			if fileName is None:
				return None
		return fileName

	def getLogFormat(self, fileName: str, lineNumber: int):
		return self._getLogFmt(fileName, lineNumber)

	def _cacheFileNames(self):
		"""
		Cache all C/C++ fileNames in sourceFilesDir
		"""
		for root, dirs, files in os.walk(self.sourceFilesDir):
			for fileName in files:
				if fileName.endswith((".cpp",".c",".h",".hpp")):
					self.fileNames.append(os.path.join(root, fileName))

	def _cacheFileNameHashes(self):
		"""
		Cache fileNameHash of all cached fileNames.
		"""
		for fileName in self.fileNames:
			# Cache hash of all file names.
			fileNameHash = self._getFileNameHash(fileName)
			self.fileNameHashMap[fileNameHash] = fileName

	def _cacheFileContents(self):
		"""
		Cache contents of all cached fileNames.
		"""
		for fileName in self.fileNames:
			filePath = fileName
			file = open(filePath, "r")
			lines = file.readlines()
			file.close()
			self.bluenetFiles[fileName] = lines

	def _getFileNameHash(self, fileName: str):
		byteArray = bytearray()
		byteArray.extend(map(ord, fileName))

		hashVal: int = 5381
		# A string in C ends with 0.
		hashVal = (hashVal * 33 + 0) & 0xFFFFFFFF
		for c in reversed(byteArray):
			if c == ord('/'):
				return hashVal
			hashVal = (hashVal * 33 + c) & 0xFFFFFFFF
		return hashVal

	def _getLogFmt(self, fileName, lineNr):
		lines = self.bluenetFiles[fileName]
		if not self.cacheFiles:
			try:
				with open(fileName, 'r') as file:
					lines = file.readlines()
			except:
				pass
		lineNr = lineNr - 1 # List starts at 0, line numbers start at 1.

		if lineNr < 0 or lineNr >= len(lines):
			_LOGGER.warning(f"Invalid line number {lineNr + 1}")
			return None

		line = lines[lineNr]
		result = self._getLogFmtFromLine(line)
		if result is not None:
			return result

		# Maybe the log line is spread over multiple lines.
		brackets = 0
		for c in line[::-1]:
			if c == ')':
				brackets = brackets - 1
			if c == '(':
				brackets = brackets + 1
		if brackets < 0:
			# There are more closing than opening brackets, so the log format is probably on a line before the given line number.
			# Iterate back over lines, and merge the lines together.
			# Loop until the brackets are balanced (as many opening as closing brackets).
			# Then check if the format can be found in the merged line.
			mergedLine = line.strip()
			i = lineNr - 1
			while (i > 0):
				curLine = lines[i].strip()
				for c in curLine[::-1]:
					if c == ')':
						brackets = brackets - 1
					if c == '(':
						brackets = brackets + 1
				mergedLine = curLine + mergedLine
#				_LOGGER.debug(f"brackets={brackets} mergedLine={mergedLine}")
				if brackets == 0:
					# Looks like we're at the first opening bracket.
					result = self._getLogFmtFromLine(mergedLine)
					if result is not None:
						return result
				i = i - 1

		_LOGGER.warning(f"Can't find log format in: {fileName[-30:]}:{lineNr + 1} {line.rstrip()}")
		return None

	def _getLogFmtFromLine(self, fileLine):
		match = self.logPattern.match(fileLine)
		if match:
			return match.group(1)

		match = self.rawLogPattern.match(fileLine)
		if match:
			return match.group(1)

		# Logs like: LOGi(FMT_INIT, "relay");
		# The string definition file contains lines like: #define FMT_INIT     "Init %s"
		# We search for the line with "FMT_INIT", and return "Init %s".
		match = self.logDefinedStringPattern.match(fileLine)
		if not match:
			match = self.rawLogDefinedStringPattern.match(fileLine)
		stringsDefFileName = self.sourceFilesDir + "/include/cfg/cs_Strings.h"
		if match and stringsDefFileName in self.bluenetFiles:
			for strDefLine in self.bluenetFiles[stringsDefFileName]:
				strDefWords = strDefLine.split()
				if len(strDefWords) >= 3 and strDefWords[0] == "#define" and strDefWords[1] == match.group(1):
					# Return the string, with quotes removed.
					return " ".join(strDefWords[2:])[1:-1]

		return None
