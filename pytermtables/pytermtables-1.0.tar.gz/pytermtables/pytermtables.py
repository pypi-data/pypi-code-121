from random import shuffle as listshuffle
from statistics import mean, median, mode, pstdev
import csv

#print a 2d array in grid form
#arr - 2d array to print
#hPadding - the horizontal padding between data and the column lines
#cChar - the character used for corners in the grid - str
#hChar - the character used for horizontal - str
#vChar - the character used for vertical seperations - str
#titleRow - if true - seperator top row from rows beneath (like using a table)
#trChar - the char used for the title row seperator
def printGrid(arr, hPadding:int=1, cChar:str="+", hChar:str= "-", vChar:str="|", titleRow:bool = False, trChar:str = "="):
  #check that variables are usable and of correct format
  if not isinstance(titleRow, bool): raise Exception("titleRow must be either true or false")
  if len(arr) == 0: raise Exception("List cannot be empty")
  if not isinstance(hPadding, int): raise Exception("hPadding must be a positive integer!")
  if hPadding < 0: raise Exception("hPadding must be a positive integer")
  if not isinstance(cChar, str): raise Exception("cChar must be a string!")
  if not isinstance(hChar, str): raise Exception("hChar must be a string!")
  if not isinstance(vChar, str): raise Exception("vChar must be a string!")
  if not isinstance(trChar, str): raise Exception("trChar must be a string!")
  if len(cChar) != 1: raise Exception("cChar must be a string of length 1")
  if len(hChar) != 1: raise Exception("hChar must be a string of length 1")
  if len(vChar) != 1: raise Exception("vChar must be a string of length 1") 
  if len(trChar) != 1: raise Exception("trChar must be a string of length 1") 
  
  #find grid cols and rows
  gridCols = len(max(arr, key=lambda x: len(x))) # <- as wide as longest sublist
  
  #iterate through data, find widest element for each column
  #this + hPadding*2 will be the width of the entire column
  columnWidths = []
  for i in range(gridCols):
    column = ([el[i] for el in arr if i < len(el)]) #get column

    #get max width of element in each column
    maxColumnElemWidth = len(str(max(column, key=lambda x: len(str(x)))))
    columnWidths.append(maxColumnElemWidth) #append to list by column index

  #if using a title row, define it
  if titleRow:
    titleSeperator = "\n"
    for width in columnWidths:
      titleSeperator += cChar + trChar * (width+hPadding * 2)
    titleSeperator += cChar

  #construct grid seperator with grid widths found
  gridSeperator = "\n"
  for width in columnWidths:
    gridSeperator += cChar + hChar * (width+hPadding * 2)
  gridSeperator += cChar

  #print grid with new column widths
  for row, i in enumerate(arr):
    if row == 1 and titleRow:
      print(titleSeperator)
    else:
      print(gridSeperator)
    for col in range(gridCols):
      colWidth = columnWidths[col] + hPadding * 2
      try:
        elem = arr[row][col]
        elem = str(elem).center(colWidth, " ")
      except IndexError:
        elem = " " * colWidth
      print(vChar + str(elem), end="")
    print(vChar, end="")
  print(gridSeperator)

#table class
#headers - the headers for each table section
#rows - optional - add rows from intialisation
class Table():
  def __init__(self, headers:list, rows=None):
    if not isinstance(headers, list): raise Exception("Headers must be a list!")
    if len(headers) == 0: raise Exception("Headers list cannot be empty")
    if len(set(headers)) != len(headers): raise Exception("Headers must not contain duplicates!")
    self.headers = headers

    #if rows supplied, add to begin with else make it blank
    self.rows = []
    if rows != None:
      self.rows = [self.addRow(row) for row in rows]
    
  #creating a row for table
  #row - the data for the row
  #returns the copy of thre created row
  def addRow(self, row:dict) -> dict:
    if not isinstance(row, dict): raise Exception("Row must be a dictionary")
    
    newRow = dict.fromkeys((h for h in self.headers), None) # <- create blank header dict
    for key, value in row.items():
      if key in self.headers:
        newRow[key] = value
      else:
        raise Exception(f"{key} is not an existing header!")
    self.rows.append(newRow)
    return newRow

  #pretty print the table
  def prettyPrint(self):
    grid = [self.headers] + [[row[header] for header in self.headers] for row in self.rows]
    printGrid(grid, titleRow=True)

  #find every row that contains subdict
  #dict - the subdict to check if is contained
  def getRows(self, subdict:dict) -> list:
    if not isinstance(subdict, dict): raise Exception("Subdict must be a dictionary!")
    return [row for row in self.rows if subdict.items() <= row.items()]

  #remove every row that contains subdict
  #subdict - the subdict to check if is contained
  def removeRows(self, subdict:dict):
    if not isinstance(subdict, dict): raise Exception("Subdict must be a dictionary!")
    self.rows = [row for row in self.rows if not subdict.items() <= row.items()]

  #sort rows by value
  #header - the key of the dictionary used to sort by
  #descending - whether it should be sorted in ascending or descending order
  def sort(self, header, descending:bool=False):
    if not isinstance(descending, bool): raise Exception("Descending must be a boolean!")
    self.rows = sorted(self.rows, key=lambda d: d[header], reverse=descending)

  #shuffle rows in a random order
  def shuffle(self):
    listshuffle(self.rows) #listshuffle is alias of shuffle from random library

  #get all data from a header
  #header - title of header to use
  #excludeNone - whether to exlucde None values when getting data
  def getHeader(self, header, excludeNone=False) -> list:
    if not isinstance(excludeNone, bool): raise Exception("excludeNone must be a boolean!")
    if not header in self.headers: raise Exception(f"{header} is not a header for this table!")
    #return column from specified header
    if excludeNone:
      return [row[header] for row in self.rows if row != None]
    else:
      return [row[header] for row in self.rows]

  #remove a column by a header name
  def removeHeader(self, headerName):
    if not headerName in self.headers: raise Exception(f"Can't delete header {headerName} as it already exists!")
    self.headers.remove(headerName)
    for row in self.rows:
      del row[headerName]

  #add a new header column
  def addHeader(self, headerName):
    if headerName in self.headers: raise Exception(f"Cant create header {headerName} as it already exists")#
    self.headers.append(headerName)
    for row in self.rows:
      row[headerName] = None
    
  #mean of a header's data
  def getMean(self, header) -> float:
    return mean(self.getHeader(header, excludeNone=True))    
  
  #median of a header's data
  def getMedian(self, header) -> float:
    return median(self.getHeader(header, excludeNone=True))

  #mode of a header's data
  def getMode(self, header) -> float:
    return mode(self.getHeader(header, excludeNone=True))

  #range of a header's data
  def getRange(self, header) -> float:
    data = self.getHeader(header, excludeNone=True)
    return max(data) - min(data)

  #standard deviation of a header's data
  def getStdDev(self, header) -> float:
    return pstdev(self.getHeader(header, excludeNone=True))

#create a table from a csv file
#filePath - path of file
#titleRow - whether CSV contains a row with headers
#deliminter - the char used for seperations
#quotechar - the char used for quotes
def tableFromCSV(filePath:str, titleRow:bool=True, delimiter:str=",", quotechar:str='"'):
  #type checking
  if not isinstance(filePath, str): raise Exception("filePath must be a string!")
  if not isinstance(delimiter, str): raise Exception("delimiter must be a string!")
  if not isinstance(quotechar, str): raise Exception("quotechar must be a string!")
  if not isinstance(titleRow, bool): raise Exception("titleRow must be a boolean!")

  #length of delimter and quotechar checking
  if not len(delimiter) == 1: raise Exception("delimiter must be a single char!")
  if not len(quotechar) == 1: raise Exception("quotechar must be a single char!")
  
  #read csv file
  with open(filePath, newline='', mode="r") as csvfile:
    #read csv
    p = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar, skipinitialspace=True, dialect="excel")
    rows = list(p)
    longestRow = max(rows, key=len)
    
    #set header titles
    start = 0
    if titleRow:
      table = Table(headers=rows[0])
      start = 1
    else:
      table = Table(headers=[x for x in range(1, len(longestRow)+1)])

    #add rows
    for i in range(start,len(rows)):
      row = rows[i]
      rowToAdd = {}
      for count, elem in enumerate(row):
        if elem == "":
          elem = None
        rowToAdd[table.headers[count]] = elem
      table.addRow(rowToAdd)
  return table

#filePath - path of file
#titleRow - whether CSV contains a row with headers
#deliminter - the char used for seperations
#quotechar - the char used for quotes
def tableToCSV(filePath:str, table:Table, titleRow:bool = True, delimiter:str=",", quotechar:str='"'):
  #type checking
  if not isinstance(filePath, str): raise Exception("filePath must be a string!")
  if not isinstance(delimiter, str): raise Exception("delimiter must be a string!")
  if not isinstance(quotechar, str): raise Exception("quotechar must be a string!")
  if not isinstance(titleRow, bool): raise Exception("titleRow must be a boolean!")

  #length of delimter and quotechar checking
  if not len(delimiter) == 1: raise Exception("delimiter must be a single char!")
  if not len(quotechar) == 1: raise Exception("quotechar must be a single char!")
    
  #write csv
  with open(filePath, 'w+', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=delimiter, quotechar=quotechar, quoting=csv.QUOTE_MINIMAL)

    if titleRow:
      writer.writerow(table.headers)

    #iterate through rows and write
    for row in table.rows:
      elems = [row[header] for header in table.headers]
      writer.writerow(elems)