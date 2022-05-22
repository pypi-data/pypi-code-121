from math import*
def Pvs(T) :

#calcul de la pression de vapeur sat


	C1 = -5.6745359 * 10 ** 3
	C2 = 6.3925247 * 10 ** 0
	C3 = -9.677843 * 10 ** (-3)
	C4 = 6.2215701 * 10 ** (-7)
	C5 = 2.0747825 * 10 ** (-9)
	C6 = -9.484024 * 10 ** (-13)
	C7 = 4.1635019 * 10 ** (0)
	C8 = -5.8002206 * 10 ** (3)
	C9 = 1.3914993 * 10 ** (0)
	C10 = -4.8640239 * 10 ** (-2)
	C11 = 4.1764768 * 10 ** (-5)
	C12 = -1.4452093 * 10 ** (-8)
	C13 = 6.5459673 * 10 ** (0)

	Tk = T + 273.15

	if T < 0 : #valable entre -100 et 0 °C

		Pvs = exp(C1 / Tk + C2 + C3 * Tk + C4 * Tk ** 2 + C5 * Tk ** 3 + C6 * Tk ** 4 + C7 * log(Tk))
	else :  #valable entre 0 et 200 °C

		Pvs = exp(C8 / Tk + C9 + C10 * Tk + C11 * Tk ** 2 + C12 * Tk ** 3 + C13 * log(Tk))




	return Pvs

def Tw(Td, HR) :   #calcul de la temp du bulbe humide
	Tw = Td * atan(0.151977 * (HR + 8.313659) ** (1 / 2)) + atan(Td + HR) - atan(HR - 1.676331) + 0.00391838 * (HR) ** (3 / 2) * atan(0.023101 * HR) - 4.686035
#Tw = 20 * atan(0.151977 * (50 + 8.313659) ** (1 / 2)) + atan(20 + 50) - atan(50 - 1.676331) + 0.00391838 * (50) ** (3 / 2) * atan(0.023101 * 50) - 4.686035
	return Tw


#Wet-Bulb Temperature from Relative Humidity and Air Temperature
#ROLAND STULL
#University of British Columbia, Vancouver, British Columbia, Canada
#(Manuscript received 14 July 2011, in final form 28 August 2011)


def HA(Pvs, HR, P):



	Pv = Pvs * (HR / 100)
	HA = 0.62198 * Pv / (P - Pv) * 1000


	return HA


def HR(Pvs, HA, P):

	Pv = P * (HA / 1000) / ((HA / 1000) + 0.62198)
	HR = (Pv / Pvs) * 100
	return HR

def T_sat(HA_target):

	T = -100
	Erreur = HA(Pvs(T), 100) - HA_target


	while Erreur <= 0 :
		T = T + 0.02
		Erreur = HA(Pvs(T), 100) - HA_target



	T_sat = T

	return T_sat



def T_Humidifier(HA_target, HA_init, Tinit):

	T = -100
	Erreur = -Enthalpie(Tinit, HA_init) + Enthalpie(T, HA_target)

	while Erreur < 0 :
		T = T + 0.01
		Erreur = -Enthalpie(Tinit, HA_init) + Enthalpie(T, HA_target)
 


	T_Humidifier = T - 0.01

	return T_Humidifier




def T_rosee(Pv):
	T = -100
	Erreur = -Pv + Pvs(T)

	while Erreur < 0 :
		T = T + 0.01
		Erreur = -Pv + Pvs(T)
  


	T_rosee = T - 0.01

	return T_rosee










def Enthalpie(T, HA):
	Enthalpie = 1.006 * T + (HA / 1000) * (2501 + 1.0805 * T)
	return Enthalpie
    
def Temperature(Enthalpie, HA):
	T=(Enthalpie-(HA / 1000) *2501)/(1.006+ (HA / 1000) *1.0805)
    
	return T

def T_Enthalpie_Ha(Enthalpie, HA):

	T_Enthalpie_Ha = (Enthalpie - (HA / 1000) * 2501) / (1.006 + (HA / 1000) * 1.0805)

	return T_Enthalpie_Ha



#def Temperature_Melange(m1, T1, HR1, m2, T2, HR2)

#Temperature_Melange = T_Enthalpie_Ha((Enthalpie(T1, (HA(Pvs(T1), HR1))) * (m1 / (1 + (HA(Pvs(T1), HR1)) / 1000)) + (Enthalpie(T2, (HA(Pvs(T2), HR2)))) * (m2 / (1 + (HA(Pvs(T2), HR2)) / 1000))) / ((m2 / (1 + (HA(Pvs(T2), HR2)) / 1000)) + (m1 / (1 + (HA(Pvs(T1), HR1)) / 1000))), 1000 * (((m2 / (1 + (HA(Pvs(T2), HR2)) / 1000)) * ((HA(Pvs(T2), HR2)) / 1000)) + ((m1 / (1 + (HA(Pvs(T1), HR1)) / 1000)) * ((HA(Pvs(T1), HR1)) / 1000))) / ((m2 / (1 + (HA(Pvs(T2), HR2)) / 1000)) + (m1 / (1 + (HA(Pvs(T1), HR1)) / 1000))))
#return
#def HA_Melange(m1, T1, HR1, m2, T2, HR2)

#HA_Melange = 1000 * (((m2 / (1 + (HA(Pvs(T2), HR2)) / 1000)) * ((HA(Pvs(T2), HR2)) / 1000)) + ((m1 / (1 + (HA(Pvs(T1), HR1)) / 1000)) * ((HA(Pvs(T1), HR1)) / 1000))) / ((m2 / (1 + (HA(Pvs(T2), HR2)) / 1000)) + (m1 / (1 + (HA(Pvs(T1), HR1)) / 1000)))
#return


def rho_ah(T, HR, P):

	Tk = T + 273.15


	Rv = 461
	Ra = 287.66
	Psat = Pvs(T)


	Pv = Psat * (HR / 100)
	rho_v = Pv / (Rv * Tk)
	rho_a = (P - Pv) / (Ra * Tk)

	Rah = Ra / (1 - ((HR / 100) * Psat / P) * (1 - Ra / Rv))

	rho_ah = (rho_a * Ra + rho_v * Rv) / Rah

	return rho_ah


