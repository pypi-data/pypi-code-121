from kavyanarthaki.text import ml
from kavyanarthaki.db import data
from kavyanarthaki.vritham import predict, _compute

def gl(text):
    if isinstance(text, ml):text = text.text
    return ml(text).laghuguru()

def syllables(text):
    if isinstance(text, ml):text = text.text
    return ml(text).syllables()
 
def compute(akshara_pattern): # calculate maathra input NJYSBMTRGL string/list
    return _compute(akshara_pattern)
 
def convertgl(text): # get NJYSBMTRGL from GL string
    if isinstance(text, list):
        try:text=''.join(text)
        except:return -1
    if isinstance(text, tuple):
        try:text=''.join(list(text))
        except:return -1
    triplets = {'LLL':'N','LLG':'S','LGL':'J','LGG':'Y','GLL':'B','GLG':'R','GGL':'T','GGG':'M'}
    output = ''
    for i in range(0,len(text),3):
        if len(text[i:i+3]) == 3:output += triplets.get(text[i:i+3].upper(),'')
        else:output += text[i:i+3].upper()
    return output

def gettriplet(character): # get GL triplet from any single NJYSBMTRGL character
    valid = ['N','S','J','Y','B','R','T','M']
    if character.upper() not in valid:return character.upper()
    else:return str('{0:03b}'.format(valid.index(character.upper()))).replace('0','L').replace('1','G')

def converttogl(string): # get GL text from NJYSBMTRGL string
    if isinstance(string, list):
        try:string=''.join(string)
        except:return -1
    if isinstance(string, tuple):
        try:string=''.join(list(string))
        except:return -1
    output = ''
    for character in string:
        output+=gettriplet(character)
    return output

def check(sequence): # check NJYSBMTRGL string in sanskrit database
    db = data()
    db.load()
    return db.check(sequence)

def sanskritvritham(text): # check poem text GL in sanskrit database
    output = check(convertgl(gl(text)))
    if isinstance(output,list):return "വൃത്ത പ്രവചനം: "+output[0]+" (ലക്ഷണം: "+output[1]+", "+output[2]+")"
    else:return "വൃത്ത പ്രവചനം: കണ്ടെത്താനായില്ല "+" (ലക്ഷണം: കണ്ടെത്താനായില്ല, -)"

def bhashavritham(*lines): # check poem lines in bhasha vritham
    return predict().bhashavritham(lines)
    
