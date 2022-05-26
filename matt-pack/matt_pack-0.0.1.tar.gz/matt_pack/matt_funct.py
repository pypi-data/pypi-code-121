import pandas as pd
import numpy as np
import scipy as sc
from scipy import stats as st



def genralize_mat(mat):
    m1 = mat / mat.sum(axis=1)
    m2 = mat / mat.sum()
    G_mat = [[gm([m1.loc[i][j], m2.loc[j][i]]) for i in m1.index] for j in m1.columns]
    return np.linalg.det(G_mat)




hm = st.mstats.hmean
gm = st.mstats.gmean


def ratio_mat(mat, average):
    m1 = mat / mat.sum(axis=1)
    m2 = mat / mat.sum()

    return [[average([m1.loc[i][j], m2.loc[j][i]])
             for i in m1.index] for j in m1.columns]


def genralize_f1(mat, average_2=hm):
    H_mat = ratio_mat(mat, hm)
    return average_2([H_mat[i][i] for i in range(len(mat))])


def genralize_mat(mat):
    G_mat = ratio_mat(mat, gm)
    return np.linalg.det(G_mat)



if __name__ =='__main__':
    a = [[5, 6, 2], [2, 8, 11], [8, 2, 10]]
    mat = pd.DataFrame(data=a)
    print("genral_val=",genralize_mat(mat))
    print("For Indeity " ,genralize_mat(pd.DataFrame(data=np.identity(4))))
    print("Gen f1=",genralize_f1(mat))
    print("gen F1 iDENT=",genralize_f1(pd.DataFrame(data=
                                    np.identity(4))))
    print ("worked on")
