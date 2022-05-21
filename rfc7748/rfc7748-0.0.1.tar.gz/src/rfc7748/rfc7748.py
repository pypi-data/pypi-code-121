def ec_multscalar(prime, element, bits, k, u):
    p = prime
    a24 = (element - 2) // 4
    x_1 = u
    x_2 = 1
    z_2 = 0
    x_3 = u
    z_3 = 1
    swap = 0

    def plus(a, b):
        return (a + b) % p

    def minus(a, b):
        return (a - b) % p

    def multiply(a, b):
        return (a * b) % p

    def power2(a):
        return pow(a, 2, p)

    def cswap(a, b):
        dummy = swap * minus(a, b)
        return minus(a, dummy), plus(b, dummy)

    for t in reversed(range(bits)):
        k_t = (k >> t) & 1
        swap ^= k_t
        x_2, x_3 = cswap(x_2, x_3)
        z_2, z_3 = cswap(z_2, z_3)
        swap = k_t

        A = plus(x_2, z_2)
        AA = power2(A)
        B = minus(x_2, z_2)
        BB = power2(B)
        E = minus(AA, BB)
        C = plus(x_3, z_3)
        D = minus(x_3, z_3)
        DA = multiply(D, A)
        CB = multiply(C, B)

        x_3 = power2(plus(DA, CB))
        z_3 = multiply(x_1, power2(minus(DA, CB)))
        x_2 = multiply(AA, BB)
        z_2 = multiply(E, plus(AA, multiply(a24, E)))

    x_2, x_3 = cswap(x_2, x_3)
    z_2, z_3 = cswap(z_2, z_3)

    return multiply(x_2, pow(z_2, p - 2, p))


class ecdh:
    'Elliptic-curve Diffie-Hellman'

    IS_PY2 = ('a' == b'a')

    @classmethod
    def bytes2number(cls, b):
        if cls.IS_PY2 and not isinstance(b, bytearray):
            b = bytearray(b)
        assert len(b) == cls.LEN
        return sum([b[i] << 8*i for i in range(cls.LEN)])

    @classmethod
    def number2bytes(cls, n):
        ret_type = bytearray if cls.IS_PY2 else bytes
        return ret_type([n >> 8*i & 0xFF for i in range(cls.LEN)])

    @classmethod
    def clamp_helper(cls, n):
        n = bytearray(n)
        cls.clamp(n)
        return n

    @classmethod
    def scalar_mult(cls, n, p):
        n = cls.clamp_helper(n)
        n = cls.bytes2number(n)
        if not isinstance(p, int):
            p = cls.bytes2number(p)

        result = ec_multscalar(
            cls.PRIME, cls.ELEMENT, cls.LEN * 8, n, p)
        return cls.number2bytes(result)

    @classmethod
    def scalar_base_mult(cls, n):
        return cls.scalar_mult(n, cls.BASE_POINT)


class x25519(ecdh):
    PRIME = 2**255 - 19
    ELEMENT = 486662
    BASE_POINT = 9
    LEN = 32

    @staticmethod
    def clamp(n):
        n[0] &= 248
        n[31] &= 127
        n[31] |= 64


class x448(ecdh):
    PRIME = 2**448 - 2**224 - 1
    ELEMENT = 156326
    BASE_POINT = 5
    LEN = 56

    @staticmethod
    def clamp(n):
        n[0] &= 252
        n[55] |= 128


def test_dh(
        ecdh,
        a_private_key,
        a_public_key,
        b_private_key,
        b_public_key,
        shared_key
    ):
    from binascii import hexlify, unhexlify

    a_private = unhexlify(a_private_key)
    b_private = unhexlify(b_private_key)

    a_public = ecdh.scalar_base_mult(a_private)
    b_public = ecdh.scalar_base_mult(b_private)
    a_shared = ecdh.scalar_mult(a_private, b_public)
    b_shared = ecdh.scalar_mult(b_private, a_public)

    assert a_public == unhexlify(a_public_key)
    assert b_public == unhexlify(b_public_key)
    assert a_shared == unhexlify(shared_key)
    assert a_shared == b_shared
    print(hexlify(a_shared))


def test():
    '''
    These test data comes from:
        https://www.rfc-editor.org/rfc/rfc7748.html#section-6
    '''

    test_dh(
        x25519,
        '77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a',
        '8520f0098930a754748b7ddcb43ef75a0dbf3a0d26381af4eba4a98eaa9b4e6a',
        '5dab087e624a8a4b79e17f8b83800ee66f3bb1292618b6fd1c2f8b27ff88e0eb',
        'de9edb7d7b7dc1b4d35b61c2ece435373f8343c85b78674dadfc7e146f882b4f',
        '4a5d9d5ba4ce2de1728e3bf480350f25e07e21c947d19e3376f09b3c1e161742'
    )

    test_dh(
        x448,
        '9a8f4925d1519f5775cf46b04b5800d4ee9ee8bae8bc5565d498c28d'
        'd9c9baf574a9419744897391006382a6f127ab1d9ac2d8c0a598726b',
        '9b08f7cc31b7e3e67d22d5aea121074a273bd2b83de09c63faa73d2c'
        '22c5d9bbc836647241d953d40c5b12da88120d53177f80e532c41fa0',
        '1c306a7ac2a0e2e0990b294470cba339e6453772b075811d8fad0d1d'
        '6927c120bb5ee8972b0d3e21374c9c921b09d1b0366f10b65173992d',
        '3eb7a829b0cd20f5bcfc0b599b6feccf6da4627107bdb0d4f345b430'
        '27d8b972fc3e34fb4232a13ca706dcb57aec3dae07bdc1c67bf33609',
        '07fff4181ac6cc95ec1c16a94a0f74d12da232ce40a77552281d282b'
        'b60c0b56fd2464c335543936521c24403085d59a449a5037514a879d',
    )


if __name__ == '__main__':
    test()
