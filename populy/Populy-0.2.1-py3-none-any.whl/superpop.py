
import pandas as pd 
import matplotlib.pyplot as plt 
import matplotlib
import os
import numpy as np
from .population import Population

class Superpop():
    
    def __init__(self,popsize,n,**kwargs):
        '''
        Multiple population simulations at the same time.
        
        Args:
            popsize (int): population size for all populations
            n (int): number of populations
            kwargs: same as Population class
                ploidy (int): Number of homologous chromosomes. Defaults to 2.
                R (float) : Recombination frequency [0,0.5] where 0.5 indicates
                statistic independence. Defaults to 0.5. 
                mu (tuple(float,float)): Mutation rate. Defaults to (1e-4,1e-4).
                freq (dict): loci (key) and allelic frequencies for each allele (values).
                D (float): initial linkage desequilibrium [0,0.5]. Defaults to 0. 
                fit (int,dict): fitness function applied, can take allele fitness value
                or genotype fitness value. E.g. {'A':0.8} or {'AABB':0.8}. Every other 
                value is set to 1. Defaults to 0 (no fitness function applied).
                sex_system (str) : sex determination sistem. Can be XY,ZW or X0. 
                Defaults to 'XY'.
                rnd (bool) : If set to True every other parameter is changed to
                a new random value (R,D,mu,freq). Defaults to False.
            '''

        self.popsize = popsize
        self.n = n
        self.kwargs = kwargs
        self.sPop = [Population(popsize,**kwargs)for x in range(n)] 
    
        
    def startPops(self,gens,**kwargs):
        """Inicializes population individuals and evolves them

        Args:
            gens (int): number of generations

        Returns:
            list: list of dictionaries which contains allelic frequencies 
            for every population
        """
        cada = 5
        for key,value in kwargs.items():
            if key == 'every':
                cada = value

            
        printInfo = False
        # inicializamos
        [x.initIndividuals()  for x in self.sPop]
        #evolucionamos
        [x.evolvePop(gens,every=cada,printInfo=False) for x in self.sPop]
        # guarda las frecuencias alelicas acumuladas en una lista
        self.freqs = [d.f_ale_acc for d in self.sPop]
        os.system("cls")
        
        return self.freqs
    
    def plotPops(self):
        """Displays allelic frequencies with matplotlib
        """
    
        # numero de generaciones
        gens = self.sPop[0].gen
        # recogida de informacion
        steps = self.sPop[0].steps
        #ploidia
        ploidy = self.sPop[0].ploidy
        
        labels = ['gen.'+str(x) for x in range(0,gens+1,steps)]
        
              
        popListnames = ['p'+str(i) for i in range(len(self.freqs))]
        
        fig,ax=plt.subplots(1,ploidy,figsize=(13,6))
        plt.suptitle(f"Deriva genética para {self.popsize} indvididuos")
        plt.style.use('ggplot')
        if "rnd" in self.kwargs and self.kwargs["rnd"] == True:
            caption = ""
        else:
            caption=f"""Caracteristicas iniciales: frecuencia gametica={self.sPop[0].freq}, R={self.sPop[0].R}
                    frecuencia de mutación={self.sPop[0].mu}""" 
        plt.figtext(0.5, 0.01, caption, wrap=True, horizontalalignment='center', fontsize=10)
        for j,let in enumerate(self.freqs[0].keys()):
            for i in range(len(self.freqs)): 
                with plt.style.context("ggplot"):
                    ax[j].set_title(f"Locus {let}")
                    ax[j].set_ylabel(f'frecuencia de {let}')
                    ax[j].set_xlabel("Generaciones")
                    ax[j].plot(self.freqs[i][let])
                    ax[j].set_ylim([0,1])
                    
                
        new_steps = int(len(labels)/5) if len(labels)>8 else 1
        plt.setp(ax, xticks=range(0,len(labels),new_steps), xticklabels=labels[::new_steps])
        
        plt.show()
        
        
if __name__ == '__main__':
    
    superpop = Superpop(10,n=5,ploidy=2,fit={'A':(0.5,0.5)},rnd=False)
    
    alFreq_sp = superpop.startPops(gens=100,every=1)
    
    
    superpop.plotPops()
        
