# coding=utf-8
""" FormatOC Package

Exports several classes used to represent documents and their nodes
"""

# Compatibility
from future.utils import iteritems
from past.builtins import basestring
try: xrange
except NameError: xrange = range
try: long
except NameError: long = int

__author__		= "Chris Nasr"
__copyright__	= "Ouroboros Coding Inc."
__license__		= "Apache"
__version__		= "1.5.17"
__maintainer__	= "Chris Nasr"
__email__		= "chris@ouroboroscoding.com"

# Import python core modules
import abc
import datetime
from decimal import Decimal, InvalidOperation as DecimalInvalid
import hashlib
import re
import sys

# Import local modules
from . import JSON

_reserved = [
	'__array__', '__hash__', '__maximum__', '__minimum__', '__name__',
	'__options__', '__regex__', '__require__', '__type__'
]
"""Reserved Fields
Holds a list of fields that can't be used as special"""

_specialSyntax	= r'[a-z0-9_-]+'
_specialName	= re.compile(r'^' + _specialSyntax + r'$')
_specialKey		= re.compile(r'^__(' + _specialSyntax + r')__$')
_specialSet		= '__%s__'
"""Special Fields
Holds regexes to match special hash elements"""

_standardField	= re.compile(r'^_?[a-zA-Z0-9][a-zA-Z0-9_-]*$')
"""Standard Field
Holds a regex to match any standard named fields. These are limited in order
to ease the ability to plugin additional data stores"""

##
#
# @var dict
_typeToRegex	= {
	'base64':	re.compile(r'^(?:[A-Za-z0-9+/]{4})+(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$'),
	'date':		re.compile(r'^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$'),
	'datetime':	re.compile(r'^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01]) (?:[01]\d|2[0-3])(?::[0-5]\d){2}$'),
	'int':		re.compile(r'^(?:0|[+-]?[1-9]\d*|0x[0-9a-f]+|0[0-7]+)$'),
	'ip':		re.compile(r'^(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[1-9])(?:\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}$'),
	'md5':		re.compile(r'^[a-fA-F0-9]{32}$'),
	'price':	re.compile(r'^-?(?:[1-9]\d+|\d)(?:\.\d{1,2})?$'),
	'time':		re.compile(r'^(?:[01]\d|2[0-3])(?::[0-5]\d){2}$'),
	'uuid':		re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'),
	'uuid4':	re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}$')
}
"""Type to regex

Holds a hash of type values to the regular expression used to validate them"""

# There is no way to access the real type of compiled regular expressions or md5
#	hashes so unfortunately we have to do this ugly hack
_REGEX_TYPE	= type(_typeToRegex['date'])
_MD5_TYPE	= type(hashlib.md5(b'hack'))

def _child(details):
	"""Child

	A private function to figure out the child node type

	Arguments:
		details {dict} -- A dictionary describing a data point

	Returns:
		_NodeInterface
	"""

	# If the details are a list
	if isinstance(details, list):

		# Create a list of options for the key
		return OptionsNode(details)

	# Else if we got a dictionary
	elif isinstance(details, dict):

		# If array is present
		if '__array__' in details:
			return ArrayNode(details)

		# Else if we have a hash
		elif '__hash__' in details:
			return HashNode(details)

		# Else if we have a type
		elif '__type__' in details:

			# If the type is a dictionary or list, this is a complex type
			if isinstance(details['__type__'], (dict,list)):
				return _child(details['__type__'])

			# Else it's just a Node
			else:
				return Node(details)

		# Else it's most likely a parent
		else:
			return Parent(details)

	# Else if we got a string
	elif isinstance(details, basestring):

		# Use the value as the type
		return Node(details)

	# Else raise an error
	else:
		raise TypeError('details')

def _strip_special(details):
	"""Strip Special

	Takes all the special fields of the details and returns them as a new dict

	Arguments:
		details (dict): The details to strip special fields from

	Returns:
		dict
	"""

	# Init the return list
	dRet = {}

	# Go through all keys in the details
	for k in (tuple(details.keys())):

		# If it's a reserved key, ignore it
		if k in _reserved:
			continue

		# If key is special
		oMatch = _specialKey.match(k)
		if oMatch:

			# Store it with the other specials then remove it
			dRet[k] = details[k]
			del details[k]

	# Return the special fields
	return dRet

class _NodeInterface(object):
	"""Node Interface

	All Node instances must be built off of this one

	Extends:
		object
	"""
	__metaclass__	= abc.ABCMeta

	def __repr__(self):
		"""Representation (__repr__)

		Returns a string representation of the instance

		Returns:
			str
		"""
		return str(self.toDict())

	@abc.abstractmethod
	def className(self):
		"""Class Name

		Returns the class of the Node instance

		Returns:
			str
		"""
		pass

	@abc.abstractmethod
	def clean(self, value):
		"""Clean

		As validation allows for strings representing non-string values, it is
		useful to be able to "clean" a value and turn it into the value it was
		representing, making sure that data in data stores is accurate, and not
		representitive

		Args:
			value (mixed): The value to clean

		Returns:
			mixed
		"""
		pass

	@classmethod
	def fromFile(cls, filename):
		"""From File

		Loads a JSON file and creates a Node instance from it

		Args:
			filename (str): The filename to load

		Returns:
			_NodeInterface
		"""

		# Load the file
		oFile = open(filename)

		# Convert it to a dictionary
		dDetails = JSON.decodef(oFile)

		# Create and return the new instance
		return cls(dDetails)

	@abc.abstractmethod
	def toDict(self):
		"""To Dict

		Returns the basic node as a dictionary in the same format as is used in
		constructing it

		Returns:
			dict
		"""
		pass

	def toJSON(self):
		"""To JSON

		Returns a JSON string representation of the instance

		Returns:
			str
		"""
		return JSON.encode(self.toDict())

	@abc.abstractmethod
	def valid(self, value, level=[]):
		"""Valid

		Checks if a value is valid based on the instance's values

		Args:
			value (mixed): The value to validate

		Returns:
			bool
		"""
		pass

class _BaseNode(_NodeInterface):
	"""Basic Node

	Represents shared functionality amongst Nodes and Parents

	Extends:
		_NodeInterface
	"""

	def __init__(self, details, _class):
		"""Constructor

		Initialises the instance

		Arguments:
			details {dict} -- Details describing the type of values allowed for
				the node
			_class {str} -- The class of the child

		Raises:
			ValueError

		Returns:
			_BaseNode
		"""

		# If details is not a dict instance
		if not isinstance(details, dict):
			raise ValueError('details in ' + self.__class__.__name__ + '.' + sys._getframe().f_code.co_name + ' must be a dict')

		# Init the variables used to identify the last falure in validation
		self.validation_failures = {}

		# Store the class name
		self._class = _class

		# Init the optional flag, assume all nodes are necessary
		self._optional = False

		# If the details contains an optional flag
		if '__optional__' in details:

			# If it's a valid bool, store it
			if isinstance(details['__optional__'], bool):
				self._optional = details['__optional__']

			# Else, write a warning to stderr
			else:
				sys.stderr.write('"' + str(details['__optional__']) + '" is not a valid value for __optional__, assuming false')

			# Remove it from details
			del details['__optional__']

		# Init the special dict
		self._special = {}

		# If there are any other special fields in the details
		for k in (tuple(details.keys())):

			# If key is special
			oMatch = _specialKey.match(k)
			if oMatch:

				# Store it with the other specials then remove it
				self._special[oMatch.group(1)] = details[k]
				del details[k]

	def className(self):
		"""Class Name

		Returns a string representation of the name of the child class

		Returns:
			str
		"""
		return self._class

	def optional(self, value = None):
		"""Optional

		Getter/Setter method for optional flag

		Args:
			value (bool): If set, the method is a setter

		Returns:
			bool | None
		"""

		# If there's no value, this is a getter
		if value is None:
			return self._optional

		# Else, set the flag
		else:
			self._optional = value and True or False

	def special(self, name, value=None, default=None):
		"""Special

		Getter/Setter method for special values associated with nodes that are
		not fields

		To retrieve a value or values, pass only the name or names, to set a
		single special value, pass a name and value

		Args:
			name (str): The name of the value to either set or get
			value (mixed): The value to set
				Must be something that can be converted directly to JSON
			default (mixed): The default value
				Returned if the special field doesn't exist

		Returns:
			On getting, the value of the special field is returned. On setting,
			nothing is returned

		Raises:
			TypeError: If the name is not a valid string
			ValueError: If the name is invalid, or if setting and the value can
				not be converted to JSON
		"""

		# Check the name is a string
		if not isinstance(name, basestring):
			raise TypeError('name must be a string')

		# Check the name is valid
		if not _specialName.match(name):
			raise ValueError('special name must match "%s"' % _specialSyntax)

		# If the value is not set, this is a getter
		if value is None:

			# Return the value or the default
			try: return self._special[name]
			except KeyError: return default

		# Else, this is a setter
		else:

			# Can the value safely be turned into JSON
			try:
				JSON.encode(value)
			except TypeError:
				raise ValueError('value can not be encoded to JSON')

			# Save it
			self._special[name]	= value

	def toDict(self):
		"""To Dictionary

		Returns the basic node as a dictionary in the same format as is used in
		constructing it

		Returns:
			dict
		"""

		# Create the dict we will return
		dRet = {}

		# If the optional flag is set
		if self._optional:
			dRet['__optional__'] = True

		# Add all the special fields found
		for k in self._special.keys():
			dRet[_specialSet % k] = self._special[k]

		# Return
		return dRet

class ArrayNode(_BaseNode):
	"""ArrayNode

	Represents a node which is actually an array containing lists of another
	node

	Extends:
		_BaseNode
	"""

	_VALID_ARRAY = ['unique', 'duplicates']
	"""Valid Array

	Holds a list of valid values used to represent arrays types"""

	def __init__(self, details):
		"""Constructor

		Initialises the instance

		Arguments:
			details {dict} -- Details describing the type of values allowed for
				the node

		Raises:
			KeyError
			ValueError

		Returns:
			ArrayNode
		"""

		# If details is not a dict instance
		if not isinstance(details, dict):
			raise ValueError('details')

		# If the array config is not found
		if '__array__' not in details:
			raise KeyError('__array__')

		# If the value is not a dict
		if not isinstance(details['__array__'], dict):
			details['__array__'] = {
				"type": details['__array__']
			}

		# If the type is missing
		if not 'type' in details['__array__']:
			self._type = 'unique'

		# Or if the type is invalid
		elif details['__array__']['type'] not in self._VALID_ARRAY:
			self._type	= 'unique'
			sys.stderr.write('"' + str(details['__array__']['type']) + '" is not a valid type for __array__, assuming "unique"')

		# Else, store it
		else:
			self._type = details['__array__']['type']

		# Init the min/max values
		self._minimum = None
		self._maximum = None

		# If there's a minimum or maximum present
		if 'minimum' in details['__array__'] \
			or 'maximum' in details['__array__']:
			self.minmax(
				('minimum' in details['__array__'] and details['__array__']['minimum'] or None),
				('maximum' in details['__array__'] and details['__array__']['maximum'] or None)
			)

		# If there's an optional flag somewhere in the mix
		if '__optional__' in details:
			bOptional = details['__optional__']
			del details['__optional__']
		elif 'optional' in details['__array__']:
			bOptional = details['__array__']['optional']
		else:
			bOptional = None

		# Remove the __array__ field from details
		del details['__array__']

		# Strip off the special fields
		dSpecial = _strip_special(details)

		# Store the child
		self._node = _child(details)

		# If we had an optional flag, add it for the parent constructor
		if bOptional:
			details['__optional__'] = bOptional

		# If we had any special fields, add them back
		for k in dSpecial:
			details[k] = dSpecial[k]

		# Call the parent constructor
		super(ArrayNode, self).__init__(details, 'ArrayNode')

	def child(self):
		"""Child

		Returns the child node associated with the array

		Returns:
			_NodeInterface
		"""
		return self._node;

	def clean(self, value):
		"""Clean

		Goes through each of the values in the list, cleans it, stores it, and
		returns a new list

		Arguments:
			value {list} -- The value to clean

		Returns:
			list
		"""

		# If the value is None and it's optional, return as is
		if value is None and self._optional:
			return None

		# If the value is not a list
		if not isinstance(value, list):
			raise ValueError('value')

		# Recurse and return it
		return [self._node.clean(m) for m in value]

	def minmax(self, minimum=None, maximum=None):
		"""Min/Max

		Sets or gets the minimum and maximum number of items for the Array

		Arguments
			minimum {uint} -- The minimum value
			maximum {uint} -- The maximum value

		Raises:
			ValueError

		Returns:
			None
		"""

		# If neither minimum or maximum is set, this is a getter
		if(minimum is None and maximum is None):
			return {"minimum": self._minimum, "maximum": self._maximum}

		# If the minimum is set
		if minimum is not None:

			# If the value is not a valid int or long
			if not isinstance(minimum, (int, long)):

				# If it's a valid representation of an integer
				if isinstance(minimum, basestring) \
					and _typeToRegex['int'].match(minimum):

					# Convert it
					minimum = int(minimum, 0)

				# Else, raise an error
				else:
					raise ValueError('minimum')

			# If it's below zero
			if minimum < 0:
				raise ValueError('minimum')

			# Store the minimum
			self._minimum = minimum

		# If the maximum is set
		if maximum is not None:

			# If the value is not a valid int or long
			if not isinstance(maximum, (int, long)):

				# If it's a valid representation of an integer
				if isinstance(maximum, basestring) \
					and _typeToRegex['int'].match(maximum):

					# Convert it
					maximum = int(maximum, 0)

				# Else, raise an error
				else:
					raise ValueError('minimum')

			# It's below zero
			if maximum < 0:
				raise ValueError('maximum')

			# If we also have a minimum and the max is somehow below it
			if self._minimum \
				and maximum < self._minimum:
				raise ValueError('maximum')

			# Store the maximum
			self._maximum = maximum

	def toDict(self):
		"""To Dictionary

		Returns the Array as a dictionary in the same format as is used in
		constructing it

		Returns:
			dict
		"""

		# Init the dictionary we will return
		dRet = {}

		# If either a min or a max is set
		if self._minimum or self._maximum:

			# Set the array element as it's own dict
			dRet['__array__'] = {
				"type": self._type
			}

			# If there is a minimum
			if self._minimum:
				dRet['__array__']['minimum'] = self._minimum

			# If there is a maximum
			if self._maximum:
				dRet['__array__']['maximum'] = self._maximum

		# Else, just add the type as the array element
		else:
			dRet['__array__'] = self._type

		# Get the parents dict and add it to the return
		dRet.update(super(ArrayNode,self).toDict())

		# Get the nodes dict and also add it to the return
		dRet.update(self._node.toDict())

		# Return
		return dRet

	def type(self):
		"""Type

		Returns the type of array

		Returns:
			str
		"""
		return self._type

	def valid(self, value, level=[]):
		"""Valid

		Checks if a value is valid based on the instance's values

		Arguments:
			value {mixed} -- The value to validate

		Returns:
			bool
		"""

		# Reset validation failures
		self.validation_failures = []

		# If the value is None and it's optional, we're good
		if value is None and self._optional:
			return True

		# If the value isn't a list
		if not isinstance(value, list):
			self.validation_failures.append(('.'.join(level), str(value)))
			return False

		# Init the return, assume valid
		bRet = True

		# Keep track of duplicates
		if self._type == 'unique':
			lItems	= []

		# Go through each item in the list
		for i in range(len(value)):

			# Add the field to the level
			lLevel = level[:]
			lLevel.append('[%d]' % i)

			# If the element isn't valid, return false
			if not self._node.valid(value[i], lLevel):
				self.validation_failures.extend(self._node.validation_failures[:])
				bRet = False;
				continue;

			# If we need to check for duplicates
			if self._type == 'unique':

				# Try to get an existing item
				try:

					# If it is found, we have a duplicate
					iIndex = lItems.index(value[i])

					# Add the error to the list
					self.validation_failures.append(('.'.join(lLevel), 'duplicate of %s[%d]' % ('.'.join(level), iIndex)))
					bRet = False
					continue

				# If a Value Error is thrown, there is no duplicate, add the
				# 	value to the list and continue
				except ValueError:
					lItems.append(value[i])

		# If there's a minumum
		if self._minimum is not None:

			# If we don't have enough
			if len(value) < self._minimum:
				self.validation_failures.append(('.'.join(level), 'did not meet minimum'))
				bRet = False

		# If there's a maximum
		if self._maximum is not None:

			# If we have too many
			if len(value) > self._maximum:
				self.validation_failures.append(('.'.join(level), 'exceeds maximum'))
				bRet = False

		# Return whatever the result was
		return bRet

class HashNode(_BaseNode):
	"""Hash Node

	Handles objects similar to parents except where the keys are dynamic instead
	of static

	Extends:
		_BaseNode
	"""

	def __init__(self, details):
		"""Constructor

		Initialises the instance

		Arguments:
			details {dict} -- Details describing the type of values allowed for
				the node

		Raises:
			KeyError
			ValueError

		Returns:
			HashNode
		"""

		# If details is not a dict instance
		if not isinstance(details, dict):
			raise ValueError('details')

		# If the hash config is not found
		if '__hash__' not in details:
			raise KeyError('__hash__')

		# If there's an optional flag somewhere in the mix
		if '__optional__' in details:
			bOptional = details['__optional__']
			del details['__optional__']
		else:
			bOptional = None

		# If the hash is simply set to True, make it a string with no
		#	requirements
		if details['__hash__'] is True:
			details['__hash__'] = {"__type__":"string"}

		# Store the key using the hash value
		self._key = Node(details['__hash__'])

		# Remove it from details
		del details['__hash__']

		# Strip off the special fields
		dSpecial = _strip_special(details)

		print(dSpecial)

		# Store the child
		self._node = _child(details)

		# If we had an optional flag, add it for the parent constructor
		if bOptional:
			details['__optional__'] = bOptional

		# If we had any special fields, add them back
		for k in dSpecial:
			details[k] = dSpecial[k]

		print(details)

		# Call the parent constructor
		super(HashNode, self).__init__(details, 'HashNode')

	def child(self):
		"""Child

		Returns the child node associated with the hash

		Returns:
			_NodeInterface
		"""
		return self._node;

	def clean(self, value):
		"""Clean

		Makes sure both the key and value are properly stored in their correct
		representation

		Arguments:
			value {mixed} -- The value to clean

		Raises:
			ValueError

		Returns:
			mixed
		"""

		# If the value is None and it's optional, return as is
		if value is None and self._optional:
			return None

		# If the value is not a dict
		if not isinstance(value, dict):
			raise ValueError('value')

		# Recurse and return it
		return {str(self._key.clean(k)):self._node.clean(v) for k,v in iteritems(value)}

	def toDict(self):
		"""To Dict

		Returns the Hashed Node as a dictionary in the same format as is used in
		constructing it

		Returns:
			dict
		"""

		# Init the dictionary we will return
		dRet = {}

		# Add the hash key
		dRet['__hash__'] = self._key.toDict()

		# Get the parents dict and add it to the return
		dRet.update(super(HashNode,self).toDict())

		# Get the nodes dict and also add it to the return
		dRet.update(self._node.toDict())

		# Return
		return dRet

	def valid(self, value, level=[]):
		"""Valid

		Checks if a value is valid based on the instance's values

		Arguments:
			value {mixed} -- The value to validate

		Returns:
			bool
		"""

		# Reset validation failures
		self.validation_failures = []

		# If the value is None and it's optional, we're good
		if value is None and self._optional:
			return True

		# If the value isn't a dictionary
		if not isinstance(value, dict):
			self.validation_failures.append(('.'.join(level), str(value)))
			return False

		# Init the return, assume valid
		bRet = True

		# Go through each key and value
		for k,v in iteritems(value):

			# Add the field to the level
			lLevel = level[:]
			lLevel.append(k)

			# If the key isn't valid
			if not self._key.valid(k):
				self.validation_failures.append(('.'.join(lLevel), 'invalid key: %s' % str(k)))
				bRet = False
				continue

			# Check the value
			if not self._node.valid(v, lLevel):
				self.validation_failures.extend(self._node.validation_failures)
				bRet = False
				continue

		# Return whatever the result was
		return bRet

class Node(_BaseNode):
	"""Node

	Represents a single node of data, an immutable type like an int or a string

	Extends:
		_BaseNode
	"""

	_VALID_TYPES = ['any', 'base64', 'bool', 'date', 'datetime', 'decimal',
					'float', 'int', 'ip', 'json', 'md5', 'price', 'string',
					'time', 'timestamp', 'uint', 'uuid', 'uuid4']
	"""Valid Types

	Holds a list of valid values used to represent Node types"""

	def __init__(self, details):
		"""Constructor

		Initialises the instance

		Arguments:
			details {dict} -- Details describing the type of value allowed for
				the node

		Raises:
			KeyError
			ValueError

		Returns:
			Node
		"""

		# If we got a string
		if isinstance(details, basestring):
			details = {"__type__": details}

		# If details is not a dict instance
		elif not isinstance(details, dict):
			raise ValueError('details')

		# If the type is not found or is invalid
		if '__type__' not in details or details['__type__'] not in self._VALID_TYPES:
			raise KeyError('__type__')

		# Store the type and remove it from the details
		self._type = details['__type__']
		del details['__type__']

		# Init the value types
		self._regex = None
		self._options = None
		self._minimum = None
		self._maximum = None

		# If there's a regex string available
		if '__regex__' in details:
			self.regex(details['__regex__'])
			del details['__regex__']

		# Else if there's a list of options
		elif '__options__' in details:
			self.options(details['__options__'])
			del details['__options__']

		# Else
		else:

			# If there's a min or max
			bMin = ('__minimum__' in details and True or False)
			bMax = ('__maximum__' in details and True or False)

			if bMin or bMax:
				self.minmax(
					(bMin and details['__minimum__'] or None),
					(bMax and details['__maximum__'] or None)
				)

			if bMin: del details['__minimum__']
			if bMax: del details['__maximum__']

		# Call the parent constructor
		super(Node, self).__init__(details, 'Node')

	@staticmethod
	def __compare_ips(first, second):
		"""Compare IPs

		Compares two IPs and returns a status based on which is greater
		If first is less than second: -1
		If first is equal to second: 0
		If first is greater than second: 1

		Arguments:
			first {str} -- A string representing an IP address
			second {str} -- A string representing an IP address

		Returns:
			int
		"""

		# If the two IPs are the same, return 0
		if first == second:
			return 0

		# Create lists from the split of each IP, store them as ints
		lFirst = [int(i) for i in first.split('.')]
		lSecond = [int(i) for i in second.split('.')]

		# Go through each part from left to right until we find the
		# 	difference
		for i in [0, 1, 2, 3]:

			# If the part of x is greater than the part of y
			if lFirst[i] > lSecond[i]:
				return 1

			# Else if the part of x is less than the part of y
			elif lFirst[i] < lSecond[i]:
				return -1

	def clean(self, value):
		"""Clean

		Cleans and returns the new value

		Arguments:
			value {mixed} -- The value to clean

		Returns:
			mixed
		"""

		# If the value is None and it's optional, return as is
		if value is None and self._optional:
			return None

		# If it's an ANY, there is no reasonable expectation that we know what
		#	the value should be, so we return it as is
		if self._type == 'any':
			pass

		# Else if it's a basic string type
		elif self._type in ['base64', 'ip', 'string', 'uuid', 'uuid4']:

			# And not already a string
			if not isinstance(value, basestring):
				value = str(value)

		# Else if it's a BOOL just check if the value flags as positive
		elif self._type == 'bool':

			# If it's specifically a string, it needs to match a specific
			#	pattern to be true
			if isinstance(value, basestring):
				value = (value in ('true', 'True', 'TRUE', 't', 'T', 'yes', 'Yes', 'YES', 'y', 'Y', 'x', '1') and True or False);

			# Else
			else:
				value = (value and True or False)

		# Else if it's a date type
		elif self._type == 'date':

			# If it's a python type, use strftime on it
			if isinstance(value, (datetime.date, datetime.datetime)):
				value = value.strftime('%Y-%m-%d')

			# Else if it's already a string
			elif isinstance(value, basestring):
				pass

			# Else convert it to a string
			else:
				value = str(value)

		# Else if it's a datetime type
		elif self._type == 'datetime':

			# If it's a python type, use strftime on it
			if isinstance(value, datetime.datetime):
				value = value.strftime('%Y-%m-%d %H:%M:%S')
			elif isinstance(value, datetime.date):
				value = '%s 00:00:00' % value.strftime('%Y-%m-%d')

			# Else if it's already a string
			elif isinstance(value, basestring):
				pass

			# Else convert it to a string
			else:
				value = str(value)

		# Else if it's a decimal
		elif self._type == 'decimal':

			# If it's not a decimal
			if not isinstance(value, Decimal):
				value = Decimal(value)

			# Convert it to a string
			value = '{0:f}'.format(value)

		# Else if it's a float
		elif self._type == 'float':
			value = float(value)

		# Else if it's an int type
		elif self._type in ['int', 'timestamp', 'uint']:

			# If the value is a string
			if isinstance(value, basestring):

				# If it starts with 0
				if value[0] == '0' and len(value) > 1:

					# If it's followed by X or x, it's hex
					if value[1] in ['x', 'X'] and len(value) > 2:
						value = int(value, 16)

					# Else it's octal
					else:
						value = int(value, 8)

				# Else it's base 10
				else:
					value = int(value)

			# Else if it's not an int already
			elif not isinstance(value, int):
				value = int(value)

		# Else if it's a JSON type
		elif self._type == 'json':

			# If it's already a string
			if isinstance(value, basestring):
				pass

			# Else, encode it
			else:
				value = JSON.encode(value)

		# Else if it's an md5 type
		elif self._type == 'md5':

			# If it's a python type, get the hexadecimal digest
			if isinstance(value, _MD5_TYPE):
				value = value.hexdigest()

			# Else if it's a string
			elif isinstance(value, basestring):
				pass

			# Else, try to convert it to a string
			else:
				value = str(value)

		# Else if it's a price type
		elif self._type == 'price':

			# If it's not already a Decimal
			if not isinstance(value, Decimal):
				value = Decimal(value)

			# Make sure its got 2 decimal places
			value = "{0:f}".format(value.quantize(Decimal('1.00')))

		# Else if it's a time type
		elif self._type == 'time':

			# If it's a python type, use strftime on it
			if isinstance(value, (datetime.time, datetime.datetime)):
				value = value.strftime('%H:%M:%S')

			# Else if it's already a string
			elif isinstance(value, basestring):
				pass

			# Else convert it to a string
			else:
				value = str(value)

		# Else we probably forgot to add a new type
		else:
			raise Exception('%s has not been added to .clean()' % self._type)

		# Return the cleaned value
		return value

	def minmax(self, minimum=None, maximum=None):
		"""Min/Max

		Sets or gets the minimum and/or maximum values for the Node. For
		getting, returns {"minimum":mixed,"maximum":mixed}

		Arguments:
			minimum {mixed} -- The minimum value
			maximum {mixed} -- The maximum value

		Raises:
			TypeError, ValueError

		Returns:
			None | dict
		"""

		# If neither min or max is set, this is a getter
		if minimum is None and maximum is None:
			return {"minimum": self._minimum, "maximum": self._maximum};

		# If the minimum is set
		if minimum != None:

			# If the current type is a date, datetime, ip, or time
			if self._type in ['date', 'datetime', 'ip', 'time']:

				# Make sure the value is valid for the type
				if not isinstance(minimum, basestring) \
					or not _typeToRegex[self._type].match(minimum):
					raise ValueError('__minimum__')

			# Else if the type is an int (unsigned, timestamp), or a string in
			# 	which the min/max are lengths
			elif self._type in ['base64', 'int', 'string', 'timestamp', 'uint']:

				# If the value is not a valid int or long
				if not isinstance(minimum, (int, long)):

					# If it's a valid representation of an integer
					if isinstance(minimum, basestring) \
						and _typeToRegex['int'].match(minimum):

						# Convert it
						minimum = int(minimum, 0)

					# Else, raise an error
					else:
						raise ValueError('__minimum__')

					# If the type is meant to be unsigned
					if self._type in ['base64', 'string', 'timestamp', 'uint']:

						# And it's below zero
						if minimum < 0:
							raise ValueError('__minimum__')

			# Else if the type is decimal
			elif self._type == 'decimal':

				# Store it if it's valid, else throw a ValueError
				try:
					minimum = Decimal(minimum)
				except ValueError:
					raise ValueError('__minimum__')

			# Else if the type is float
			elif self._type == 'float':

				# Store it if it's valid, else throw a ValueError
				try:
					minimum = float(minimum)
				except ValueError:
					raise ValueError('__minimum__')

			# Else if the type is price
			elif self._type == 'price':

				# If it's not a valid representation of a price
				if not isinstance(minimum, basestring) or not _typeToRegex['price'].match(minimum):
					raise ValueError('__minimum__')

				# Store it as a Decimal
				minimum = Decimal(minimum)

			# Else we can't have a minimum
			else:
				raise TypeError('can not set __minimum__ for ' + self._type)

			# Store the minimum
			self._minimum = minimum

		# If the maximum is set
		if maximum != None:

			# If the current type is a date, datetime, ip, or time
			if self._type in ['date', 'datetime', 'ip', 'time']:

				# Make sure the value is valid for the type
				if not isinstance(maximum, basestring) \
					or not _typeToRegex[self._type].match(maximum):
					raise ValueError('__maximum__')

			# Else if the type is an int (unsigned, timestamp), or a string in
			# 	which the min/max are lengths
			elif self._type in ['base64', 'int', 'string', 'timestamp', 'uint']:

				# If the value is not a valid int or long
				if not isinstance(maximum, (int, long)):

					# If it's a valid representation of an integer
					if isinstance(maximum, basestring) \
						and _typeToRegex['int'].match(maximum):

						# Convert it
						maximum = int(maximum, 0)

					# Else, raise an error
					else:
						raise ValueError('__minimum__')

					# If the type is meant to be unsigned
					if self._type in ['base64', 'string', 'timestamp', 'uint']:

						# And it's below zero
						if maximum < 0:
							raise ValueError('__maximum__')

			# Else if the type is decimal
			elif self._type == 'decimal':

				# Store it if it's valid, else throw a ValueError
				try:
					maximum = Decimal(maximum)
				except ValueError:
					raise ValueError('__maximum__')

			# Else if the type is float
			elif self._type == 'float':

				# Store it if it's valid, else throw a ValueError
				try:
					minimum = float(minimum)
				except ValueError:
					raise ValueError('__maximum__')

			# Else if the type is price
			elif self._type == 'price':

				# If it's not a valid representation of a price
				if not isinstance(maximum, basestring) or not _typeToRegex['price'].match(maximum):
					raise ValueError('__maximum__')

				# Store it as a Decimal
				maximum = Decimal(maximum)

			# Else we can't have a maximum
			else:
				raise TypeError('can not set __maximum__ for ' + self._type)

			# If we also have a minimum
			if self._minimum is not None:

				# If the type is an IP
				if self._type == 'ip':

					# If the min is above the max, we have a problem
					if self.__compare_ips(self._minimum, maximum) == 1:
						raise ValueError('__maximum__')

				# Else any other data type
				else:

					# If the min is above the max, we have a problem
					if self._minimum > maximum:
						raise ValueError('__maximum__')

			# Store the maximum
			self._maximum = maximum

	def options(self, options=None):
		"""Options

		Sets or gets the list of acceptable values for the Node

		Arguments:
			options {list} -- A list of valid values

		Raises:
			TypeError, ValueError

		Returns:
			None | list
		"""

		# If opts aren't set, this is a getter
		if options is None:
			return self._options

		# If the options are not a list
		if not isinstance(options, (list, tuple)):
			raise ValueError('__options__')

		# If the type is not one that can have options
		if self._type not in ['base64', 'date', 'datetime', 'decimal', 'float', \
								'int', 'ip', 'md5', 'price', 'string', 'time', \
								'timestamp', 'uint', 'uuid', 'uuid4']:
			raise TypeError('can not set __options__ for ' + self._type)

		# Init the list of options to be saved
		lOpts = []

		# Go through each item and make sure it's unique and valid
		for i in range(len(options)):

			# Convert the value based on the type
			# If the type is a string one that we can validate
			if self._type in ['base64', 'date', 'datetime', 'ip', 'md5', 'time', 'uuid', 'uuid4']:

				# If the value is not a string or doesn't match its regex, raise
				# 	an error
				if not isinstance(options[i], basestring) \
					or not _typeToRegex[self._type].match(options[i]):
					raise ValueError('__options__[%d]' % i)

			# Else if it's decimal
			elif self._type == 'decimal':

				# If it's a Decimal
				if isinstance(options[i], Decimal):
					pass

				# Else if we can't conver it
				else:
					try: options[i] = Decimal(options[i])
					except ValueError:
						raise ValueError('__options__[%d]' % i)

			# Else if it's a float
			elif self._type == 'float':

				try:
					options[i] = float(options[i])
				except ValueError:
					raise ValueError('__options__[%d]' % i)

			# Else if it's an integer
			elif self._type in ['int', 'timestamp', 'uint']:

				# If we don't already have an int
				if not isinstance(options[i], (int, long)):

					# And we don't have a string
					if not isinstance(options[i], basestring):
						raise ValueError('__options__[%d]' % i)

					try:
						options[i] = int(options[i], 0)
					except ValueError:
						raise ValueError('__options__[%d]' % i)

				# If the type is unsigned and negative, raise an error
				if self._type in ['timestamp', 'uint'] and options[i] < 0:
					raise ValueError('__options__[' + str(i) + ']')

			# Else if it's a price
			elif self._type == 'price':

				# If it's a Decimal
				if isinstance(options[i], Decimal):
					pass

				# Else if it's not a valid price representation
				elif not isinstance(options[i], basestring) or not _typeToRegex['price'].match(options[i]):
					raise ValueError('__options__[%d]' % i)

				# Store it as a Decimal
				options[i] = Decimal(options[i])

			# Else if the type is a string
			elif self._type == 'string':

				# If the value is not a string
				if not isinstance(options[i], basestring):

					# If the value can't be turned into a string
					try:
						options[i] = str(options[i])
					except ValueError:
						raise ValueError('__options__[%d]' % i)

			# Else we have no validation for the type
			else:
				raise TypeError('can not set __options__ for ' + self._type)

			# If it's already in the list, raise an error
			if options[i] in lOpts:
				sys.stderr.write('__options__[' + str(i) + '] is a duplicate')

			# Store the option
			else:
				lOpts.append(options[i])

		# Store the list of options
		self._options = lOpts

	def regex(self, regex = None):
		"""Regex

		Sets or gets the regular expression used to validate the Node

		Arguments:
			regex {str} -- A standard regular expression string

		Raises:
			ValueError

		Returns:
			None | str
		"""

		# If regex was not set, this is a getter
		if regex is None:
			return self._regex

		# If the type is not a string
		if self._type != 'string':
			sys.stderr.write('can not set __regex__ for %s' % self._type)
			return

		# If it's not a valid string or regex
		if not isinstance(regex, (basestring, _REGEX_TYPE)):
			raise ValueError('__regex__')

		# Store the regex
		self._regex = regex

	def toDict(self):
		"""To Dict

		Returns the Node as a dictionary in the same format as is used in
		constructing it

		Returns:
			dict
		"""

		# Init the dictionary we will return
		dRet = {
			"__type__": self._type
		}

		# If there is a regex associated, add it
		if self._regex:
			dRet['__regex__'] = str(self._regex)

		# Else if there were options associated, add them
		elif self._options:
			dRet['__options__'] = self._options

		# Else check for min and max and add if either are found
		else:
			if self._minimum:
				dRet['__minimum__'] = self._minimum
			if self._maximum:
				dRet['__maximum__'] = self._maximum

		# Get the parents dict and add it to the return
		dRet.update(super(Node,self).toDict())

		# Return
		return dRet

	def type(self):
		"""Type

		Returns the type of Node

		Returns:
			str
		"""
		return self._type

	def valid(self, value, level=[]):
		"""Valid

		Checks if a value is valid based on the instance's values

		Arguments:
			value {mixed} -- The value to validate

		Returns:
			bool
		"""

		# Reset validation failures
		self.validation_failures = []

		# If the value is None and it's optional, we're good
		if value is None and self._optional:
			return True

		# If we are validating an ANY field, immediately return true
		if self._type == 'any':
			pass

		# If we are validating a DATE, DATETIME, IP or TIME data point
		elif self._type in ['base64', 'date', 'datetime', 'ip', 'md5', 'time', 'uuid', 'uuid4']:

			# If it's a date or datetime type and the value is a python type
			if self._type == 'date' and isinstance(value, (datetime.date, datetime.datetime)):
				value = value.strftime('%Y-%m-%d')

			elif self._type == 'datetime' and isinstance(value, (datetime.date, datetime.datetime)):
				if isinstance(value, datetime.datetime):
					value = value.strftime('%Y-%m-%d %H:%M:%S')
				elif isinstance(value, datetime.date):
					value = '%s 00:00:00' % value.strftime('%Y-%m-%d')

			# If it's a time type and the value is a python type
			elif self._type == 'time' and isinstance(value, (datetime.time, datetime.datetime)):
				value = value.strftime('%H:%M:%S')

			# Else if the type is md5 and the value is a python type
			elif self._type == 'md5' and isinstance(value, _MD5_TYPE):
				value = value.hexdigest()

			# If the value is not a string
			elif not isinstance(value, basestring):
				self.validation_failures.append(('.'.join(level), 'not a string'))
				return False

			# If there's no match
			if not _typeToRegex[self._type].match(value):
				self.validation_failures.append(('.'.join(level), 'failed regex (internal)'))
				return False

			# If we are checking an IP
			if self._type == 'ip':

				# If there's a min or a max
				if self._minimum is not None or self._maximum is not None:

					# If the IP is greater than the maximum
					if self._maximum is not None and self.__compare_ips(value, self._maximum) == 1:
						self.validation_failures.append(('.'.join(level), 'exceeds maximum'))
						return False

					# If the IP is less than the minimum
					if self._minimum is not None and self.__compare_ips(value, self._minimum) == -1:
						self.validation_failures.append(('.'.join(level), 'did not meet minimum'))
						return False

					# Return OK
					return True

		# Else if we are validating some sort of integer
		elif self._type in ['int', 'timestamp', 'uint']:

			# If the type is a bool, fail immediately
			if type(value) == bool:
				self.validation_failures.append(('.'.join(level), 'is a bool'))
				return False

			# If it's not an int
			if not isinstance(value, (int, long)):

				# And it's a valid representation of an int
				if isinstance(value, basestring) \
					and _typeToRegex['int'].match(value):

					# If it starts with 0
					if value[0] == '0' and len(value) > 1:

						# If it's followed by X or x, it's hex
						if value[1] in ['x', 'X'] and len(value) > 2:
							value = int(value, 16)

						# Else it's octal
						else:
							value = int(value, 8)

					# Else it's base 10
					else:
						value = int(value)

				# Else, return false
				else:
					self.validation_failures.append(('.'.join(level), 'not an integer'))
					return False

			# If it's not signed
			if self._type in ['timestamp', 'uint']:

				# If the value is below 0
				if value < 0:
					self.validation_failures.append(('.'.join(level), 'signed'))
					return False

		# Else if we are validating a bool
		elif self._type == 'bool':

			# If it's already a bool
			if isinstance(value, bool):
				return True

			# If it's an int or long at 0 or 1
			if isinstance(value, (int, long)) and value in [0, 1]:
				return True

			# Else if it's a string
			elif isinstance(value, basestring):

				# If it's t, T, 1, f, F, or 0
				if value in ['true', 'True', 'TRUE', 't', 'T', '1', 'false', 'False', 'FALSE', 'f', 'F', '0']:
					return True
				else:
					self.validation_failures.append(('.'.join(level), 'not a valid string representation of a bool'))
					return False

			# Else it's no valid type
			else:
				self.validation_failures.append(('.'.join(level), 'not valid bool replacement'))
				return False

		# Else if we are validating a decimal value
		elif self._type == 'decimal':

			# If the type is a bool, fail immediately
			if type(value) == bool:
				self.validation_failures.append(('.'.join(level), 'is a bool'))
				return False

			# If it's already a Decimal
			if isinstance(value, Decimal):
				pass

			# Else if we fail to convert the value
			else:
				try: value = Decimal(value)
				except (DecimalInvalid, TypeError, ValueError):
					self.validation_failures.append(('.'.join(level), 'can not be converted to decimal'))
					return False

		# Else if we are validating a floating point value
		elif self._type == 'float':

			# If the type is a bool, fail immediately
			if type(value) == bool:
				self.validation_failures.append(('.'.join(level), 'is a bool'))
				return False

			# If it's already a float
			if isinstance(value, float):
				pass

			# Else if we fail to convert the value
			else:
				try: value = float(value)
				except (ValueError, TypeError):
					self.validation_failures.append(('.'.join(level), 'can not be converted to float'))
					return False

		# Else if we are validating a JSON string
		elif self._type == 'json':

			# If it's already a string
			if isinstance(value, basestring):

				# Try to decode it
				try:
					value = JSON.decode(value)
					return True
				except ValueError:
					self.validation_failures.append(('.'.join(level), 'Can not be decoded from JSON'))
					return False

			# Else
			else:

				# Try to encode it
				try:
					value = JSON.encode(value)
					return True
				except (ValueError, TypeError):
					self.validation_failures.append(('.'.join(level), 'Can not be encoded to JSON'))
					return False

		# Else if we are validating a price value
		elif self._type == 'price':

			# If the type is a bool, fail immediately
			if type(value) == bool:
				self.validation_failures.append(('.'.join(level), 'is a bool'))
				return False

			# If it's not a floating point value
			if not isinstance(value, Decimal):

				# But it is a valid string representing a price, or a float
				if isinstance(value, (basestring, float)) \
					and _typeToRegex['price'].match(str(value)):

					# Convert it to a decimal
					value = Decimal(value).quantize(Decimal('1.00'))

				# Else if it's an int
				elif isinstance(value, int):

					# Convert it to decimal
					value = Decimal(str(value) + '.00')

				# Else whatever it is is no good
				else:
					self.validation_failures.append(('.'.join(level), 'failed regex (internal)'))
					return False

			# Else
			else:

				# If the exponent is longer than 2
				if abs(value.as_tuple().exponent) > 2:
					self.validation_failures.append(('.'.join(level), 'too many decimal points'))
					return False

		# Else if we are validating a string value
		elif self._type == 'string':

			# If the value is not some form of string
			if not isinstance(value, basestring):
				self.validation_failures.append(('.'.join(level), 'is not a string'))
				return False

			# If we have a regex
			if self._regex:

				# If it doesn't match the regex
				if re.match(self._regex, value) == None:
					self.validation_failures.append(('.'.join(level), 'failed regex (custom)'))
					return False

			# Else
			elif self._minimum or self._maximum:

				# If there's a minimum length and we don't reach it
				if self._minimum and len(value) < self._minimum:
					self.validation_failures.append(('.'.join(level), 'not long enough'))
					return False

				# If there's a maximum length and we surpass it
				if self._maximum and len(value) > self._maximum:
					self.validation_failures.append(('.'.join(level), 'too long'))
					return False

				# Return OK
				return True

		# If there's a list of options
		if self._options is not None:

			# Returns based on the option's existance
			if value not in self._options:
				self.validation_failures.append(('.'.join(level), 'not in options'))
				return False
			else:
				return True

		# Else check for basic min/max
		else:

			# If the value is less than the minimum
			if self._minimum and value < self._minimum:
				self.validation_failures.append(('.'.join(level), 'did not meet minimum'))
				return False

			# If the value is greater than the maximum
			if self._maximum and value > self._maximum:
				self.validation_failures.append(('.'.join(level), 'exceeds maximum'))
				return False

		# Value has no issues
		return True

class OptionsNode(_NodeInterface):
	"""Options Node

	Represents a node which can have several different types of values/Nodes and
	still be valid

	Extends:
		_NodeInterface
	"""

	def __getitem__(self, index):
		"""Get Item (__getitem__)

		Returns a specific index from the options

		Arguments:
			index {uint} -- The index to get

		Raises:
			IndexError

		Returns:
			mixed
		"""
		return self._nodes[index]

	def __init__(self, details):
		"""Constructor

		Initialises the instance

		Arguments:
			details {dict} -- Details describing the type of values allowed for
				the node

		Raises:
			ValueError

		Returns:
			OptionsNode
		"""

		# If details is not a list instance
		if not isinstance(details, list):
			raise ValueError('details in ' + self.__class__.__name__ + '.' + sys._getframe().f_code.co_name + ' must be a list')

		# Init the variable used to identify the last falures in validation
		self.validation_failures = {}

		# Init the optional flag, assume all nodes are optional until we find
		#	one that isn't
		self._optional = True

		# Init the internal list
		self._nodes = []

		# Go through each element in the list
		for i in range(len(details)):

			# If it's another Node instance
			if isinstance(details[i], _BaseNode):
				self._nodes.append(details[i])
				continue

			# If the element is a dict instance
			elif isinstance(details[i], (dict, list)):

				# Store the child
				self._nodes.append(_child(details[i]))

			# Whatever was sent is invalid
			else:
				raise ValueError('details[' + str(i)  + '] in ' + self.__class__.__name__ + '.' + sys._getframe().f_code.co_name + ' must be a dict')

			# If the element is not optional, then the entire object can't be
			#	optional
			if not self._nodes[-1]._optional:
				self._optional = False

	def __iter__(self):
		"""Iterator (__iter__)

		Returns an iterator to the nodes list

		Returns:
			ListIterator
		"""
		return iter(self._nodes)

	def __len__(self):
		"""Length (__len__)

		Returns the length of the list of option nodes

		Returns:
			uint
		"""
		return len(self._nodes)

	def className(self):
		"""Class Name

		Returns a string reprentation of the class

		Returns:
			str
		"""
		return 'OptionsNode'

	def clean(self, value):
		"""Clean

		Uses the valid method to check which type the value is, and then calls
		the correct version of clean on that node

		Arguments:
			value {mixed} -- The value to clean

		Returns:
			mixed
		"""

		# If the value is None and it's optional, return as is
		if value is None and self._optional:
			return None

		# Go through each of the nodes
		for i in range(len(self._nodes)):

			# If it's valid
			if self._nodes[i].valid(value):

				# Use it's clean
				return self._nodes[i].clean(value)

		# Something went wrong
		raise ValueError('value', value)

	def get(self, index, default=None):
		"""Get

		Returns the node of a specific index from the options

		Arguments:
			index {uint} -- The index to get
			default {mixed} Value to return if the key does not exist

		Returns:
			mixed
		"""
		try: return self._nodes[index]
		except IndexError: return default

	def toDict(self):
		"""To Dict

		Returns the Nodes as a list of dictionaries in the same format as is
		used in constructing them

		Returns:
			list
		"""
		return [d.toDict() for d in self._nodes]

	def toJSON(self):
		"""To JSON

		Returns a JSON string representation of the instance

		Returns:
			str
		"""
		return JSON.encode(self.toDict())

	def valid(self, value, level=[]):
		"""Valid

		Checks if a value is valid based on the instance's values

		Arguments:
			value {mixed} -- The value to validate

		Returns:
			bool
		"""

		# Reset validation failures
		self.validation_failures = []

		# If the value is None and it's optional, we're good
		if value is None and self._optional:
			return True

		# Go through each of the nodes
		for i in range(len(self._nodes)):

			# If it's valid
			if self._nodes[i].valid(value):

				# Return OK
				return True

		# Not valid for anything
		self.validation_failures.append(('.'.join(level), 'no valid option'))
		return False

class Parent(_BaseNode):
	"""Parent

	Represents defined keys mapped to other Nodes which themselves could be
	Parents

	Extends:
		_BaseNode
	"""

	def __contains__(self, key):
		"""Contain (__contains__)

		Returns whether a specific key exists in the parent

		Arguments:
			key {str} -- The key to check for

		Returns:
			bool
		"""
		return key in self._nodes

	def __getitem__(self, key):
		"""Get Item (__getitem__)

		Returns a specific key from the parent

		Arguments:
			key {str} -- The key to get

		Raises:
			KeyError

		Returns:
			mixed
		"""
		if key in self._nodes:	return self._nodes[key]
		else:					raise KeyError(key)

	def __init__(self, details):
		"""Constructor

		Initialises the instance

		Arguments:
			details {dict} -- Details describing the type of values allowed for
				the node

		Raises:
			ValueError

		Returns:
			Parent
		"""

		# If details is not a dict instance
		if not isinstance(details, dict):
			raise ValueError('details in ' + self.__class__.__name__ + '.' + sys._getframe().f_code.co_name + ' must be a dict')

		# Init the nodes and requires dicts
		self._nodes = {}
		self._requires = {}

		# Go through the keys in the details
		for k in tuple(details.keys()):

			# If key is standard
			if _standardField.match(k):

				# If it's a Node
				if isinstance(details[k], _NodeInterface):

					# Store it as is
					self._nodes[k] = details[k]

				# Else
				else:
					self._nodes[k] = _child(details[k])

				# Remove the key from the details
				del details[k]

		# If there's a require hash available
		if '__require__' in details:
			self.requires(details['__require__'])
			del details['__require__']

		# Call the parent constructor with whatever details are left
		super(Parent, self).__init__(details, 'Parent')

	def __iter__(self):
		"""Iterator (__iter__)

		Returns an iterator to the parent's keys

		Returns:
			dictionary-keyiterator
		"""
		if hasattr(self._nodes, 'iterkeys'):
			return self._nodes.iterkeys()
		else:
			return iter(self._nodes.keys())

	def clean(self, value):
		"""Clean

		Goes through each of the values in the dict, cleans it, stores it, and
		returns a new dict

		Arguments:
			value {dict} -- The value to clean

		Returns:
			dict
		"""

		# If the value is None and it's optional, return as is
		if value is None and self._optional:
			return None

		# If the value is not a dict
		if not isinstance(value, dict):
			raise ValueError('value')

		# Init the return value
		dRet = {}

		# Go through each value and clean it using the associated node
		for k in value.keys():
			try:
				dRet[k] = self._nodes[k].clean(value[k])
			except KeyError:
				raise ValueError('%s is not a valid node in the parent' % k)

		# Return the cleaned values
		return dRet

	def get(self, key, default=None):
		"""Get

		Returns the node of a specific key from the parent

		Arguments:
			key {str} -- The key to get
			default {mixed} Value to return if the key does not exist

		Returns:
			mixed
		"""
		if key in self._nodes: return self._nodes[key]
		else: return default

	def has_key(self, key):
		"""Has Key

		Returns whether a specific key exists in the parent

		Arguments:
			key {str} -- The key to check for

		Returns:
			bool
		"""
		return key in self._nodes

	def iterkeys(self):
		"""Iterate Keys

		Returns an iterator to the parent's keys

		Returns:
			dictionary-keyiterator
		"""
		if hasattr(self._nodes, 'iterkeys'):
			return self._nodes.iterkeys()
		else:
			return iter(self._nodes.keys())

	def keys(self):
		"""Keys

		Returns a list of the node names in the parent

		Returns:
			list
		"""
		if hasattr(self._nodes, 'iterkeys'):
			return self._nodes.keys()
		else:
			return tuple(self._nodes.keys())

	def requires(self, require=None):
		"""Requires

		Sets the require rules used to validate the Parent

		Arguments:
			require {dict} -- A dictionary expressing requirements of fields

		Raises:
			ValueError

		Returns:
			None
		"""

		# If require is None, this is a getter
		if require is None:
			return self._requires

		# If it's not a valid dict
		if not isinstance(require, dict):
			raise ValueError('__require__')

		# Go through each key and make sure it goes with a field
		for k,v in iteritems(require):

			# If the field doesn't exist
			if k not in self._nodes:
				raise ValueError('__require__[%s]' % str(k))

			# If the value is a string
			if isinstance(v, basestring):
				v = [v]

			# Else if it's not a list type
			elif not isinstance(v, (tuple,list)):
				raise ValueError('__require__[%s]' % str(k))

			# Make sure each required field also exists
			for s in v:
				if s not in self._nodes:
					raise ValueError('__require__[%s]: %s' % (str(k), str(v)))

			# If it's all good
			self._requires[k] = v

	def toDict(self):
		"""To Dict

		Returns the Parent as a dictionary in the same format as is used in
		constructing it

		Returns:
			dict
		"""

		# Get the parents dict as the starting point of our return
		dRet = super(Parent,self).toDict()

		# Go through each field and add it to the return
		for k,v in iteritems(self._nodes):
			dRet[k] = v.toDict()

		# Return
		return dRet

	def valid(self, value, level=[]):
		"""Valid

		Checks if a value is valid based on the instance's values

		Arguments:
			value {mixed} -- The value to validate

		Returns:
			bool
		"""

		# Reset validation failures
		self.validation_failures = []

		# If the value is None and it's optional, we're good
		if value is None and self._optional:
			return True

		# If the value isn't a dictionary
		if not isinstance(value, dict):
			self.validation_failures.append(('.'.join(level), str(value)))
			return False

		# Init the return, assume valid
		bRet = True

		# Go through each node in the instance
		for k in self._nodes:

			# Add the field to the level
			lLevel = level[:]
			lLevel.append(k)

			# If we are missing a node
			if k not in value:

				# If the value is not optional
				if not self._nodes[k]._optional:
					self.validation_failures.append(('.'.join(lLevel), 'missing'))
					bRet = False

				# Continue to next node
				continue

			# If the element isn't valid, return false
			if not self._nodes[k].valid(value[k], lLevel):
				self.validation_failures.extend(self._nodes[k].validation_failures)
				bRet = False
				continue

			# If the element requires others
			if k in self._requires:

				# Go through each required field
				for f in self._requires[k]:

					# If the field doesn't exist in the value
					if f not in value or value[f] in ('0000-00-00','',None):
						self.validation_failures.append(('.'.join(lLevel), 'requires \'%s\' to also be set' % str(f)))
						bRet = False

		# Return whatever the result was
		return bRet

	def viewkeys(self):
		"""View Keys

		Returns a view associated with the parent's keys

		Returns:
			dict_view
		"""
		if hasattr(self._nodes, 'viewkeys'):
			return self._nodes.viewkeys()
		else:
			return self._nodes.keys()

class Tree(Parent):
	"""Tree

	Represents the master parent of a record, holds special data to represent
	how the entire tree is stored

	Extends:
		Parent
	"""

	def __init__(self, details):
		"""Constructor

		Initialises the instance

		Arguments:
			details {dict} -- Details describing the type of values allowed for
				the node

		Raises:
			KeyError
			ValueError

		Returns:
			Tree
		"""

		# If details is not a dict instance
		if not isinstance(details, dict):
			raise ValueError('details in ' + self.__class__.__name__ + '.' + sys._getframe().f_code.co_name + ' must be a dict')

		# If the name is not set
		if '__name__' not in details:
			raise KeyError('__name__')

		# If the name is not valid
		if not _standardField.match(details['__name__']):
			raise ValueError('__name__')

		# Store the name then delete it
		self._name = details['__name__']
		del details['__name__']

		# If for some reason the array flag is set, remove it
		if '__array__' in details:
			del details['__array__']

		# Call the parent constructor
		super(Tree, self).__init__(details)

		# Overwrite classname
		self._class = 'Tree'

	def toDict(self):
		"""To Dict

		Returns the Tree as a dictionary in the same format as is used in
		constructing it

		Returns:
			dict
		"""

		# Init the dictionary we will return
		dRet = {
			"__name__": self._name
		}

		# Get the parents dict and add it to the return
		dRet.update(super(Tree,self).toDict())

		# Return
		return dRet

	def valid(self, value, include_name=True):
		"""Valid

		Checks if a value is valid based on the instance's values

		Arguments:
			value {mixed} -- The value to validate
			include_name {bool} -- If true, Tree's name will be prepended to
				all error keys

		Returns:
			bool
		"""

		# Call the parent valid method and return the result
		return super(Tree, self).valid(value, include_name and [self._name] or [])
