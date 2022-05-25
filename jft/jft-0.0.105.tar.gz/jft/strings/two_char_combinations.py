from itertools import combinations_with_replacement as cwr
from string import ascii_letters, digits, punctuation
_ch = ascii_letters + digits + punctuation + ' '

f = lambda ch=_ch: [''.join(c) for n in range(2, 0, -1) for c in cwr(ch, n)]

def t():
  z = f()
  return all([z[0] == 'aa', z[1000]=='lv', z[-1] == ' '])

if __name__ == '__main__': print(t())