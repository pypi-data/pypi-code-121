#!/usr/bin/python3
from kavyanarthaki.text import ml

def _compute(akshara_pattern): # calculate maathra input NJYSBMTRGL string/list
    if isinstance(akshara_pattern, list):
        try:akshara_pattern=''.join(akshara_pattern)
        except:return -1
    akshara_pattern=akshara_pattern.upper()
    Maathra_table = {'N':3,'J':4,'Y':5,'S':4,'B':4,'M':6,'T':5,'R':5,'G':2,'L':1}
    maathra = 0
    for akshara in akshara_pattern:
        maathra += Maathra_table.get(akshara,0)
    return maathra

class predict:
    def __init__(self):
        pass        

    def bhashavritham(self, lines):
        def average(lines):
            odd_lines = [];even_lines = [];_l1=[];_l2=[];_m1=[];_m2=[]
            for index, line in enumerate(lines):
                if isinstance(line, ml):line = line.text
                if (index%2==0):odd_lines.append(ml(" ".join([str(ml(i).nochillu()) for i in line.split()])))
                else:even_lines.append(ml(" ".join([str(ml(i).nochillu()) for i in line.split()])))
            for line in odd_lines:
                _l1.append(len(line))
                _m1.append(_compute(line.laghuguru()))
            for line in even_lines:
                _l2.append(len(line))
                _m2.append(_compute(line.laghuguru()))
            l1,l2,m1,m2 = (0,0,0,0)
            if len(odd_lines)>0:
                l1 = (sum(_l1)/len(_l1))
                m1 = (sum(_m1)/len(_m1))
            if len(even_lines)>0:
                l2 = (sum(_l2)/len(_l2))
                m2 = (sum(_m2)/len(_m2))
            if l2 == 0:l2 = l1
            if m2 == 0:m2 = m1
            return (l1,l2,m1,m2)
        def inRange(value, lowerlimit, upperlimit):
            if value>=lowerlimit and value<=upperlimit:return True
            return False
        l1, l2, m1, m2 = average(lines)
        prediction = ''
        if(((inRange(l1,8,12)) and (m1==11 or m1==12)) and ((inRange(l2,8,12)) and (m2== 11 or m2==12))):prediction="മുമ്മാത്ര"
        if(((l1==12) and (inRange(m1,15,17))) and ((l2==12) and (inRange(m2,15,17)))):prediction="അന്നനട"
        if(((l1==16) and (m1==23 or m1==24)) and ((l2==16) and (m2==23 or m2==24))):prediction="ഭാഷാ പഞ്ചചാമരം"
        if(((inRange(l1,8,16)) and (m1==15 or m1==16)) and ((inRange(l2,8,17)) and (m2==15 or m2==16))):prediction="തരംഗിണി"
        if(((l1==16) and (m1<=32)) and ((l2==13) and (m2<=26))):prediction="നതോന്നത"
        if(((l1==12) and (m1==19 or m1==20)) and ((l2==12) and (m2==19 or m2==20))):prediction="കാകളി"
        if(((l1==14) and (m1<=20)) and ((l2==14) and (m2<=20))):prediction="മണികാഞ്ചി"
        if(((l1==16) and (m1<=20)) and ((l2==16) and (m2<=20))):prediction="കളകാഞ്ചി"
        if(((l1==12) and (m1<20)) and ((l2==8) and (m2==14 or m2==13))):prediction="മരകാകളി"
        if(((l1==11) and (m1<=18)) and ((l2==11) and (m2<=18))):prediction="പാന"
        if(((l1==12) and (m1<=18)) and ((l2==10) and (m2==16 or m2==17))):prediction="മഞ്ജരി"
        if((l1==10) and (l2==8)): prediction="താരാട്ടു/ഓമനക്കുട്ടൻ"
        if((l1==14) and (l2==14)): prediction="കേക"
        if((l1==12) and (l2==10)): prediction="മതിലേഖ"
        if((l1==10) and (l2==10)): prediction="മാവേലി"
        return "വൃത്ത പ്രവചനം: "+prediction
    
