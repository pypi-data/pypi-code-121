def fibonach(sequenceLen):
  num = 0
  nextnum = 1
  fibolist = [num,nextnum]
  for i in range(sequenceLen):
    fibolist+=[(num+nextnum)]
    helper = num
    num = nextnum
    nextnum = helper+nextnum
    yield fibolist[len(fibolist)-1]
gen = fibonach(9)
print(next(gen))