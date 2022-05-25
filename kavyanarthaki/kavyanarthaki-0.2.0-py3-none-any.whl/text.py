#!/usr/bin/python3

class ml:
    def __init__(self, text):
        self.text = text

    def syllables(self):
        sign = [3330, 3331, 3390, 3391, 3392, 3393, 3394, 3395, 3396,
                3398, 3399, 3400, 3402, 3403, 3404, 3405, 3415]
        output = [];connected = False;word_len = len(self.text)
        for index in range(word_len):
            if ord(self.text[index])<3330 or ord(self.text[index])>3455:connected = False;continue
            if not connected:output.append(self.text[index])
            else:output[-1] += self.text[index]
            if index+1 >= word_len:continue
            elif ord(self.text[index+1]) in sign:connected = True
            elif ord(self.text[index]) in [3405]:
                nonsigncharacters = ""
                for character in output[-1]:
                    if ord(character) not in sign:nonsigncharacters = nonsigncharacters + character
                if output[-1].count(chr(3405))<2:connected = True
                elif (ord(self.text[index+1]) in [i for i in range(3375,3386)]):
                    if len(nonsigncharacters)<3:connected = True
                    else:connected = False
                else:
                    connected = False
                    for character in nonsigncharacters:
                        if (ord(character) in [i for i in range(3375,3386)]):
                            connected = True
                            break
            elif ord(self.text[index]) in [3451]:connected = True if ord(self.text[index+1])==3377 else False
            else:connected = False
        return output

    def laghuguru(self):
        def nonsignchars(syllable):
            signs = (3330, 3331, 3390, 3391, 3392, 3393, 3394, 3395, 3396,3398, 3399, 3400, 3402, 3403, 3404, 3405, 3415)
            output = [s for s in syllable if ord(s) not in signs]
            return ''.join(output)
        syllables = self.syllables()
        output = ['L' for syllable in syllables]
        chillu = (3450, 3451, 3452, 3453, 3454)
        g_characters = (3334, 3336, 3338, 3343, 3347, 3348, 3390, 3392, 
                        3394, 3399, 3400, 3403, 3404, 3415, 3330, 3331)
        for index, syllable in enumerate(syllables):
            if ord(syllable[-1]) in chillu:output[index] = '-'
            elif ord(syllable[-1]) in g_characters:output[index] = 'G'
            if len(nonsignchars(syllable))>=2 and index>0:
                if output[index-1]=='-' and index-2>=0:output[index-2]='G'
                elif output[index-1]=='L':output[index-1]='G'
                else:pass
            if ord(syllable[-1])==3405:output[index]='-' # convert character end in chandrakala into -                                                                                 
        if len(output)>1 and output[-1]=='-':output[-2]='G'
        return output

    def nochillu(self):
        lg = self.laghuguru()
        sb = self.syllables()
        output = []
        for index, letter in enumerate(sb):
            if not(lg[index] == '-'):output.append(letter)
        return ml(''.join(output))
    
    def __getitem__(self,index):
        return ml(''.join(self.syllables()[index]))
        
    def __eq__(self,otherobject):
        if isinstance(otherobject, ml):
            if self.text == otherobject.text:return True
        elif isinstance(otherobject,str):
            if self.text == otherobject:return True
        else:return False
                  
    def __mul__(self,num):
        return ml(self.text*num)
                  
    def __rmul__(self,num):
        return ml(self.text*num)
    
    def __add__(self,otherobject):
        if isinstance(otherobject, ml):return ml(self.text + otherobject.text)
        elif isinstance(otherobject,str):return ml(self.text + otherobject)
        else: return ml(self.text)
    
    def __radd__(self,otherobject):
        if isinstance(otherobject,str):return ml(otherobject + self.text)
        else: return ml(self.text)

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text

    def __iter__(self):
        for syllable in self.syllables():
            yield syllable
    def __len__(self):
        return len(self.syllables())
