
CEE_cost=5.0 #euro/MWhcumac
H1=[1,2,3,5,8,10,14,15,19,21,23,25,27,28,38,39,42,43,45,51,52,54,55,57,58,59,60,61,62,63,67,68,69,70,71,73,74,75,76,77,78,80,87,88,89,90,91,92,93,94,95,975]
H2=[4,7,9,12,16,17,18,22,24,26,29,31,32,33,35,36,37,40,41,44,46,47,48,49,50,53,56,64,65,72,79,81,82,84,85,86]
H3=[6,11,13,20,30,34,66,83,971,972,973,974,976]

#Operating_Mode : "1*8h" ,"2*8h" ,"3*8h" ,"3*8h&WE"
#Equipement_type : "pump","fan","air compressor","chiller"
#P_KW : <=1000 kW , Puissance électrique nominale du moteur entraînant le système moto-régulé (en kW)

def IND_UT_136(Operating_Mode, Equipement_type,P_KW):
    global CEE_cost
    if P_KW<=1000:
        if Equipement_type=="pump" or Equipement_type=="fan":
        
            if Operating_Mode=="1*8h" :
                kWh_cumac=7800*P_KW
            if Operating_Mode=="2*8h" :
                kWh_cumac=17100*P_KW
            if Operating_Mode=="3*8h" :
                kWh_cumac=23300*P_KW
            if Operating_Mode=="3*8h&WE"  :
                kWh_cumac=32600*P_KW
            MWh_cumac=kWh_cumac/1000
            euro=MWh_cumac*CEE_cost

        if Equipement_type=="air compressor" or Equipement_type=="chiller":
        
            if Operating_Mode=="1*8h" :
                kWhcumac_kW=4400
            if Operating_Mode=="2*8h" :
                kWhcumac_kW=9800
            if Operating_Mode=="3*8h" :
                kWhcumac_kW=13300
            if Operating_Mode=="3*8h&WE":
                kWhcumac_kW=18600
            
            kWh_cumac=kWhcumac_kW*P_KW
            MWh_cumac=kWh_cumac/1000
            euro=MWh_cumac*CEE_cost

    else:
        MWh_cumac=0
        euro=0
    return "Systèmes moto-régulés : ",MWh_cumac, euro,

#print(IND_UT_136("1*8h",20))

def IND_UT_135(Operating_Mode, Department, Supply_Temperature, P_KW):

    global CEE_cost
    global H1,H2,H3

    if Department in H1:
        if 12 <= Supply_Temperature <15:
            kWhcumac_kW=7400
        if 15 <= Supply_Temperature <18:
            kWhcumac_kW=9900
        if 18 <= Supply_Temperature <=21:
            kWhcumac_kW=12300

    if Department in H2:
        if 12 <= Supply_Temperature <15:
            kWhcumac_kW=4900
        if 15 <= Supply_Temperature <18:
            kWhcumac_kW=8200
        if 18 <= Supply_Temperature <=21:
            kWhcumac_kW=11500

    if Department in H3:
        if 12 <= Supply_Temperature <15:
            kWhcumac_kW=3300
        if 15 <= Supply_Temperature <18:
            kWhcumac_kW=5800
        if 18 <= Supply_Temperature <=21:
            kWhcumac_kW=9000

    if Operating_Mode=="1*8h" :
        Coef=1.0
    if Operating_Mode=="2*8h" :
        Coef=2.2
    if Operating_Mode=="3*8h" :
        Coef=3.0
    if Operating_Mode=="3*8h&WE":
        Coef=4.2

    kWh_cumac=kWhcumac_kW*Coef*P_KW
    MWh_cumac=kWh_cumac/1000
    euro=MWh_cumac*CEE_cost


    return "Freecooling par eau de refroidissement en substitution d’un groupe froid : ",MWh_cumac, euro

#print(IND_UT_135("2*8h",65,15,10))
#Heat_Use : "chauffage de locaux","ECS","procédé industriel"
# P_KW : Puissance nominal de l'échangeur ou au max la puissance électrique nominale du compresseur
def IND_UT_103(Operating_Mode, Department, Heat_Use, P_KW):

    global CEE_cost
    global H1,H2,H3

    if Heat_Use=="chauffage de locaux" or Heat_Use=="ECS":

        if Department in H1:
            if Operating_Mode=="1*8h" :
                kWhcumac_kW=6400
            if Operating_Mode=="2*8h" :
                kWhcumac_kW=15900
            if Operating_Mode=="3*8h" :
                kWhcumac_kW=19700
            if Operating_Mode=="3*8h&WE":
                kWhcumac_kW=26700              

        if Department in H2:
            if Operating_Mode=="1*8h" :
                kWhcumac_kW=6000
            if Operating_Mode=="2*8h" :
                kWhcumac_kW=15000
            if Operating_Mode=="3*8h" :
                kWhcumac_kW=18600
            if Operating_Mode=="3*8h&WE":
                kWhcumac_kW=25200

        if Department in H3:
            if Operating_Mode=="1*8h" :
                kWhcumac_kW=5000
            if Operating_Mode=="2*8h" :
                kWhcumac_kW=12600
            if Operating_Mode=="3*8h" :
                kWhcumac_kW=15600
            if Operating_Mode=="3*8h&WE":
                kWhcumac_kW=21100

    if Heat_Use=="procédé industriel":
        if Operating_Mode=="1*8h" :
            kWhcumac_kW=10300
        if Operating_Mode=="2*8h" :
            kWhcumac_kW=25600
        if Operating_Mode=="3*8h" :
            kWhcumac_kW=31800
        if Operating_Mode=="3*8h&WE":
            kWhcumac_kW=43100

    kWh_cumac=kWhcumac_kW*P_KW
    MWh_cumac=kWh_cumac/1000
    euro=MWh_cumac*CEE_cost

    return "Système de récupération de chaleur sur un compresseur d’air : ",MWh_cumac, euro

def IND_UT_131(*Data):
    #Operating_Mode,  Temperature,Geometry,S (Plan)
    #Operating_Mode,Temperature, Geometry ,D,L (Cylindre)

    Operating_Mode=Data[0]
    Temperature=Data[1]
    Geometery=Data[2]
    if Geometery=="cylindre":
        D=Data[3]
        L=Data[4]
        if D>=508:
            S=3.141592653589793*D/1000*L
        if D<508:
            S=None
    if Geometery=="plan":
        S=Data[3]
    
    if Operating_Mode=="1*8h" :
        Coef=1.0
    if Operating_Mode=="2*8h" :
        Coef=2.2
    if Operating_Mode=="3*8h" :
        Coef=3.0
    if Operating_Mode=="3*8h&WE":
        Coef=4.2
    
    if S is not None:
        print("equation plan ou grand diamètre")
        if -60 < Temperature <=0:
            kWhcumac_m2=80
        if 0 < Temperature <=40:
            kWhcumac_m2=0
        if 40 < Temperature <=100:
            kWhcumac_m2=190
        if 100 < Temperature <=300:
            kWhcumac_m2=490
        if 300 < Temperature <=600:
            kWhcumac_m2=1100
        kWh_cumac=kWhcumac_m2*Coef*S
    

    else:
        print("equation cylindre avec D<508 mm")
        if -60 < Temperature <=0:
            kWhcumac_m=53
        if 0 < Temperature <=40:
            kWhcumac_m=0
        if 40 < Temperature <=100:
            kWhcumac_m=110
        if 100 < Temperature <=300:
            kWhcumac_m=310
        if 300 < Temperature <=600:
            kWhcumac_m=850
        kWh_cumac=kWhcumac_m*Coef*L

    MWh_cumac=kWh_cumac/1000
    euro=MWh_cumac*CEE_cost
    

    return "Isolation thermique des parois planes ou cylindriques sur des installations industrielles (France métropolitaine) : ",MWh_cumac, euro

def IND_UT_130(Operating_Mode,P_KW):
    global CEE_cost
    if P_KW<=20000:
        
        
        if Operating_Mode=="1*8h" :
            kWhcumac_kW=340
        if Operating_Mode=="2*8h" :
            kWhcumac_kW=740
        if Operating_Mode=="3*8h" :
            kWhcumac_kW=1000
        if Operating_Mode=="3*8h&WE"  :
            kWhcumac_kW=1400
        
       

       
            
        kWh_cumac=kWhcumac_kW*P_KW
        MWh_cumac=kWh_cumac/1000
        euro=MWh_cumac*CEE_cost

    else:
        MWh_cumac=0
        euro=0
    return "Condenseur sur les effluents gazeux d’une chaudière de production de vapeur : ",MWh_cumac, euro,


