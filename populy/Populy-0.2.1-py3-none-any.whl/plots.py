
import matplotlib.pyplot as plt
import pandas as pd

from .population import Population
from .superpop import Superpop

class Plots:
    
    def __init__(self):
        pass
    
    def __populationInfo(pop):
        try:
            labels = ['gen.'+str(x) for x in range(0,pop.gen+1,pop.steps)]
        except e as e:
            print(e)
            
        caption=f"""Caracteristicas iniciales: frecuencia gametica={pop.freq}, R={pop.R}
        frecuencia de mutación={pop.mu}"""
        
        return labels, caption
        
    def alleles(pop: Population):
        '''
        Metodo estatico que recibe un dataframe y lo representa
        graficamente
        '''
        labels,caption = Plots.__populationInfo(pop)
        alleles = pop.getDataFrame('alelos')      
        plt.style.use('ggplot')
        plt.title("Change in allelic frequencies")
        plt.tight_layout()
        plt.xlabel("Generations")
        plt.ylabel("Allelic frequencies")
        plt.ylim([0,1])
        plt.plot(alleles)  
        plt.legend(alleles.columns)
        plt.show()
        
    def gametes(pop: population.Population):
        labels,caption = Plots.__populationInfo(pop)
        gametes = pop.getDataFrame('gametos')
        
        plt.style.use('ggplot')
        plt.title("Change in gametic frequencies")
        plt.tight_layout()
        plt.xlabel("Generations")
        plt.ylabel("Gametic frequencies")
        plt.ylim([0,1])
        plt.plot(gametes)
        plt.legend(gametes.columns)
        plt.show()
        
    def sex(pop: population.Population):
        labels,caption = Plots.__populationInfo(pop)
        sex = pop.getDataFrame('sex')
        
        plt.style.use('ggplot')
        plt.title("Change in sex frequencies")
        plt.tight_layout()
        plt.xlabel("Generations")
        plt.ylabel("Frequency")
        plt.ylim([0,1])
        plt.plot(sex)
        plt.legend(sex.columns)
        plt.show()
        
    def mutations(pop: population.Population):
        labels, caption = Plots.__populationInfo(pop)
        mut = pop.getDataFrame('mutantes')
        
        plt.style.use('ggplot')
        plt.title("Number of total mutations per generation")
        plt.tight_layout()
        plt.xlabel("Generations")
        plt.ylabel("Mutants")
        plt.plot(mut)
        plt.legend(mut.columns)
        plt.show()
        