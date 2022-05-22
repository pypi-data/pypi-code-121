import matplotlib.pyplot as plt
import numpy as np

from .projector import learn_projection


from .linedraw import draw

def reducedraw(x,tx,ty,score,border,inc=0.0, hist=True):
    proj=learn_projection(x,n_components=2)

    q=proj.transform(x)
    tq=proj.transform(tx)

    if not type(score) is list:
        score=[score]

    def new_score(q, i=0):
        x=proj.inverse_transform(q)
        p=score[i](x)
        return p

    nscores=[lambda q, i=i: new_score(q, i) for i in range(len(score))]

    minx,maxx,miny,maxy=np.min(q[:,0]),np.max(q[:,0]),np.min(q[:,1]),np.max(q[:,1])
    minx=minx-(maxx-minx)*inc
    maxx=maxx+(maxx-minx)*inc
    miny=miny-(maxy-miny)*inc
    maxy=maxy+(maxy-miny)*inc




    for i,nsc in enumerate(nscores):
        draw(tq,ty,nsc,border,minx=minx,maxx=maxx,miny=miny,maxy=maxy, hist=hist and not i)






