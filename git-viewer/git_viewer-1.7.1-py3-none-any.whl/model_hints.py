#!/usr/bin/env python3

import math

def generate_keys(alphabet, num_keys):
	if num_keys == 0:
		return

	a,b, len_keys = calc_key_length(alphabet, num_keys)

	if len_keys > 1:
		keys = alphabet
		for i in range(len_keys - 2):
			keys = (key+c for key in keys for c in alphabet)
	else:
		assert a == 0
		keys = [""]
	
	
	keys = iter(keys)

	for i in range(a):
		yield next(keys)
	
	i = 0
	while True:
		key_start = next(keys)
		for c in alphabet:
			yield key_start + c
			i += 1
			if i >= b:
				return

def calc_key_length(alphabet, num_keys):
	len_alphabet = len(alphabet)
	len_key = math.ceil(math.log(num_keys, len_alphabet))
	a = math.floor((len_alphabet**len_key - num_keys) / (len_alphabet - 1))
	b = num_keys - a

	return a,b, len_key


if __name__ == '__main__':
	alph = "fg"
	n = 5
	#a,b, len_key = calc_key_length(alph, n)
	#print(f"{a}+{b}, {len_key}")
	out = list(generate_keys(alph, n))
	assert len(out) == n
	assert len(set(out)) == n
	for k in out:
		print(k)
