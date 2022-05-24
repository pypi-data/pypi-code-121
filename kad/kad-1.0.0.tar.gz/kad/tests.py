#!/usr/bin/env python3

import kad

dictionary = {'a': 5, 'b': True}

kad_object = kad.to_kad(dictionary)
assert(kad_object.b)
assert(kad_object.a == 5)
print("All tests pass.")
