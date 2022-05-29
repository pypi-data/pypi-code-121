'''
Clase Individual, solo es llamada por la clase poblacion y contiene
informacion sobre un individuo concreto
esto es:
str sexo: male or female
str ide: identificador que consta de generacion (g.X) + numero (ID-YYY)
int age: de momento sin usar
dict genotype: {'str': 'str'} siendo la clave A o B y los valores
                su genotipo para ese locus
'''
from calendar import c
import itertools
import numpy as np
from random import randint
import random
from .functions import outer_product

class Individual():


    def __init__(self,nom='1',name='n',
                 size=1,ploidy=2,
                 vida_media=0,
                 freq={'A':(0.4,0.6),'B':(0.6,0.4)},
                 d=0,R=0.5,mu=(0.1,0.1),
                 sex_system='XY',gen=0,
                 parents=0):
        
         
        self.spName = name
        self.spSize = size
        self.spPloidy = ploidy

        self.vida_media = vida_media
        
        self.ide = 'g'+str(gen)+".ID-"+str(nom)
        self.age = 0
        self.parents = parents
        self.sex_system = sex_system
        self.d = d
        # diccionario con frecuencias alelicas
        self.alFreq = freq
        # frecuencia de recombinacion
        self.R = R
        # tasa de mutacion
        self.mu = mu
        self.__createIndividual()
        

        
    def __createIndividual(self):
        '''
        Inicializa las variables que no se le pasan al inicializador
        '''
        self.chromosome = dict()
        self.isMutated = False
        # si tiene padres, es decir, no esta iniciada de 0...
        if self.parents:
            # self.mating()
            self.mating()
            self.mutation()
        else:
            self.sex_chromosome = self.generate_sexual_genotype()
            self.chromosome = self.chooseGametes()
            self.gameticFreq()
            
        self.sex = self.getSex()
        self.genotype = self.getGenotype()

            
    def generate_sexual_genotype(self):
        '''Genera un genotipo sexual, compuesto por dos valores correspondientes
        a cada un de los cromosomas, los almacena en la variable sex_chromosome
        
        Returns:
            str: cromosoma sexual para el individuo'''
        # sex_chromosome= 'XX'or'XY' / 'ZW' or 'ZZ' / 'XO' or 'XX'
        if randint(0,1)==0:
            return self.sex_system[0]+self.sex_system[0]
        else:
            return self.sex_system
        
    def getSex(self):
        '''Devuelve el sexo segun los chromosomas sexuales
        
        Returns:
            str: 'Male' or 'Female' '''
            
        if self.sex_chromosome[0] == self.sex_chromosome[1]:
            sexo = 'Female' if self.sex_system != 'ZW' else 'Male'
        else:
            sexo = 'Male'  if self.sex_system != 'ZW' else 'Female'
        return sexo
        
    def getGenotype(self):
        
        genotype = dict()
        # print(self.chromosome)
        for i,letra in enumerate(self.chromosome['c1']):
            if self.spPloidy == 2:
                genotype[letra.upper()] = ''.join(sorted(self.chromosome['c1'][i] + 
                                                         self.chromosome['c2'][i]))
            else:
                genotype[letra.upper()] = self.chromosome['c1'][i]
        
        return genotype

    # Calcula la frecuencia gametica a partir de las frecuencias alelicas y D
    # esto quiza deberia estar en population !!!revisar
    def gameticFreq(self):

        f = self.alFreq
        d = self.d
        fGametes = dict()
        
        #producto externo (outer product)
        freqValues = list(f.values())
        inp = freqValues[0]
        finalDict = dict()
        if len(freqValues)>1:
            fGametes = outer_product(f)
        else:
            word = str(list(f.keys())[0])
            keys = [word,word.lower()]
            
            values = list(freqValues[0])  
                 
            fGametes = dict(zip(keys,values))

        return fGametes

    # Elige un gameto segun su probabilidad (frecuencia)
    def chooseGametes(self):
        """Choose a gamete from gameticFreq keys
        by its given probability in gameticFreq values

        Returns:
           dict(str:str): two chromosomes and its genotype
        """
        chrom = dict()
        fGametes = self.gameticFreq()
        
        gameto =list(fGametes.keys())
        pesos = list(fGametes.values())
        
        for i in range(1,self.spPloidy+1):
            
            chrom['c'+str(i)]= ''.join(random.choices(gameto,
                                            weights=pesos,k=1))

        # self.chromosome = chrom
        return chrom

    
    # metodo dunder
    def __str__(self):
        return ("Este individuo es {}, su sexo es {} su genotipo es {}"
              .format(self.ide,self.sex,self.chromosome))
    
    def printParents(self,):
        '''
        Print individual parents
        '''
        
        print(f'''su padre es {self.parents[0].ide}, 
        con genotipo {self.parents[0].chromosome}\n su madre es {self.parents[1].ide}
        con genotipo {self.parents[1].chromosome}''')

    # calculates
    def mating(self):
        # print(self.chromosome,len(self.chromosome))
        if self.spPloidy > 1:
            r = self.R
            for x in range(len(self.parents)):
                # autosomas
                c1P = self.parents[x].chromosome['c1']
                c2P = self.parents[x].chromosome['c2']
                # metodo de recombinacion
                c1,c2 = self.recombination(c1P,c2P,r)              
                self.chromosome['c'+str(x+1)] = random.choice([c1,c2])   
            # cromosomas sexuales sex_chromosome: str XX/XY or ZW/ZZ or XX/X0
            sP = self.parents[0].sex_chromosome
            sM = self.parents[1].sex_chromosome
            self.sex_chromosome = ''.join(sorted([random.choice(sP),random.choice(sM)]))
        else:  
            self.chromosome = {'c'+str(k+1):v for k in range(2) for v in random.choice(self.parents[k].chromosome.values())}

    def recombination(self,c1,c2,r):
        # factor de interferencia
        # para que sea menos probable la recombinacion de dos loci seguidos
        int = 0
        for i in range(0,len(c1),2):
            if random.random()<=r-int:
                # ocurre la recombinacion (solo recombinan los loci A B )
                c1R = c1[i]+c2[i+1:]
                c2R = c2[i]+c1[i+1:] 
                int = r/2
                
                c1 = c1R
                c2 = c2R
            else:
                int = 0
            
            
        return c1,c2
            
    
    def mutation(self):
        '''
        Provoca el cambio del alelo mayor al menor con una frecuencia mut
        '''
        muType = 'unidirectional'
        #000100 significa que ha mutado en la posicion 4
        self.adMutated = ''
        for k,v in self.chromosome.items():
            for i in range(len(v)):
                #comprueba si es el alelo mayor
                if v[i].isupper():
                    #si muta, cambia el alelo del cromosoma por el alelo menor
                    if random.random() < self.mu[i]:
                        self.chromosome[k] = self.chromosome[k].replace(v[i],v[i].lower())
                        self.isMutated = True
                        self.adMutated += k
                    

            

