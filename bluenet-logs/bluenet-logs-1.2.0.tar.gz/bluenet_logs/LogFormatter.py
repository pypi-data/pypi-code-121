import logging
import datetime
import sys

from crownstone_core.util.BufferReader import BufferReader
from crownstone_core.util.Conversion import Conversion

_LOGGER = logging.getLogger(__name__)

class LogFormatter:
	def __init__(self):
		self.timestampFormat = "%Y-%m-%d %H:%M:%S.%f"

		# Whether to enable colors in logs.
		self.enableColors = True
		if sys.platform == "win32":
			self.enableColors = False

		# Whether the next log line should get a prefix.
		self._printPrefix = True

	def _getPrefix(self, timestamp, fileName, lineNr, logLevel):
		return f"LOG: [{timestamp.strftime(self.timestampFormat)}] [{fileName[-30:]:>30}:{lineNr:4n}] {self._getLogLevelStr(logLevel)}{self._getLogLevelColor(logLevel)} "

	def _getLogLevelStr(self, logLevel):
		if logLevel == 8: return "V"
		if logLevel == 7: return "D"
		if logLevel == 6: return "I"
		if logLevel == 5: return "W"
		if logLevel == 4: return "E"
		if logLevel == 3: return "F"
		return " "

	def _getLogLevelColor(self, logLevel):
		if self.enableColors:
			if logLevel == 8: return "\033[37;1m" # White
			if logLevel == 7: return "\033[37;1m" # White
			if logLevel == 6: return "\033[34;1m" # Blue
			if logLevel == 5: return "\033[33;1m" # Yellow
			if logLevel == 4: return "\033[35;1m" # Purple
			if logLevel == 3: return "\033[31;1m" # Red
		return ""

	def _getEndColor(self):
		if self.enableColors:
			return "\033[0m"
		return ""


	def printLog(self,
	           logFormat: str,
	           fileName: str,
	           lineNr: int,
	           logLevel: int, # TODO: make enum
	           newLine: bool,
	           argBufs: list):
		timestamp = datetime.datetime.now()

		_LOGGER.debug(f"Log {fileName}:{lineNr} {logFormat} {argBufs}")

		if logFormat is not None:
			formattedString = ""
			i = 0
			argNum = 0
			while i < len(logFormat):
				if logFormat[i] == '%':
					# Check the arg format.
					i += 1
				else:
					# Just append the character
					formattedString += logFormat[i]
					i += 1
					continue

				if logFormat[i] == '%':
					# Actually not an arg, but an escaped '%'
					formattedString += logFormat[i]
					i += 1
					continue

				# Check arg type and let python do the formatting.
				argVal = 0     # Value of this arg
				argFmt = "%"   # Format of this arg
				while True:
					c = logFormat[i]
					argBuf = None
					argLen = 0
					if argNum < len(argBufs):
						argBuf = argBufs[argNum]
						argLen = len(argBuf)

					if c == 'd' or c == 'i':
						# Signed integer
						argVal = 0
						if argLen == 1:
							argVal = Conversion.uint8_to_int8(argBuf[0])
						elif argLen == 2:
							argVal = Conversion.uint8_array_to_int16(argBuf)
						elif argLen == 4:
							argVal = Conversion.uint8_array_to_int32(argBuf)
						elif argLen == 8:
							argVal = Conversion.uint8_array_to_int64(argBuf)

						argFmt += c
						break

					elif c == 'u' or c == 'x' or c == 'X' or c == 'o' or c == 'p' or c == 'b':
						# Unsigned integer
						argVal = 0
						if argLen == 1:
							argVal = argBuf[0]
						elif argLen == 2:
							argVal = Conversion.uint8_array_to_uint16(argBuf)
						elif argLen == 4:
							argVal = Conversion.uint8_array_to_uint32(argBuf)
						elif argLen == 8:
							argVal = Conversion.uint8_array_to_uint64(argBuf)

						if c == 'p':
							# Python doesn't do %p
							argFmt += 'x'
						else:
							argFmt += c
						break

					elif c == 'f' or c == 'F' or c == 'e' or c == 'E' or c == 'g' or c == 'G':
						# Floating point
						argVal = 0.0
						if argLen == 4:
							argVal = Conversion.uint8_array_to_float(argBuf)

						argFmt += c
						break

					elif c == 'a':
						# Character
						argVal = ' '
						if argLen == 1:
							argVal = argBuf[0]

						argFmt += c
						break

					elif c == 's':
						# String
						argVal = ""
						if argBuf is not None:
							argVal = Conversion.uint8_array_to_string(argBuf)

						argFmt += c
						break

					else:
						i += 1
						argFmt += c
						continue

				# Let python do the formatting
				if argFmt.endswith('b'):
					# f-strings can do binary format. Remove the '%' from the arg format.
					argStr = f"{argVal:{argFmt[1:]}}"
				else:
					argStr = argFmt % argVal
				formattedString += argStr
				argNum += 1
				i += 1

			logStr = formattedString
			if self._printPrefix:
				logStr = self._getPrefix(timestamp, fileName, lineNr, logLevel) + logStr

			sys.stdout.write(logStr)
			if newLine:
				# Next line should be prefixed.
				self._printPrefix = True
				sys.stdout.write(self._getEndColor())
				sys.stdout.write('\n')
			else:
				self._printPrefix = False


	def _getElementValues(self,
	                      elementType: int,  # TODO: make enum
	                      elementSize: int,
	                      elementData: list) -> list:
		bufferReader = BufferReader(elementData)
		dataSize = len(elementData)
		if dataSize % elementSize != 0:
			_LOGGER.warning(f"Remaining data with element size of {elementSize} and element data of size {dataSize}")
			return []

		vals = []
		numElements = int(dataSize / elementSize)
		_LOGGER.debug(f"dataSize={dataSize} elementSize={elementSize} numElements={numElements}")
		for i in range(0, numElements):
			if elementType == 0:
				# Signed integer
				if elementSize == 1:
					vals.append(bufferReader.getInt8())
				elif elementSize == 2:
					vals.append(bufferReader.getInt16())
				elif elementSize == 4:
					vals.append(bufferReader.getInt32())
				elif elementSize == 8:
					vals.append(bufferReader.getInt64())
				else:
					_LOGGER.warning(f"Unknown type: element with type {elementType} and size {elementSize}")
					return []

			elif elementType == 1:
				# Unsigned integer
				if elementSize == 1:
					vals.append(bufferReader.getUInt8())
				elif elementSize == 2:
					vals.append(bufferReader.getUInt16())
				elif elementSize == 4:
					vals.append(bufferReader.getUInt32())
				elif elementSize == 8:
					vals.append(bufferReader.getUInt64())
				else:
					_LOGGER.warning(f"Unknown type: element with type {elementType} and size {elementSize}")
					return []

			elif elementType == 2:
				# Floating point
				if elementSize == 4:
					vals.append(bufferReader.getFloat())
				else:
					_LOGGER.warning(f"Unknown type: element with type {elementType} and size {elementSize}")
					return []
		return vals


	def _getElementString(self,
	                      elementFormat: str or None,
	                      elementType: int,  # TODO: make enum
	                      elementSize: int,
	                      elemVal: list) -> str:

		if elementFormat is not None:
			if elementFormat.endswith('b'):
				return f"{elemVal:{elementFormat[1:]}}"
			return elementFormat % elemVal

		# Default formats:
		elementFormat = f"unknown_type(type={elementType}, size={elementSize})"
		if elementType == 0:
			# Signed integer
			if elementSize == 1:
				elementFormat = "%3i"
			elif elementSize == 2:
				elementFormat = "%5i"
			elif elementSize == 4:
				elementFormat = "%10i"
			elif elementSize == 8:
				elementFormat = "%20i"

		elif elementType == 1:
			# Unsigned integer
			if elementSize == 1:
				elementFormat = "%3u"
			elif elementSize == 2:
				elementFormat = "%5u"
			elif elementSize == 4:
				elementFormat = "%10u"
			elif elementSize == 8:
				elementFormat = "%20u"

		elif elementType == 2:
			# Floating point
			if elementSize == 4:
				elementFormat = "%f."
		return elementFormat % elemVal


	def printLogArray(self,
	                startFormat: str or None,
	                endFormat: str or None,
	                separationFormat: str or None,
	                elementFormat: str or None,
	                fileName: str,
	                lineNr: int,
	                logLevel: int, # TODO: make enum
	                newLine: bool,
	                reverse: bool,
	                elementType: int, # TODO: make enum
	                elementSize: int,
	                elementData: list):
		timestamp = datetime.datetime.now()

		elementValues = self._getElementValues(elementType, elementSize, elementData)

		if startFormat is None:
			startFormat = "["
		if endFormat is None:
			endFormat = "]"
		if separationFormat is None:
			separationFormat = ", "

		logStr = startFormat
		numElements = len(elementValues)
		for i in range(0, numElements):
			elementValue = elementValues[i]
			if reverse:
				elementValue = elementValues[numElements - 1 - i]
			logStr += self._getElementString(elementFormat, elementType, elementSize, elementValue)
			if i < numElements - 1:
				logStr += separationFormat

		logStr += endFormat

		if self._printPrefix:
			logStr = self._getPrefix(timestamp, fileName, lineNr, logLevel) + logStr

		sys.stdout.write(logStr)
		if newLine:
			# Next line should be prefixed.
			self._printPrefix = True
			sys.stdout.write(self._getEndColor())
			sys.stdout.write('\n')
		else:
			self._printPrefix = False
