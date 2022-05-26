import argparse
from termcolor import colored
from utils import utils

# 1. IELTS->CLB level
# CLB Level:	Reading	Writing	Listening	Speaking
clb_ielts_table = [
    [10, 8.0, 7.5, 8.5, 7.5],
    [9, 7.0, 7.0, 8.0, 7.0],
    [8, 6.5, 6.5, 7.5, 6.5],
    [7, 6.0, 6.0, 6.0, 6.0],
    [6, 5.0, 5.5, 5.5, 5.5],
    [5, 4.0, 5.0, 5.0, 5.0],
    [4, 3.5, 4.0, 4.5, 4.0]
]

# 输入CLB值 返回对应的雅思r w l s分数列表
def clb2ielts(clb):
    clb=10 if clb>10 else clb
    if clb<4:
        return [0,0,0,0]
     
    index=10-clb
    return clb_ielts_table[index][1:5]

# 输入一组雅思成绩list：r w l s, 输出一个list对应CLB level： r w l s
def ielts_2_clbs(ielts):
    clb_level = []
    for column in range(1, 5):  # 从读到说，4个列，从1开始，开始找对应的clb级别
        factor = float(ielts[column - 1])  # r w l s每个子项
        for level in range(0, 7):  # 从CLB 级别10一直找到4 7行
            if factor > clb_ielts_table[0][column]:  # 如果语言成绩高于最高分，按照最高分算
                clb_level.append(10) 
                break
            if factor < clb_ielts_table[6][column]:  # 如果低于最低分，则CLB Level =0 跳出本列循环
                clb_level.append(0)
                break
            # 要算每个子项的CLB值
            if clb_ielts_table[level][column] == ielts[column - 1]:
                clb_level.append(clb_ielts_table[level][0])  # 得到该雅思成绩对应的CLB 级别
                break
        # 如果某项分数不在阵列中
        for level in range(1, 7):
            if clb_ielts_table[level][column] < factor < clb_ielts_table[level - 1][column]:
                clb_level.append(clb_ielts_table[level][0])  # 得到该雅思成绩对应的CLB 级别
                break

    return clb_level


# 输入一组雅思成绩list：r w l s, 输出一个CLB level 数字
def ielts_2_clb(ielts):
    clb = 0
    for row in clb_ielts_table:
        if (float(ielts[0]) >= row[1]) & (float(ielts[1]) >= row[2]) & (float(ielts[2]) >= row[3]) & (float(ielts[3]) >= row[4]):
            clb = row[0]
            break
    return clb


# 2 CLPIP和CLB是一一对应关系。
# Canadian English Language Proficiency Index Program (CELPIP) – General Test score equivalency chart
# CLB Level	Reading	Writing	Listening	Speaking
# 10	10	10	10	10
# 9	9	9	9	9
# 8	8	8	8	8
# 7	7	7	7	7
# 6	6	6	6	6
# 5	5	5	5	5
# 4	4	4	4	4

def celpip_2_clb(rwls):
    has_error = False
    for s in rwls:
        if not isinstance(s, int):
            print("the CELPIP must be integer")
            has_error = True
    if not has_error:
        if min(rwls)>10:
            result=10 
        elif min(rwls)<0:
            result=0
        else:
            result=min(rwls)
        return result
    else:
        return 0


def celpip_2_clbs(rwls):
    has_error = False
    for s in rwls:
        if not isinstance(s, int):
            print("the CELPIP must be integer")
            has_error = True
    if not has_error:
        i=0
        for x in rwls:
            if x>10:
                rwls[i]=10
            elif x<0:
                rwls[i]=0
            else:
                rwls[i]=x
            i+=1
        return rwls
    else:
        return []


# 3 TEF
# Test d’évaluation de français pour le Canada (TEF Canada)
# Test score equivalency chart
# CLB Level	Reading	Writing	Listening	Speaking
# 10	    263-277	393-415	316-333	    393-415
# 9	        248-262	371-392	298-315	    371-392
# 8	        233-247	349-370	280-297	    349-370
# 7	        207-232	310-348	249-279	    310-348
# 6	        181-206	271-309	217-248	    271-309
# 5	        151-180	226-270	181-216	    226-270
# 4	        121-150	181-225	145-180	    181-225

tef_clb_table = [
    [10, 263, 277, 393, 415, 316, 333, 393, 415],
    [9, 248, 262, 371, 392, 298, 315, 371, 392],
    [8, 233, 247, 349, 370, 280, 297, 349, 370],
    [7, 207, 232, 310, 348, 249, 279, 310, 348],
    [6, 181, 206, 271, 309, 217, 248, 271, 309],
    [5, 151, 180, 226, 270, 181, 216, 226, 270],
    [4, 121, 150, 181, 225, 145, 180, 181, 225]
]


def tef_2_clb(rwls):
    has_error = False
    for s in rwls:
        if not isinstance(s, int):
            print("the TEF must be integer")
            has_error = True
    if not has_error:

        clb = []
        for column in range(0, 4):  # r w l s
            for row in range(0, 7):
                start = (column + 1) * 2 - 1
                end = (column + 1) * 2
                if rwls[column] in range(tef_clb_table[row][start], tef_clb_table[row][end] + 1):
                    clb.append(tef_clb_table[row][0])
                    break
        return min(clb)
    else:
        return 0

def tef_2_clbs(rwls):
    has_error = False
    for s in rwls:
        if not isinstance(s, int):
            print("the TEF must be integer")
            has_error = True
    if rwls[0] not in range(121,278):
        print('read score is invalid')
        exit(1)
    if rwls[1] not in range(181,416):
        print('write score is invalid')
        exit(1)
    if rwls[2] not in range(145,334):
        print('listen score is invalid')
        exit(1)
    if rwls[3] not in range(181,416):
        print('write score is invalid')
        exit(1)
    
    if not has_error:
        clb = []
        for column in range(0, 4):  # r w l s
            for row in range(0, 7):
                start = (column + 1) * 2 - 1
                end = (column + 1) * 2
                if rwls[column] in range(tef_clb_table[row][start], tef_clb_table[row][end] + 1):
                    clb.append(tef_clb_table[row][0])
                    break
        return clb
    else:
        return 0

# 输入CLB值 返回对应的tef r w l s分数列表
def clb2tef(clb):
    clb=10 if clb>10 else clb
    if clb<4:
        return [0,0,0,0,0,0,0,0]
     
    index=10-clb
    return tef_clb_table[index][1:9]

# 4 TCF
# Test de connaissance du français pour le Canada (TCF Canada)
# Test score equivalency chart
# CLB Level	    Reading	Writing	Listening	Speaking
# 10 and above	549-699	16-20	549-699	16-20
# 9	            524-548	14-15	52        
# 8	            499-523	12-13	503-522	12-13
# 7	            453-498	10-11	458-502	10-11
# 6	            406-452	7-9	    398-457	7-9
# 5	            375-405	6	    369-397	6
# 4	            342-374	4-5	    331-368	4-5

tcf_clb_table = [
    [10, 549, 699, 16, 20, 549, 699, 16, 20],
    [9, 524, 548, 14, 15, 523, 548, 14, 15],
    [8, 499, 523, 12, 13, 503, 522, 12, 13],
    [7, 453, 498, 10, 11, 458, 502, 10, 11],
    [6, 406, 452, 7, 9, 398, 457, 7, 9],
    [5, 375, 405, 6, 6, 369, 397, 6, 6],
    [4, 342, 374, 4, 5, 331, 368, 4, 5]
]


def tcf_2_clb(rwls):        
    has_error=False
    for s in rwls:
        if not isinstance(s, int):
            print("the TCF must be integer")
            has_error = True
    if rwls[0] not in range(342,700):
        print('read score is invalid')
        exit(1)
    if rwls[1] not in range(4,21):
        print('write score is invalid')
        exit(1)
    if rwls[2] not in range(331,700):
        print('listen score is invalid')
        exit(1)
    if rwls[3] not in range(4,21):
        print('write score is invalid')
        exit(1)
    if not has_error:
        clb = []
        for column in range(0, 4):  # r w l s
            for row in range(0, 7):
                start = (column + 1) * 2 - 1
                end = (column + 1) * 2
                if rwls[column] in range(tcf_clb_table[row][start], tcf_clb_table[row][end] + 1):
                    clb.append(tcf_clb_table[row][0])
                    break
        return min(clb)
    else:
        return 0


def tcf_2_clbs(rwls):
    has_error = False
    for s in rwls:
        if not isinstance(s, int):
            print("the TCF must be integer")
            has_error = True
    if not has_error:
        clb = []
        for column in range(0, 4):  # r w l s
            for row in range(0, 7):
                start = (column + 1) * 2 - 1
                end = (column + 1) * 2
                if rwls[column] in range(tcf_clb_table[row][start], tcf_clb_table[row][end] + 1):
                    clb.append(tcf_clb_table[row][0])
                    break
        return clb
    else:
        return 0

# 输入CLB值 返回对应的tcf r w l s分数列表
def clb2tcf(clb):
    clb=10 if clb>10 else clb
    if clb<4:
        return [0,0,0,0,0,0,0,0]
     
    index=10-clb
    return tcf_clb_table[index][1:9]

def getCLBs(rwls, format):
    format=format.upper()
    if format == 'IELTS':
        clb = ielts_2_clb(rwls)
        clbs = ielts_2_clbs(rwls)
    if format == 'CELPIP':
        clb = celpip_2_clb(rwls)
        clbs = celpip_2_clbs(rwls)
    if format == 'TEF':
        clbs = tef_2_clbs(rwls)        
        clb=tef_2_clb(rwls)
    if format == 'TCF':
        clb = tcf_2_clb(rwls)
        clbs = tcf_2_clbs(rwls)
    return clb, clbs


class Language:
    def __init__(self,r,w,l,s,format):
        self.reading = r
        self.writing = w
        self.listening = l
        self.speaking = s
        self.format = format
        self.clb, [self.clb_r, self.clb_w, self.clb_l, self.clb_s] = getCLBs([self.reading, self.writing, self.listening, self.speaking], self.format)

    def get4(self):
        return self.reading,self.writing,self.listening,self.speaking,self.format        


def main():
    parser=argparse.ArgumentParser(description="Language test and CLB converter")
    # Language
    parser.add_argument("-li", "--level2ielts", help="input clb level")
    parser.add_argument("-lc", "--level2celpip", help="input clb level")
    parser.add_argument("-ltef", "--level2tef", help="input clb level")
    parser.add_argument("-ltcf", "--level2tcf", help="input clb level")

    parser.add_argument("-il", "--ielts2level", help="input ielts 4 score(r w s l)",nargs='+')
    parser.add_argument("-cl", "--celpip2level", help="input celpip 4 score(r w s l)",nargs='+')
    parser.add_argument("-tefl", "--tef2level", help="input tef  4 score(r w s l)",nargs='+')
    parser.add_argument("-tcfl", "--tcf2level", help="input tcf 4 score(r w s l)", nargs='+')

    parser.add_argument("-l", "--level", help="input clb level")
    
    args = parser.parse_args()
    no_variables=True

    if args.level2ielts:
        no_variables=False
        clb=int(args.level2ielts)
        items=[]
        if clb!=None:
            print(colored(f'\nCLB {clb} to IELTS:','green'))
            items.append(['Read','Write','Listen','Speak'])
            items.append(clb2ielts(clb))
            utils.printFList2D(items)
        else:
            print('You should input clb level...')
            exit(1)

    if args.level2celpip:
        no_variables=False
        clb=int(args.level2celpip)
        items=[]
        if clb!=None: 
            if clb>10:
                clb=10
            elif clb<0:
                clb=0
            print(colored(f'\nCLB {clb} to CELPIP:','green'))
            items.append(['Read','Write','Listen','Speak'])
            items.append([clb,clb,clb,clb])
            utils.printFList2D(items)
        else:
            print('You should input clb level...')
            exit(1)

    if args.level2tef:
        no_variables=False
        clb=int(args.level2tef)
        items=[]
        if clb!=None:
            print(colored(f'\nCLB {clb} to TEF:','green'))
            items.append(['Read','Write','Listen','Speak'])
            tef=clb2tef(clb)
            items.append([str(tef[0])+'-'+str(tef[1]),str(tef[2])+'-'+str(tef[3]),str(tef[4])+'-'+str(tef[5]),str(tef[6])+'-'+str(tef[7])])
            utils.printFList2D(items)
        else:
            print('You should input clb level...')
            exit(1)        

    if args.level2tcf:
        no_variables=False
        clb=int(args.level2tcf)
        items=[]
        if clb!=None:
            print(colored(f'\nCLB {clb} to TCF:','green'))
            items.append(['Read','Write','Listen','Speak'])
            tcf=clb2tef(clb)
            items.append([str(tcf[0])+'-'+str(tcf[1]),str(tcf[2])+'-'+str(tcf[3]),str(tcf[4])+'-'+str(tcf[5]),str(tcf[6])+'-'+str(tcf[7])])

            utils.printFList2D(items)
        else:
            print('You should input clb level...')
            exit(1)

    if args.ielts2level:
        no_variables=False
        r=float(args.ielts2level[0])
        w=float(args.ielts2level[1])
        l=float(args.ielts2level[2])
        s=float(args.ielts2level[3])
        items=[]
        clb, [clb_r, clb_w, clb_l, clb_s] = getCLBs([r,w,l,s],'IELTS')
        items.append(['IELTS','Read','Write','Listen','Speak'])
        items.append(['',r,w,l,s])
        items.append(['CLB','Read','Write','Listen','Speak'])
        items.append([clb,clb_r,clb_w,clb_l,clb_l])
        utils.printFList2D(items)

    if args.celpip2level:
        no_variables=False
        r=int(args.celpip2level[0])
        w=int(args.celpip2level[1])
        l=int(args.celpip2level[2])
        s=int(args.celpip2level[3])
        clb,[clb_r, clb_w, clb_l, clb_s] = getCLBs([r,w,l,s],"CELPIP")
        items=[]
        items.append(['CELPIP','Read','Write','Listen','Speak'])
        items.append(['',r,w,l,s])
        items.append(['CLB','Read','Write','Listen','Speak'])
        items.append([clb,clb_r,clb_w,clb_l,clb_l])
        utils.printFList2D(items)
    
    if args.tef2level:
        no_variables=False
        r=int(args.tef2level[0])
        w=int(args.tef2level[1])
        l=int(args.tef2level[2])
        s=int(args.tef2level[3])
        clb, [clb_r, clb_w, clb_l, clb_s] = getCLBs([r,w,l,s],'TEF')
        items=[]
        items.append(['TEF','Read','Write','Listen','Speak'])
        items.append(['',r,w,l,s])
        items.append(['CLB','Read','Write','Listen','Speak'])
        items.append([clb,clb_r,clb_w,clb_l,clb_s])
        utils.printFList2D(items)
    
    if args.tcf2level:
        no_variables=False
        r=int(args.tcf2level[0])
        w=int(args.tcf2level[1])
        l=int(args.tcf2level[2])
        s=int(args.tcf2level[3])
        clb, [clb_r, clb_w, clb_l, clb_s] = getCLBs([r,w,l,s],'TCF')
        items=[]
        items.append(['TCF','Read','Write','Listen','Speak'])
        items.append(['',r,w,l,s])
        items.append(['CLB','Read','Write','Listen','Speak'])
        items.append([clb,clb_r,clb_w,clb_l,clb_s])
        utils.printFList2D(items)
    
    if args.level:
        no_variables=False
        clb=int(args.level)
        items=[['Test','Read','Write','Listen','Speak']]
        if clb!=None:
            ielts=clb2ielts(clb)
            ielts.insert(0,"IELTS")
            tef=clb2tef(clb)
            tef.insert(0,'TEF')
            tcf=clb2tcf(clb)
            tcf.insert(0,'TCF')
            items.append(ielts)
            items.append(['CELPIP',clb,clb,clb,clb])
            items.append([tef[0],str(tef[1])+'-'+str(tef[2]),str(tef[3])+'-'+str(tef[4]),str(tef[5])+'-'+str(tef[6]),str(tef[7])+'-'+str(tef[8])])
            items.append([tcf[0],str(tcf[1])+'-'+str(tcf[2]),str(tcf[3])+'-'+str(tcf[4]),str(tcf[5])+'-'+str(tcf[6]),str(tcf[7])+'-'+str(tcf[8])])
            print(colored(f"\nCLB level {clb} equivalents to:","green"))
            utils.printFList2D(items)
        else:
            print('You should input clb level...')
            exit(1)
   
    if no_variables:
        print('CLB->IELTS')
        clb_ielts_table.insert(0,['Level','Read','Write','Listen','Speak'])
        utils.printFList2D(clb_ielts_table)
        
        print('CLB->TEF')
        tef=[['Level','Read','Write','Listen','Speak']]
        for t in tef_clb_table:
            tef.append([t[0],str(t[1])+'-'+str(t[2]),str(t[3])+'-'+str(t[4]),str(t[5])+'-'+str(t[6]),str(t[7])+'-'+str(t[8])])
        utils.printFList2D(tef)
        
        print('CLB->TCF')
        tef=[['Level','Read','Write','Listen','Speak']]
        for t in tcf_clb_table:
            tef.append([t[0],str(t[1])+'-'+str(t[2]),str(t[3])+'-'+str(t[4]),str(t[5])+'-'+str(t[6]),str(t[7])+'-'+str(t[8])])
        utils.printFList2D(tef)

if __name__=='__main__':
    main()
