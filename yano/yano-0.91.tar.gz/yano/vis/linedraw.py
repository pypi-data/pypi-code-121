import matplotlib.pyplot as plt
import numpy as np

from scipy.optimize import minimize

from tqdm import tqdm


def dualiter(q):
    for i in range(len(q)-1):
        yield q[i], q[i+1]

def draw(samples,truth,func,borders,minx,maxx,miny,maxy, hist=True):

    startingpoints=10#0
    epsilon=0.001
    continuepoints=100
    maxwidth=1000

    linecount=5000
    linesteps=10
    refinement=5

    if type(borders) is not list:
        borders=[borders]


    epsilonx=epsilon*(maxx-minx)
    epsiolny=epsilon*(maxy-miny)

    #print(minx,maxx,miny,maxy)

    sample0=np.array([s for s,t in zip(samples,truth) if t==0])
    sample1=np.array([s for s,t in zip(samples,truth) if t==1])

    if hist:

        hist0=np.histogram2d(sample0[:,0],sample0[:,1],bins=100,range=[[minx,maxx],[miny,maxy]])[0].T
        hist1=np.histogram2d(sample1[:,0],sample1[:,1],bins=100,range=[[minx,maxx],[miny,maxy]])[0].T
        hist=hist1-hist0
        plt.imshow(hist,extent=[minx,maxx,miny,maxy],origin='lower',cmap="hot")
        plt.grid(False)

    for border in borders:
    
        #plt.hist2d(samples[:,0],samples[:,1],bins=100,range=[[minx,maxx],[miny,maxy]])
    
        #plt.fill(dx,dy,color="red",alpha=0.1)
    
    
        def color(point):
            return (func(point)>border).astype(float)
    
    
        def intermediate_line(x1,x2,y1,y2,cou=100):
            dx,dy=x2-x1,y2-y1
            t=np.arange(0,1,1/cou)
            x=x1+dx*t
            y=y1+dy*t
            q=np.concatenate((np.expand_dims(x,1),np.expand_dims(y,1)),axis=1)
            return q
    
        def random_line(cou=100):
            x1,x2=np.random.uniform(minx,maxx,2)
            y1,y2=np.random.uniform(miny,maxy,2)
            return intermediate_line(x1,x2,y1,y2,cou)
        
        todoo=[random_line(cou=linesteps) for i in range(linecount)]
        hyperbreak=False
        for i in tqdm(range(refinement)):
            if len(todoo)==0:
                print("failed to find anomalousness value")
                hyperbreak=True
                continue
            nextlines=[]
            lines=np.array(todoo)
            lineshape=lines.shape
            lines=lines.reshape(lineshape[0]*lineshape[1],2)
        
        
            colors=color(lines)
            colors=colors.reshape(lineshape[:-1])
            lines=lines.reshape(lineshape)
        
        
            for line,colo in zip(lines,colors):
                for (x1,x2),(c1,c2) in zip(dualiter(line),dualiter(colo)):
                    #print(x1,x2,c1,c2)
                    if c1!=c2:
                        nextlines.append((x1,x2))
            todoo=[intermediate_line(x1[0],x2[0],x1[1],x2[1],cou=linesteps) for x1,x2 in nextlines]
        if hyperbreak:break
        matter=[]
        for x1,x2 in nextlines:
            matter.append((x1+x2)/2)
    
        matter=np.array(matter)
    
    
    
        plt.plot(matter[:,0],matter[:,1],".",alpha=0.3)
    
    
    
    
    
