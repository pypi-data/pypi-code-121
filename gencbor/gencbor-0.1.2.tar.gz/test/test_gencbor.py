#!/usr/bin/python3

import gencbor
import json
import base64
import os.path
import sys


def run_py_tests():
    if gencbor.null == (22,):
        raise Exception("gencbor.null == (22,)")

    m = {gencbor.Tag(1, 2): 1, (1, 2): 2}
    if len(m) != 2:
        raise Exception("len(m) != 2")

    if hash(gencbor.true) == hash(gencbor.false):
        raise Exception("hash(gencbor.true) == hash(gencbor.false)")


def to_json(value):
    if isinstance(value, gencbor.Tag):
        # TODO: Proper bigint decoding?
        if value.number == 2 and \
                value.content == b'\x01\x00\x00\x00\x00\x00\x00\x00\x00':
            return 2 ** 64
        if value.number == 3 and \
                value.content == b'\x01\x00\x00\x00\x00\x00\x00\x00\x00':
            return - 1 - 2 ** 64
        return gencbor.Tag(value.number, to_json(value.content))
    elif isinstance(value, list) or isinstance(value, tuple):
        return list([to_json(v) for v in value])
    elif isinstance(value, dict) or isinstance(value, gencbor.Map):
        return {to_json(key): to_json(value[key]) for key in value}
    else:
        return value


def main():
    with open(os.path.dirname(__file__) + '/appendix_a.json') as file:
        tests = json.load(file)
    with open(os.path.dirname(__file__) + '/fail.json') as file:
        tests_fail = json.load(file)
    failures = 0
    for test in tests:
        # print(test)
        cbor = base64.b64decode(test['cbor'])
        cbor2 = base64.b16decode(test['hex'].upper())
        if cbor != cbor2:
            raise Exception('cbor != cbor2')
        actual = gencbor.decode(cbor)
        actual_conv = to_json(actual)
        if 'decoded' in test:
            expected = test['decoded']
            if expected != actual_conv:
                print('Expected {}, got {}'.format(expected, actual_conv))
                failures += 1
        else:
            # print(actual)
            pass
        roundtrip = test['roundtrip']
        reencoded = gencbor.encode(actual)
        if cbor == reencoded and roundtrip:
            # print(cbor)
            pass
        if cbor != reencoded:
            if roundtrip:
                print('Expected {}, got {}'.format(cbor, reencoded))
                failures += 1

    for test in tests_fail:
        # print(test)
        cbor = base64.b16decode(test['hex'].upper())
        try:
            actual = gencbor.decode(cbor)
        except gencbor.NotWellFormedError:
            continue
        except gencbor.NotBasicValidError:
            continue
        except gencbor.GotDataAfterEndError:
            continue
        print('Unexpected success for {}'.format(cbor))
        failures += 1

    try:
        run_py_tests()
    except Exception as e:
        print('Test failed: {}'.format(e))
        failures += 1

    if failures != 0:
        print('Got failures')
        sys.exit(1)


if __name__ == '__main__':
    main()
