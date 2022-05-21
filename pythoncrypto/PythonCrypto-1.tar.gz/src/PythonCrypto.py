def Encrypter(a,b):
    bin1 =  ''.join(format(ord(i), '08b') for i in a)
    bin2 =  ''.join(format(ord(i), '08b') for i in b)
    lenx=len(bin2)
    len1=len(bin1)
    len2=len(bin2)
    while len1>len2:
      bin3=bin2*len1
      len2=len(bin3)
    if len1!=len2:
      bin3=bin3[:len1]
      len3=len(bin3)
    c=[str(int(bin1[i])^int(bin3[i])) for i in range(len1)]
    c=''.join(c)
    d=[str(int(c[i])<<2) for i in range(len1)]
    d=''.join(d)
    x2=[str(int(bin2[i])<<2) for i in range(lenx)]
    x2=''.join(x2)
    d5=str(d)+str(x2)
    d6=d5[::-1]
    print('encrypted text is : ',d6)

def Decrypter(a,b):
    bin2 = ''.join(format(ord(i), '08b') for i in b)
    lenc=len(bin2)
    a1=a[::-1]
    x2=[str(int(bin2[i])<<2) for i in range(len(bin2))]
    x2=''.join(x2)
    if (a1.endswith(x2)):
      x3=a1.replace(x2,'')
      len2=len(bin2)
      len1=len(x3)
      while len1>len2:
        bin3=bin2*len1
        len2=len(bin3)
      if len1!=len2:
        bin3=bin3[:len1]
      d=[str(int(x3[i])>>2) for i in range(len(x3))]
      d=''.join(d)
      c=[str(int(d[i])^int(bin3[i])) for i in range(len1)]
      c=''.join(c)
      d=[c[i:i+8] for i in range(0, len(c), 3)]
      d1=' '.join([c[i:i+8] for i in range(0, len(c), 8)])
      binary_values = d1.split()


      ascii_string = ""
      for binary_value in binary_values:
        an_integer = int(binary_value, 2)
        ascii_character = chr(an_integer)



        ascii_string += ascii_character



      print('decrypted text is : ',ascii_string)
    else:
      print('passkey is wrong')


