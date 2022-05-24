import os
import sys

from botocore import session as aws
from getopt import getopt, GetoptError
from inspect import cleandoc

from .pgpkms import KmsPgpKey

def __help():
  cmd = os.getenv('PGP_KMS_ARGV0', sys.argv[0])
  cmd = 'python3 -m pgpkms' if cmd == __file__ else cmd

  sys.exit(cleandoc('''\
    Usage: {cmd} <command> [options]

    Commands:
      export     Export the public key in a PGP-compatible format.
      sign       Sing some data and write a detached PGP signature.
      message    Wrap a plaintext in a PGP message and sign it.

    Options:
      -k, --key=<id>         The ID, ARN, or alias of the key to use.
      -o, --output=<file>    Use the specified file as output instead of stdout.
      -i, --input <file>     Use the specified file as input instead of stdin.
      -b,--binary            Do not armour the output (igored for "message").
      --sha[256|384|512]     Use the specified hashing algorithm.

    Environment Variables:
      PGP_KMS_KEY            The default ID, ARN or alias of the key to use.
      PGP_KMS_HASH           The hashing algorithm to use (default tp "sha256").

    Examples

      Export the (unarmoured) public key into the "trusted.gpg" file.
        $ {cmd} export --binary --output trusted.gpg

      Sign the file "myfile.bin" and emit the armoured signature to stdout.
        $ {cmd} sign --input myfile.bin

  '''.format(cmd = cmd)) + os.linesep)

# ==============================================================================

def __export(key, hash, input = None, output = None, armoured = True):
  session = aws.get_session()
  kms_client = session.create_client('kms')

  key = KmsPgpKey(key, kms_client = kms_client)

  pgp_key = key.to_pgp(armoured = armoured, hash = hash, kms_client = kms_client)

  o = open(output, 'wb') if output else sys.stdout.buffer
  o.write(pgp_key)
  o.close()

  sys.exit(0)

# ==============================================================================

def __sign(key, hash, input = None, output = None, armoured = True):
  session = aws.get_session()
  kms_client = session.create_client('kms')

  key = KmsPgpKey(key, kms_client = kms_client)

  i = open(input, 'rb') if input else sys.stdin.buffer

  signature = key.sign(i, armoured = armoured, hash = hash, kms_client = kms_client)

  o = open(output, 'wb') if output else sys.stdout.buffer
  o.write(signature)
  o.close()

  sys.exit(0)

# ==============================================================================

def __message(key, hash, input = None, output = None, armoured = True):
  session = aws.get_session()
  kms_client = session.create_client('kms')

  key = KmsPgpKey(key, kms_client = kms_client)

  i = open(input, 'r') if input else sys.stdin # text reads!
  o = open(output, 'wb') if output else sys.stdout.buffer # write binary!

  signature = key.message(i, o, hash = hash, kms_client = kms_client)

  sys.exit(0)

# ==============================================================================

if __name__ == '__main__':
  if len(sys.argv) < 2:
    __help()

  command = sys.argv[1]

  if not(command in [ 'help', 'export', 'sign', 'message' ]):
    sys.exit('Error: command "%s" unknown' % (command))
  elif command == 'help':
    __help()

  key = os.environ.get('PGP_KMS_KEY')
  hash = os.environ.get('PGP_KMS_HASH', 'sha256')
  input = None
  output = None
  armoured = True

  try:
    (options, rest) = getopt(sys.argv[2:], 'k:o:i:b', [
      'key=', 'output=', 'input=', 'binary',
      'sha256', 'sha384', 'sha512',
    ])

    if len(rest) > 0:
      sys.exit('Error: unknown option "%s"' % (rest[0]))

    for key, value in options:
      if key in [ '-b', '--binary' ]:
        armoured = False
      elif key in [ '-i', '--input' ]:
        input = value
      elif key in [ '-o' , '--output' ]:
        output = value
      elif key in [ '--sha256', '--sha384', '--sha512' ]:
        hash = key[2:]

  except GetoptError as error:
    sys.exit('Error: %s' % (error))

  if key == None:
    sys.exit('Error: no key ID specified')

  if not(hash in [ 'sha256', 'sha384', 'sha512' ]):
    sys.exit('Error: invalid hashing algorithm "%s"' % (hash))

  {
    'export': __export,
    'sign': __sign,
    'message': __message,
  }[command](
    key = key,
    hash = hash,
    input = input,
    output = output,
    armoured = armoured
  )
