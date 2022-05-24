from base64 import standard_b64encode
from os import linesep
from textwrap import wrap

__CRC24_INIT = 0x0b704ce
__CRC24_POLY = 0x1864cfb

def __crc24(data: bytes) -> bytes:
    crc = __CRC24_INIT

    for b in data:
      crc ^= b << 16

      for i in range(8):
        crc <<= 1
        if crc & 0x1000000:
          crc ^= __CRC24_POLY

    crc = crc & 0xFFFFFF
    return crc.to_bytes(3, 'big')

def armour(header: str, payload: bytes) -> str:
  encoded = standard_b64encode(payload)
  wrapped = wrap(encoded.decode('utf-8'), 64)

  checksum = standard_b64encode(__crc24(payload)).decode('utf-8')

  wrapped.insert(0, '-----BEGIN PGP %s-----' % (header))
  wrapped.insert(1, 'Version: PgpKms-AwsWrapper v1')
  wrapped.insert(2, '')
  wrapped.append('=%s' % (checksum))
  wrapped.append('-----END PGP %s-----' % (header))
  wrapped.append('') # final newline!

  return (linesep.join(wrapped)).encode('utf-8')
