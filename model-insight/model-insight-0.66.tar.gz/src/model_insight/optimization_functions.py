# -*- coding: utf-8 -*-
"""
Created on April 13,  2022

@author: wang Haihua
"""
import pandas as pd
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, value
from datetime import datetime
import numpy as np

#################################################################################################
###############################     1 Heuristic Algorithms        ###############################
#################################################################################################

####***************************     1.1 Simulated Annealing       ****************************###

def Simulated_Annealing(f, x, alpha=.99, t=10000, delta=.1, maxIter=1000):
        
    ''' Simulated Annealing Algorithm (objective: find global minimum)

    Parameters:
    ----------
    f - objective function, R^n -> R
    x - inital solution, starting point, R^n
    alpha - annealing schedule parameter
    t - inital temperature
    delta - neighborhood radius
    maxIter - maximum no. of iterations  
    
    Yields :
    --------
    result : a dictionary contains the following parameters
        - 'x_opt' : the optimal x value(s)
        - 'f_opt' : the optimal value of the objective function
        - 'x_hist': the array of x values
        - 'f_hist': the array of the objective function
        - 'time'  : time
    ''' 

    
    # initializing starting parameters
    results = {'x_opt':x, 'f_opt':f(x), 'x_hist':[x], 'time':[0],
               'f_hist':[f(x)], 'temp':[t], 'transProb':[0]}
    
    currIter = 1
    finished = False
    x_s = x    
    time_0 = datetime.now() # to measure speed
    
    while not finished:
        
        # x_c - uniformly drawing a candidate solution from neighborhood of x_s
        unif = np.random.rand(len(x_s))
        x_c = x_s + (-delta + 2*delta*unif)
    
        # A - calculating Metropolis activation function
        A = np.minimum(1, np.exp(-(f(x_c) - f(x_s)) / t))
    
        # transition to candidate solution
        if bool(np.random.rand(1) < A):
            x_s = x_c
        
        # temperature update for the next iteration
        t = alpha * t

    
        if currIter < maxIter:
            
            # if better solution, update results
            if f(x_s) < f(results['x_opt']):
                results['x_opt'] = x_s
                results['f_opt'] = f(x_s)
            
            # update results history
            results['x_hist'].append(x_s)
            results['f_hist'].append(f(x_s))
            results['time'].append((datetime.now() - time_0).microseconds)

            results['transProb'].append(A)
        else:
            finished = True
        
        # if currIter % 250 == 0:
        #     print(f"f_opt after {currIter} iterations: {results['x_opt']} \n")
        
        currIter += 1
    print('The optimal x:',results['x_opt'])
    print('The optimal objective function :',results['f_opt'])
    return results['x_opt'],results['f_opt']


####***************************     1.2 Genetic Algorithm       ****************************###

# two helper functions
def binToInt(x):
    # Translate the binary chromosome to real values
    flipped = np.flipud(x)
    idx = np.argwhere(flipped==1).reshape(-1,)
    return (2**idx).sum()
  
def getCoords(population, cel, x_min, x_max):
    # Transform the binary chromosome of size 'cel' into real values of size 2
    coords = np.zeros((population.shape[0], 2))
    for i in range(population.shape[0]):
        for j in range(2): # test for more dimensions in spare time
            coordTemp = binToInt(population[i, (j*cel):((j+1)*cel)])
            # ensuring we are not leaving bounding box
            coords[i, j] = ((x_max[j]-x_min[j])/(2**cel))*coordTemp + x_min[j]
            
    return(coords)


def Genetic_Algorithm(f, x_min=[-20, -20], x_max=[20, 20], cel=50,
                     popSize=30, pMut=0.05, maxIter=1000):

    ''' Genetic Algorithm (objective: find global minimum)

    Parameters:
    ----------
    - f: objective function, R^n -> R
    - x_min: vector of the minimum values of coordinates, 
    - x_max: vector of the maximum values of coordinates
    - cel: coordinate encryption length, number of genes in a single chromosome
    - popSize: size of the population
    - pMut: probability of single genome mutation
    - maxIter: number of generations
    
    Yields :
    --------
    results : a dictionary contains the following parameters
        - 'x_opt' : the optimal x value(s)
        - 'f_opt' : the optimal value of the objective function
        - 'x_hist': the array of x values
        - 'f_hist': the array of the objective function
        - 'time'  : time
    ''' 

  
    # initializing history
    results = {'x_opt':[], 'f_opt':[], 'x_hist':[], 'f_mean':[], 
               'f_hist':[], 'time':[]}

    # Check the number of dimensions
    d = len(x_min) 
        
    # Initialize population
    population = np.zeros((popSize, cel*d))
      
    for i in range(popSize):
        # .5 chosen arbitrarily
        population[i,] = np.random.uniform(size=cel*d) > .5 
    
    coordinates = getCoords(population, cel, x_min, x_max)
      
    # Calculate fittness of individuals
    objFunction = np.zeros((popSize,))
    for i in range(popSize):
        objFunction[i] = f(coordinates[i,])
    
    # Assign the first population to output 
    results['x_opt'] = coordinates[np.argmin(objFunction),]
    results['f_opt'] = f(coordinates[np.argmin(objFunction),])
      
    # The generational loop
    finished = False
    currIter = 1
    time_0 = datetime.now() # to measure speed

    
    while not finished:
        # Assign the output
        if currIter <= maxIter:
            if results['f_opt'] > f(coordinates[np.argmin(objFunction),]):
                results['x_opt'] = coordinates[np.argmin(objFunction),]
                results['f_opt'] = f(coordinates[np.argmin(objFunction),])
          
            results['f_hist'].append(results['f_opt'])
            results['x_hist'].append(coordinates[np.argmin(objFunction),])
            results['f_mean'].append(np.mean(objFunction))
            results['time'].append((datetime.now() - time_0).microseconds)
        else:
          finished = True

        
        # Translate binary coding into real values to calculate function value
        coordinates = getCoords(population, cel, x_min, x_max)
        
        # Calculate fittness of the individuals
        objFunction = np.zeros((popSize,))
        for i in range(popSize):
            objFunction[i] = f(coordinates[i,])
        
        np.warnings.filterwarnings('ignore')

        rFitt = np.divide(min(objFunction), objFunction) # relative fittness
        # relative normalized fittness (sum up to 1) :
        nrFitt = np.divide(rFitt, sum(rFitt))
                
        # Selection operator (roulette wheel), analogy to disk
        selectedPool = np.zeros((popSize,))
        for i in range(popSize):
            selectedPool[i] = np.argmin(np.random.uniform(size=1) > np.cumsum(nrFitt))

        
        # Crossover operator (for selected pool)
        nextGeneration = np.zeros((popSize, cel*d))
        for i in range(popSize):
            parentId = int(np.round(np.random.uniform(1, popSize-1, 1)))
            cutId = int(np.round(np.random.uniform(1, d*cel-2, 1)))
            # Create offspring
            nextGeneration[i, :cutId] = population[int(selectedPool[i]), :cutId]
            nextGeneration[i, cutId:(d*cel)] = population[int(selectedPool[parentId]), cutId:(d*cel)]
        
        # Mutation operator
        for i in range(popSize):
            # Draw the genomes that will mutate
            genomeMutId = np.argwhere(np.random.rand(d*cel) < pMut)
            for j in range(len(genomeMutId)):
                nextGeneration[i, genomeMutId[j]] = not nextGeneration[i, genomeMutId[j]] 
        
        # Replace the old population
        population = nextGeneration
        currIter += 1

    print('The optimal x:',results['x_opt'])
    print('The optimal objective function :',results['f_opt'])
    return results['x_opt'],results['f_opt']


####***************************     1.3 Particle Swarm Optimization       ****************************###

def PSO(f, swarm_size=20, max_iter=200, x_min=[-20,-20], x_max=[20,20],
        c1=1, c2=1, omega=.5):

    ''' Particle Swarm Optimization (objective: find global minimum)

    Parameters:
    ----------
    - f: objective function, R^n -> R,
    - x_min: vector of the minimum values of coordinates, 
    - x_max: vector of the maximum values of coordinates,
    - swarm_size: number of particles in the swarm
    - max_iter: maximum number of iterations
    - c1: weight of personal best result of a particule
    - c2: weight of global best result of a swarm
    - omega: weight of current velocity
    
    Yields :
    --------
    results : a dictionary contains the following parameters
        - 'x_opt' : the optimal x value(s)
        - 'f_opt' : the optimal value of the objective function
        - 'x_hist': the array of x values
        - 'f_hist': the array of the objective function
        - 'time'  : time
    '''

    
    dim = len(x_min) 
    r = np.empty((swarm_size, dim))
    s = np.empty((swarm_size, dim))
    
    # initializing swarm
    swarm = np.empty((swarm_size, dim))
    velocity = np.empty((swarm_size, dim))
    p_best = np.empty((swarm_size, dim))
    swarm_result = np.empty((swarm_size, 1))
    
    # for each particle and each dimension initialize starting points
    for i in range(swarm_size):
        for j in range(dim):
            swarm[i, j] = np.random.uniform(low=x_min[j], high=x_max[j], size=1)
        velocity[i,:] = np.random.uniform(low=0, high=1, size=dim)
        p_best[i,:] = swarm[i,:]
        swarm_result[i] = f(swarm[i,:])
        g_best = swarm[np.argmin(swarm_result),:] # updating global best solution
    
    results = {'x_opt': [g_best], 'f_opt':[f(g_best)], 'x_hist':[g_best],
               'f_hist':[f(g_best)], 'time':[0]}

    
    pocz_iter = datetime.now()
    
    for k in range(max_iter):
        
        for m in range(swarm_size):
            r[m, :] = np.random.uniform(low=0, high=1, size=dim)
            s[m, :] = np.random.uniform(low=0, high=1, size=dim)
            
            # calculating components of new velocity
            old_vel = omega * velocity[m,:] # old velocity comp.
            best_pers_vel = c1 * r[m,:] * (p_best[m,:]-swarm[m,:]) # personal best comp.
            best_glob_vel = c2 * s[m,:] * (g_best-swarm[m,:]) # global best comp.
            # calculating new velocity
            velocity[m, :] = old_vel + best_pers_vel + best_glob_vel 
            # moving a particle in a new direction
            swarm[m, :] += velocity[m, :]
            
            # updating best solution for particle m
            if f(swarm[i,]) < f(p_best[i,]):
                p_best[m, :] = swarm[m, :]
            swarm_result[m] = f(swarm[m, :])
 

       
        # updating global best particle in iteration k
        if min(swarm_result)[0] < f(g_best):
            g_best = swarm[np.argmin(swarm_result), :]
        
        # saving history
        if results['f_opt'] > f(g_best):
            results['x_opt'] = swarm[np.argmin(swarm_result),:]
            results['f_opt'] = f(swarm[np.argmin(swarm_result),:])
        
        results['x_hist'].append(g_best)
        results['f_hist'].append(f(g_best))
        results['time'].append((datetime.now()-pocz_iter).microseconds)
    print('The optimal x:',results['x_opt'])
    print('The optimal objective function :',results['f_opt']) 
    return results['x_opt'],results['f_opt']


#################################################################################################
###############################     2 DEA                         ###############################
#################################################################################################

def dea(df_input,df_output,model_type='CRS'):
    ''' Data Evelopment Analysis(DEA) model

    Parameters:
    ----------
    - df_input : a DataFrame object containing the input data
    - df_output: a DataFrame object containing the output data
    - model_type:
        - 'CRS': CRS
        - 'VRS': VRS

    Yields :
    --------
    df_result : the DataFrame of the result

    '''    
    # Set building
    K = df_input.index
    I = df_input.columns
    J = df_output.columns
    X = df_input.to_dict()
    Y = df_output.to_dict()
    
    eta_plus = {}
    eta_minus={}
    objective_ = {}
    eps=0.00000001
    r = 0
    
    for k in K:
        # Model Building
        model = LpProblem(model_type+'_'+k, LpMinimize)  

        # Decision variables Building
        theta_r = LpVariable('theta_r',lowBound=0,upBound=1)
        lambda_k = LpVariable.dicts('lambda_k', lowBound=0, indexs=K)
        eta_plus_i = LpVariable.dicts('eta_plus_i',lowBound=0,indexs=I)
        eta_minus_j = LpVariable.dicts('eta_minus_j',lowBound=0,indexs=J)

        # Objective Function setting
        model += theta_r-eps*lpSum(eta_plus_i[i] for i in I)-eps*lpSum(eta_minus_j[j] for j in J)

        # Constraints setting
        for i in I:
            model += lpSum([
                    lambda_k[k] * X[i][k]
                for k in K]) + eta_plus_i[i] == theta_r * float(X[i][K[r]])
        for j in J:
            model += lpSum([
                    lambda_k[k] * Y[j][k]
                for k in K]) - eta_minus_j[j] == float(Y[j][K[r]])
            
        if model_type.upper()=='VRS':
            model += lpSum([ lambda_k[k] for k in K]) == 1
        # Model solving
        model.solve()
        
        eta_plus[k] = {}
        eta_minus[k] = {}
        for i in I:
            eta_plus[k][i] = value(eta_plus_i[i])
        for j in J:
            eta_minus[k][j] = value(eta_minus_j[j])
        objective_[k] = value(model.objective)
        
        r += 1
    df_obj = pd.DataFrame(pd.Series(objective_),columns=['Efficency']).T
    df_plus = pd.DataFrame(eta_plus)
    df_minus = pd.DataFrame(eta_minus)
    df_result = pd.concat([df_obj,df_plus,df_minus]).T
    return df_result
