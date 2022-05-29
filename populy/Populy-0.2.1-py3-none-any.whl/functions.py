
import random
from struct import pack

def outer_product(f: dict):
    """Calculate the outer product of two vectors and stores them on a dictionary
        Args:
        f(dict[char:str]): chromosome
        
        Returns:
        dict: genotype"""
    # lista de tuplas con los valores de frecuencia alelica
    fValues = list(f.values())
    # primera tupla
    a = fValues[0]
    finalD = dict()
    # recorremos todos los valores
    for x in range(1,len(fValues)):
        d = dict()
        values = list()
        names = list()
        k=0
        # recorremos la tupla numero i
        for i,val_i in enumerate(a):
            #recorremos el resto de tuplas
            for j,val_j in enumerate(fValues[x]):
                    # multiplicamos el valor i de la primera tupla
                    # por el valor j de la tupla x
                    values.append(val_i*val_j)
                    # cambiamos el nombre
                    letrai,letraj = rename(i,j,x,k,finalD)
                    names.append(letrai+letraj)
                    if j%2==1:
                        k+=1
        finalD = dict(zip(names,values))
        a = list(finalD.values())
    if len(list(f.keys()))==1: # si solo hay un locus
        # la letra (prob. A)
        letter = list(f.keys())
        # lista de keys (A,a)
        letter.append(letter[0].lower())
        # lista de valores ej: (0.4,0,6)
        values = list(f.values())[0]
        # se hace diccionario
        finalD = dict(zip(letter,values))
        
    return finalD

def rename(i,j,iteration,k,finalDict):
    """rename

    Args:
        i (_type_): _description_
        j (_type_): _description_
        iteration (_type_): _description_
        k (_type_): _description_
        finalDict (_type_): _description_

    Returns:
        _type_: _description_
    """
    # check if it is the first round
    if iteration==1:
        letrai =chr(ord('A')+iteration-1)
        # check if its the first position
        if i==1:
            letrai = letrai.lower()
    else:
        letrai = list(finalDict.keys())[k]

    if j==1:
        letraj = chr(ord('A')+iteration).lower()
    else:
        letraj = chr(ord('A')+iteration)
    return letrai,letraj


def fitness(fit : dict, genotype):
    '''
    A partir del tipo de seleccion y del genotipo que se le pase
    Te devuelve si ese individuo vive o muere.
    
    Args:
        fit ( dict[str : int] ): valor de fitness de genotipo o alelo
        ej.1: fit = {'locusA':(0.8,0.9)...}
        ej.2. fit = {'}
        
        child_gen (dict[str:int]): genotipo del individuo
    '''
    def live_die(p):
        """
        Función de vida o muerte, si el valor generado
        es mayor que el valor pasado como parametro muere.

        Args:
            p (_type_): _description_

        Returns:
            bool: decide si vive(True) o muere(False)
        """
        randNum = random.random()
        if randNum <= p:
            return True
        else:
            return False

    # Fitness segun locus/genotipo
    # si tiene 1 A = fit[A][0]*fit[A][1]
    # si tiene 0 A = fit[A][1]**2
    # ...
    if type(fit) is not int:
        # para alelo
        for k,v in genotype.items():
            # si el locus esta en los valores de fit
            if any(k == c for c in fit):
                # recorremos cada alelo del genotipo para el locus dado k
                p = 1
                for letra in v:
                    # si es el mayor llamamos a una probabilidad, si no a otra
                    if letra.isupper():
                        p *= fit[k][0]
                    else:
                        p *= fit[k][1]
                    if live_die(p) == False:
                        return False     
        else:
            # para genotipos completos
            for k,v in fit.items():
                genotipo = ''.join(genotype.values())
                if genotipo == k:
                    if live_die(v) == False:
                        return False
            else:
                return True 
            
    # fitness numerico
    if fit==0:
        return True
    if fit==1:
        if 'Aa'== genotype['A']:
            return live_die(0.9)
        if 'aa'== genotype['A']:
            return live_die(0.81)
    if fit==2:
        if 'Aa'== genotype['A']:
            return live_die(0.9)
        if 'AA'== genotype['A']:
            return live_die(0.81)
    if fit==3:
        if 'aa'== genotype['A'] and 'bb'== genotype['B']:
            return False
    
    return True
        
        
    
