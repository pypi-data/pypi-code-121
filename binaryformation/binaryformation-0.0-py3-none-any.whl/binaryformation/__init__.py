def convert_Binary_To_decimal(binary):
  binary = str(binary)
  bdigit = 1
  decimal = 0
  ab=[]
  for numbers in binary:
    ab.append(numbers)

  ab = ab[::-1]

  for numbers in ab:
    numbers = int(numbers)
    decimal = decimal+(numbers*bdigit)
    bdigit = bdigit*2

  print(decimal)

def convert_Decimal_To_binary(a):
   decimal = a
   remainder = 0
   binary = []
   while (True):
     decimal = decimal // 2
     remainder = decimal % 2
     binary.append(remainder)
     if decimal == 0:
       break

   if (a % 2) == 0:
     binary.insert(0, 0)
   else:
     binary.insert(0, 1)

   print(binary[::-1])

