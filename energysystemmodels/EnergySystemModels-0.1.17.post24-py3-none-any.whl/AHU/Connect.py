from AHU.AirPort.AirPort import AirPort
def Air_connect( entree=AirPort(),sortie=AirPort()): # a : port d'entrée d'un composant, b sortie composant 
    entree.HA=sortie.HA #humidité absolue en g/kgas"
    entree.P=sortie.P
    entree.h=sortie.h #kJ/kgas
    entree.F_kgs=sortie.F_kgs
    return "connectés"