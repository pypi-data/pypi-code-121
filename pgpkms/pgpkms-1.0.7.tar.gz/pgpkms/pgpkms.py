import hashlib

from botocore import session as aws
from io import BufferedReader, BytesIO, TextIOWrapper
from pyasn1_modules.rfc3279 import RSAPublicKey
from pyasn1_modules.rfc5280 import SubjectPublicKeyInfo
from pyasn1.codec.der import decoder
from time import time
from os import linesep

from .armour import armour

KEY_VERSION = b'\x04'
KEY_ALGORITHM_RSA = b'\x01'

PGP_SIGNATURE_TAG = 0x02
PGP_PUBLIC_KEY_TAG = 0x06
PGP_USER_ID_TAG = 0x0d

SIGNATURE_VERSION = b'\x04'

SIGNATURE_TYPE_BINARY_DOCUMENT = b'\x00'
SIGNATURE_TYPE_CANONICAL_TEXT = b'\x01'
SIGNATURE_TYPE_PUBLIC_KEY = b'\x13'

SUBPACKET_ISSUER_FINGERPRINT      = b'\x21'
SUBPACKET_SIGNATURE_CREATION_TIME = b'\x02'
SUBPACKET_KEY_FLAGS               = b'\x1b'
SUBPACKET_ENCRYPTION_ALGORITHMS   = b'\x0b'
SUBPACKET_HASH_ALGORITHMS         = b'\x15'
SUBPACKET_COMPRESSION_ALGORITHMS  = b'\x16'
SUBPACKET_KEY_FEATURES            = b'\x1e'
SUBPACKET_KEY_SERVER_PREFERENCES  = b'\x17'
SUBPACKET_ISSUER                  = b'\x10'

class KmsPgpKey:
  """
  The "KmsPgpKey" class wraps an AWS KMS key and is capable of producing
  signatures compatible with GnuPG / OpenPGP.
  """

  def __init__(self, key_id, kms_client = None):
    """
    Initialize a new "KmsPgpKey" instance.

    Parameters:
    -----------

    key_id (str, required):
      The ID, ARN or alias of the AWS KMS key. This can be one of the following:
        - Key ID: e.g. "1234abcd-12ab-34cd-56ef-1234567890ab"
        - Key ARN: e.g. "arn:aws:kms:us-east-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab"
        - Alias name: e.g. "alias/ExampleAlias"
        - Alias ARN: "arn:aws:kms:us-east-2:111122223333:alias/ExampleAlias"

    kms_client:
      A BotoCore "KMS" client, if "None" this will be initialized as:
        | session = botocore.session.get_session()
        | kms_client = session.create_client('kms')

    Notes:
    ------

    In order to supply the User ID information in the PGP key, the AWS KMS key
    should provide two tags:

      - PGPName: the display name to associate with the PGP key.
      - PGPEmail: the email address to associate with the PGP key.

    If those tags are not present a simple user id will be generated from the
    AWS KMS key id (an opaque random UUID).
    """

    # Create a KMS client if none was specified
    if kms_client == None:
      session = aws.get_session()
      kms_client = session.create_client('kms')

    # Get the key and remember the ARN
    key = kms_client.get_public_key(KeyId="alias/PGP_KEY")
    self.arn = key['KeyId']

    # Get metadata and tags
    metadata = kms_client.describe_key(KeyId=self.arn)
    tags = kms_client.list_resource_tags(KeyId=self.arn)

    # The creation_date as an integer in seconds from the epoch
    self.creation_date = int(metadata['KeyMetadata']['CreationDate'].timestamp())

    # The user_id is calculated from the "PGPName" and "PGPEmail" tags
    name = None
    email = None

    for tag in tags['Tags']:
      if tag['TagKey'] == 'PGPName':
        name = tag['TagValue']
      elif tag['TagKey'] == 'PGPEmail':
        email = tag['TagValue']

    if (name != None) & (email != None):
      self.user_id = '%s <%s>' % (name, email)
    elif email != None:
      self.user_id = email
    elif name != None:
      self.user_id = name
    else:
      self.user_id = 'PgpKms-AwsWrapper (%s)' % (metadata['KeyMetadata']['KeyId'])

    # Check the AWS "KeySpec" to assert type and length of the key
    key_spec = key['KeySpec']
    self.bits = 2048 if key_spec == 'RSA_2048' else \
                3072 if key_spec == 'RSA_3072' else \
                4096 if key_spec == 'RSA_4096' else \
                None

    assert self.bits is not None, 'Wrong spec %s for key %s' % (key_spec, self.arn)

    # Decode the ASN.1 structure to get modulo and exponent as numbers
    public_key = key['PublicKey']

    (spki, rest) = decoder.decode(public_key, asn1Spec=SubjectPublicKeyInfo())

    spk = spki.getComponentByName('subjectPublicKey').asOctets()

    (pk, rest) = decoder.decode(spk, RSAPublicKey())

    self.modulus = int(pk['modulus'])
    self.exponent = int(pk['publicExponent'])



  @property
  def __pgp_key(self):
    # We should really be using 0x03 (RSA Sign-Only) as KEY_ALGORITHM here, as
    # AWS keys can either SIGN only or ENCRYPT only... But RFC-4880 in section
    # 9.1 says "RSA Encrypt-Only (0x2) and RSA Sign-Only (0x3) are deprecated
    # and SHOULD NOT be generated, but may be interpreted."
    return \
      KEY_VERSION + \
      self.creation_date.to_bytes(4, 'big') + \
      KEY_ALGORITHM_RSA + \
      __mpi(self.modulus, self.bits) + \
      __mpi(self.exponent)



  @property
  def __pgp_fingerprint(self):
    key = self.__pgp_key
    hash = hashlib.sha1()
    hash.update(b'\x99') # marker byte for the v4 key
    hash.update(len(key).to_bytes(2, 'big')) # then 2 bytes length
    hash.update(key) # and finally key
    return hash.digest()



  @property
  def __pgp_key_id(self):
    fingerprint = self.__pgp_fingerprint
    return fingerprint[-8:]



  def __sign_kms(self, digest, hash_length, kms_client=None):
    # Create a KMS client if none was specified
    if kms_client == None:
      session = aws.get_session()
      kms_client = session.create_client('kms')

    # PGP luckily wants PKCS1 v1.5 for signatures
    signature = kms_client.sign(
      KeyId = self.arn,
      Message = digest,
      MessageType = 'DIGEST',
      SigningAlgorithm = 'RSASSA_PKCS1_V1_5_SHA_%s' % hash_length,
    )

    # Get the integer, as we'll convert it in a PGP's own MPI
    return int.from_bytes(signature['Signature'], 'big')



  def to_pgp(self, hash='sha256', armoured=True, kms_client=None):
    """
    Return the public key from AWS KMS wrapped in an OpenPGP v4 key format.

    Parameters:
    -----------

    hash (str):
      The hashing algorithm used to prepare the self-signature of the public key.

    armoured (bool):
      Whether the returned key should be armoured (text) or not (binary).

    kms_client:
      A BotoCore "KMS" client, if "None" this will be initialized as:
        | session = botocore.session.get_session()
        | kms_client = session.create_client('kms')

    Returns:
    --------

    A "bytes" string containing the GnuPG / OpenPGP formatted public key.
    """

    (hash_algorithm, hash_length, hasher) = \
      (b'\x08', 256, hashlib.sha256()) if hash == 'sha256' else \
      (b'\x09', 384, hashlib.sha384()) if hash == 'sha384' else \
      (b'\x0a', 512, hashlib.sha512()) if hash == 'sha512' else \
      (None, None)

    assert hash_algorithm, 'Wrong hash algorithm %s for signature' % (hash)

    # Start preparing the signature
    payload =  SIGNATURE_VERSION
    payload += SIGNATURE_TYPE_PUBLIC_KEY
    payload += KEY_ALGORITHM_RSA
    payload += hash_algorithm

    # Those are all our hashed subpackets. Note the encryption algorithm and
    # compression algorithms in here... They shouldn't be (as with AWS keys we
    # we can only either sign _OR_ encrypt). That saidt most other keys I've
    # seen include them (and RFC-4880 deprecates "sign-only" keys), so we throw
    # our hands up in the air and party like it's 1998! (yes, this is shit!)
    hashed_subpackets =  __subpacket(SUBPACKET_ISSUER_FINGERPRINT, b'\x04' + self.__pgp_fingerprint)
    hashed_subpackets += __subpacket(SUBPACKET_SIGNATURE_CREATION_TIME, self.creation_date.to_bytes(4, 'big'))
    hashed_subpackets += __subpacket(SUBPACKET_KEY_FLAGS, b'\x03') # OR-ed flags: 0x01 => certify, 0x02 => sign
    hashed_subpackets += __subpacket(SUBPACKET_ENCRYPTION_ALGORITHMS, b'\x09\x08\x07') # 0x09 => AES256, 0x08 => AES192, 0x07 => AES128
    hashed_subpackets += __subpacket(SUBPACKET_HASH_ALGORITHMS, b'\x0a\x09\x08') # 0x0A => SHA512, 0x09 => SHA384, 0x08 => SHA256
    hashed_subpackets += __subpacket(SUBPACKET_COMPRESSION_ALGORITHMS, b'\x02\x03\x01') # 0x02 => ZLib, 0x03 => BZip2, 0x01 => ZIP
    hashed_subpackets += __subpacket(SUBPACKET_KEY_FEATURES, b'\x01') # 0x01 => Modification detection
    hashed_subpackets += __subpacket(SUBPACKET_KEY_SERVER_PREFERENCES, b'\x80') # 0x80 => No modify
    hashed_subpackets_length = len(hashed_subpackets)

    payload += hashed_subpackets_length.to_bytes(2, 'big')
    payload += hashed_subpackets

    # ==========================================================================
    # At this point we want to calculate the data to be signed. This is
    # done by concatenating the key, the user_id packet, the signature
    # _UP_TO_THIS_POINT_ (excludes any unhashed data and stuff) and a trailer

    # Start with the key... With RSA it's the simple key
    signature_key = self.__pgp_key
    signature_data = b'\x99'
    signature_data += len(signature_key).to_bytes(2, 'big')
    signature_data += signature_key

    # Add the user id
    if self.user_id != None:
      signature_user = self.user_id.encode('utf-8')
      signature_data += b'\xb4'
      signature_data += len(signature_user).to_bytes(4, 'big')
      signature_data += signature_user

    # Then add the signature payload, from version to hashed subpackets
    signature_data += payload

    # Now we add the "trailer": 0x04 (version) 0xff ("stuff") and signature length
    signature_data += b'\x04\xff'
    signature_data += len(payload).to_bytes(4, 'big')

    # And then we create a nice hash of our signature data
    hasher.update(signature_data)
    digest = hasher.digest()

    # Call the KMS to sign our digest
    signature = self.__sign_kms(digest, hash_length, kms_client = kms_client)

    # ==========================================================================
    # Now that we have the signature_body and signature hash, we can continue
    # preparing the payload of our signature packet...

    unhashed_subpackets = __subpacket(SUBPACKET_ISSUER, self.__pgp_key_id)
    unhashed_subpackets_length = len(unhashed_subpackets)

    payload += unhashed_subpackets_length.to_bytes(2, 'big')
    payload += unhashed_subpackets

    payload += digest[:2] # hashed value prefix
    payload += __mpi(signature, self.bits)

    # ==========================================================================
    # Finally, we prepare our message, and decide whether to armour it or not

    message = __packet(PGP_PUBLIC_KEY_TAG, self.__pgp_key)

    if self.user_id != None:
      message += __packet(PGP_USER_ID_TAG, self.user_id.encode('utf-8'))

    message += __packet(PGP_SIGNATURE_TAG, payload)

    return armour('PUBLIC KEY BLOCK', message) if armoured else message



  def sign(self, input, hash='sha256', armoured=True, kms_client=None):
    """
    Sign the specified input using this key, and returns the signature in a
    format compatible with GnuPG / OpenPGP.

    Parameters:
    -----------

    input (str, bytes or BufferedReader):
      The data to be signed.

    hash (str):
      The hashing algorithm used to sign the data.

    armoured (bool):
      Whether the returned signature should be armoured (text) or not (binary).

    kms_client:
      A BotoCore "KMS" client, if "None" this will be initialized as:
        | session = botocore.session.get_session()
        | kms_client = session.create_client('kms')

    Returns:
    --------

    A "bytes" string containing the GnuPG / OpenPGP formatted signature.
    """

    (hash_algorithm, hash_length, hasher) = \
      (b'\x08', 256, hashlib.sha256()) if hash == 'sha256' else \
      (b'\x09', 384, hashlib.sha384()) if hash == 'sha384' else \
      (b'\x0a', 512, hashlib.sha512()) if hash == 'sha512' else \
      (None, None)

    assert hash_algorithm, 'Wrong hash algorithm %s for signature' % (hash)

    # Start preparing the signature
    payload =  SIGNATURE_VERSION
    payload += SIGNATURE_TYPE_BINARY_DOCUMENT
    payload += KEY_ALGORITHM_RSA
    payload += hash_algorithm

    # Those are all our hashed subpackets (only fingerprint and time).
    hashed_subpackets =  __subpacket(SUBPACKET_ISSUER_FINGERPRINT, b'\x04' + self.__pgp_fingerprint)
    hashed_subpackets += __subpacket(SUBPACKET_SIGNATURE_CREATION_TIME, int(time()).to_bytes(4, 'big'))
    hashed_subpackets_length = len(hashed_subpackets)

    payload += hashed_subpackets_length.to_bytes(2, 'big')
    payload += hashed_subpackets

    # ==========================================================================
    # At this point we want to calculate the data to be signed. This is
    # done by concatenating data to be signed, the signature _UP_TO_THIS_POINT_
    # (excludes any unhashed data and stuff) and a trailer

    if isinstance(input, str):
      hasher.update(str.encode('utf-8'))
    elif isinstance(input, bytes):
      hasher.update(input)
    elif isinstance(input, BufferedReader):
      while chunk := input.read(65536):
        hasher.update(chunk)
    else:
      raise AssertionError('Wrong type for input')

    # Add the signature payload, from version to hashed subpackets
    hasher.update(payload)

    # Now we add the "trailer": 0x04 (version) 0xff ("stuff") and signature length
    hasher.update(b'\x04\xff')
    hasher.update(len(payload).to_bytes(4, 'big'))

    # And then we create a nice hash of our signature data
    digest = hasher.digest()

    # Call the KMS to sign our digest
    signature = self.__sign_kms(digest, hash_length, kms_client = kms_client)

    # ==========================================================================
    # Now that we have the signature_body and signature hash, we can continue
    # preparing the payload of our signature packet...

    unhashed_subpackets = __subpacket(SUBPACKET_ISSUER, self.__pgp_key_id)
    unhashed_subpackets_length = len(unhashed_subpackets)

    payload += unhashed_subpackets_length.to_bytes(2, 'big')
    payload += unhashed_subpackets

    payload += digest[:2] # hashed value prefix
    payload += __mpi(signature, self.bits)

    # ==========================================================================
    # Finally, we prepare our message, and decide whether to armour it or not

    message = __packet(PGP_SIGNATURE_TAG, payload)

    return armour('SIGNATURE', message) if armoured else message



  def message(self, input, output=None, hash='sha256', kms_client=None):
    """
    Sign the specified TEXT input using this key, writing the signed message
    AND signature to the output specified.

    Parameters:
    -----------

    input (str, bytes or TextIOWrapper):
      The text message to be signed.

    output (None or BufferedWrite):
      The output for the message AND signature or "None" to have them returned
      as a string.

    hash (str):
      The hashing algorithm used to sign the data.

    kms_client:
      A BotoCore "KMS" client, if "None" this will be initialized as:
        | session = botocore.session.get_session()
        | kms_client = session.create_client('kms')

    Returns:
    --------

    If output was "None", a string containing the GnuPG / OpenPGP formatted
    message and signature.
    """

    (hash_algorithm, hash_length, hasher) = \
      (b'\x08', 256, hashlib.sha256()) if hash == 'sha256' else \
      (b'\x09', 384, hashlib.sha384()) if hash == 'sha384' else \
      (b'\x0a', 512, hashlib.sha512()) if hash == 'sha512' else \
      (None, None)

    assert hash_algorithm, 'Wrong hash algorithm %s for signature' % (hash)

    # If "output" was None, we want to buffer the output and return a string...
    (return_string, output) = (True, BytesIO()) if output == None else (False, output)

    # Start preparing the signature
    payload =  SIGNATURE_VERSION
    payload += SIGNATURE_TYPE_CANONICAL_TEXT
    payload += KEY_ALGORITHM_RSA
    payload += hash_algorithm

    # Those are all our hashed subpackets (only fingerprint and time).
    hashed_subpackets =  __subpacket(SUBPACKET_ISSUER_FINGERPRINT, b'\x04' + self.__pgp_fingerprint)
    hashed_subpackets += __subpacket(SUBPACKET_SIGNATURE_CREATION_TIME, int(time()).to_bytes(4, 'big'))
    hashed_subpackets_length = len(hashed_subpackets)

    payload += hashed_subpackets_length.to_bytes(2, 'big')
    payload += hashed_subpackets

    # ==========================================================================
    # At this point we want to calculate the data to be signed. This is
    # done by concatenating data to be signed, the signature _UP_TO_THIS_POINT_
    # (excludes any unhashed data and stuff) and a trailer

    # Line separator, as a UTF-8 string
    eol = linesep.encode('utf-8')

    # Encode a line in UTF-8 and write it to the output, followed by the
    # OS-dependent newline character...
    def __write_encoded(line):
      # RFC4880, section 7.1: Dash-Escaped Text
      if line.startswith('-'):
        line = '- ' + line
      line = line.rstrip('\t ')

      # Now we have a somewhat proper string
      encoded = line.encode('utf-8')
      output.write(encoded)
      output.write(eol)
      return encoded

    # Write a line to the output _and_ update the hasher with its contents
    def __add_line(line):
      encoded = __write_encoded(line)
      hasher.update(encoded)
      hasher.update(b'\r\n')

    # Message preamble
    output.write('-----BEGIN PGP SIGNED MESSAGE-----'.encode('utf-8') + eol)
    output.write(('Hash: SHA%s' % (hash_length)).encode('utf-8') + eol)
    output.write(eol)

    # Process lines, depending on input type
    if isinstance(input, str):
      lines = input.splitlines()
      for line in lines:
        __add_line(line)

    elif isinstance(input, bytes):
      lines = input.decode('utf-8').splitlines()
      for line in lines:
        __add_line(line)

    elif isinstance(input, TextIOWrapper):
      for lines in input:
        for line in lines.splitlines():
          __add_line(line)

    else:
      raise AssertionError('Wrong type for input')

    output.write(eol)

    # Add the signature payload, from version to hashed subpackets
    hasher.update(payload)

    # Now we add the "trailer": 0x04 (version) 0xff ("stuff") and signature length
    hasher.update(b'\x04\xff')
    hasher.update(len(payload).to_bytes(4, 'big'))

    # And then we create a nice hash of our signature data
    digest = hasher.digest()

    # Call the KMS to sign our digest
    signature = self.__sign_kms(digest, hash_length, kms_client = kms_client)

    # ==========================================================================
    # Now that we have the signature_body and signature hash, we can continue
    # preparing the payload of our signature packet...

    unhashed_subpackets = __subpacket(SUBPACKET_ISSUER, self.__pgp_key_id)
    unhashed_subpackets_length = len(unhashed_subpackets)

    payload += unhashed_subpackets_length.to_bytes(2, 'big')
    payload += unhashed_subpackets

    payload += digest[:2] # hashed value prefix
    payload += __mpi(signature, self.bits)

    # ==========================================================================
    # Finally, we prepare our message, and emit the armoured signature. Then
    # if we need to return a string, we convert it from UTF-8

    message = __packet(PGP_SIGNATURE_TAG, payload)

    output.write(armour('SIGNATURE', message))

    if (return_string):
      return output.getvalue().decode('utf-8').strip()



# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def _KmsPgpKey__packet(tag: int, payload: bytes) -> bytes:
  bytes = len(payload)
  bits = bytes.bit_length()

  type = 0 if bits <= 8 else \
         1 if bits <= 16 else \
         2 if bits <= 32 else \
         None

  assert type is not None, 'Length %s too big for packet' % (bytes)

  length = \
    bytes.to_bytes(1, 'big') if type == 0 else \
    bytes.to_bytes(2, 'big') if type == 1 else \
    bytes.to_bytes(4, 'big') if type == 2 else \
    None # Will never happen!

  header = 0b10000000 | (tag << 2) | type
  header = header.to_bytes(1, 'big')

  return header + length + payload

# ==============================================================================

def _KmsPgpKey__subpacket(type, value):
  payload = type + value

  length = len(payload)
  assert length < 192, 'Length %s too big for subpacket' % (length)

  return length.to_bytes(1, 'big') + payload

# ==============================================================================

def _KmsPgpKey__mpi(number, bits = 0):
  bits = max(number.bit_length(), bits)
  bytes = number.to_bytes(bits // 8 + (bits % 8 and 1 or 0), 'big')
  length = bits.to_bytes(2, 'big')
  return length + bytes
