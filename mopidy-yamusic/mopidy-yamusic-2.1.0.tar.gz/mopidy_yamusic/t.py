b=bytes("1234567890",'utf-8')
print(b)

range="bytes=1-"
range_start = None
range_end = None
if range != None:
  if range.split('=')[0] == 'bytes':
              startend = range.split('=')[1].split('-')
              range_start = startend[0]
              range_end = startend[1]
              if range_start != "":
                range_start = int(range_start)
              else:
                range_start = None
              if range_end != "":
                range_end = int(range_end)
              else:
                range_end = None
  print(range_start)
  print(range_end)
  print(b[range_start:range_end])
