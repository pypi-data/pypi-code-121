"""Main module."""

"""
This module implements the censored ROC curve estimation.
Author: Yury Moskaltsov from plaindata.ai
"""

__author__ = "Yury Moskaltsov, plaindata.ai"
__email__ = "yury-m@hotmail.com.com"
__status__ = "planning"


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from scipy.stats import norm
from statsmodels.sandbox.nonparametric import kernels
from statsmodels.nonparametric.bandwidths import bw_normal_reference
import os


df_surv = pd.read_csv('/Users/yurymoskaltsov/Tresors/survival_tools/data/survival_df.csv')
df_test = df_surv.iloc[:50,:]
Dt =  pd.read_csv('/Users/yurymoskaltsov/Tresors/survival_tools/data/Csurv_res.csv')

class cenROC():

    def __init__(self, Y, M, censor,t,
                 U=None, h=None, bw='NR', method="tra", ktype="normal",
                 ktype1="normal", B=0, alpha=0.05, plot="TRUE"):

        self.Y = Y
        self.M = M
        self.censor = censor
        self.t = t
        self.U = U
        self.h = h
        self.bw = bw
        self.method = method
        self.ktype = ktype
        self.ktype1 = ktype1
        self.B = B
        self.alpha = alpha
        self.plot = plot

    def kfunc(self,ktype,difmat):

        if ktype == 'normal':

            estim = norm.cdf(difmat)

        else:

            estim = difmat.copy()
            low = (difmat <= -1)
            up = (difmat >= 1)
            btwn = (difmat > -1) & (difmat < 1)
            estim[low] = 0
            estim[up] = 1
            X = estim[btwn]


            if ktype == 'epanechnikov':

                estim[btwn] = (0.75 * X * (1 - (X**2) / 3) + 0.5)

            elif ktype == 'biweight':

                estim[btwn] = (15/16) * X - (5/8) * (X**3) + (3/16) * (X**5) + 0.5

            elif ktype == 'triweight':

                estim[btwn] = (35/32) * X - (35/32) * X**3 + (21/32) * X**5 - (5/32) * X**7 + 0.5

        return estim

    def RocFun(self,U, D, M, method, ktype=None, bw = "NR"):

        oM = np.argsort(M)
        D = np.array(D).ravel()
        D = np.array(D[oM]).ravel()
        nD = len(D)
        sumD = sum(D)
        Z = 1 - np.cumsum(1 - D) / (nD - sumD)
        AUC = sum(D * Z) / sumD

        assert ktype in ['normal', 'epanechnikov', 'biweight', 'triweight'], \
            ''' ktype should be on of the following: ['normal', 'epanechnikov', 'biweight', 'triweight'] '''

        assert method in ['emp', 'untra', 'tra'], \
            ''' method should be on of the following: ['emp', 'untra', 'tra'] '''

        assert bw in ['NR'] or type(bw)==float or type(bw)==int, \
            ''' bw should be a number or one of the following: ['NR'] '''

        if method == 'emp':

            difmat = np.round(np.subtract.outer(U, Z),8)
            result = difmat >= 0
            ROC1 = result * D
            ROC = np.round((np.sum(ROC1, axis=1)) / sumD,8)
            bw1 = np.nan

        if ktype == 'normal':

            kernel = kernels.Gaussian()

        elif ktype == 'epanechnikov':

            kernel = kernels.Epanechnikov()

        elif ktype == 'biweight':

            kernel = kernels.Biweight()

        elif ktype == 'triweight':

            kernel = kernels.Triweight()


        if method == 'untra':

            Zt = Z
            Ut = U
            Ztt = Z[D!=0]
            wt = D[D!=0]

            try:

                float(bw)
                bw1=bw

            except ValueError:

                if bw == 'NR':

                    bw1 = bw_normal_reference(Ztt,kernel=kernel)

            difmat = np.round(np.subtract.outer(Ut, Ztt),8) / bw1
            result = self.kfunc(ktype=ktype, difmat=difmat)
            w = wt/sum(wt)
            ROC1 = result * w
            ROC = np.round((np.sum(ROC1, axis=1)),8)

        elif method == 'tra':

            mul = nD / (nD + 1)
            Zt = norm.ppf(mul * Z + (1 / nD ** 2))
            Ut = norm.ppf(mul * U + (1 / nD ** 2))
            Ztt = Zt[D != 0]
            wt = D[D != 0]

            if type(bw) == float or type(bw) == int:

                bw1=bw

            else:

                if bw == 'NR':

                    bw1 = bw_normal_reference(Ztt,kernel=kernel)


            difmat = np.round(np.subtract.outer(Ut, Ztt), 8) / bw1
            result = self.kfunc(ktype=ktype, difmat=difmat)
            w = wt / sum(wt)
            ROC1 = result * w
            ROC = np.round((np.sum(ROC1, axis=1)), 8)


        return ROC, AUC, bw1


    def cenROC(self):

        Y = self.Y
        M = self.M
        censor = self.censor
        t = self.t
        U = self.U
        h = self.h
        bw = self.bw
        method = self.method
        ktype = self.ktype
        ktype1 = self.ktype1
        B = self.B
        alpha = self.alpha
        plot = self.plot

        if U == None:

            U = np.linspace(0,1,151)

        try:

            ''' Do the try for each '''

            Y.astype(float)
            M.astype(float)
            censor.astype(float)

        except ValueError:

            print("Error! all vectors Y, M and censor should be specified and numeric")


        ROC, AUC, bw1 = self.RocFun(U=np.array(U), D=censor, M=M, bw=bw, method = method, ktype=ktype)

        AUCc = 1- AUC


        if B>0:

            data = pd.DataFrame({'Y':Y, 'M':M, 'cen':censor})
            aucb = []
            rocb = np.empty((len(U),B))
            rocb[:] = np.nan


            for i in range(B):


                bootsample = np.random.randint(0,data.shape[0]-1,data.shape[0])
                dat = data.iloc[bootsample,:]
                ROC_b, AUC_b, bw1_b = self.RocFun(U = U, D = dat['cen'], M = dat['M'], method = method,
                          bw = bw, ktype = ktype)
                aucb.append(1-AUC_b)
                rocb[:,i] = ROC_b

            SP = np.quantile(aucb, [alpha/2, 1 - alpha/2])

            AUC = pd.DataFrame(
                {'AUC': [np.round(np.mean(aucb), 4)],#'AUC': [np.round(AUCc, 4)],
                 'sd': [np.round(np.std(aucb,ddof=1), 4)],
                 'LCL': [np.round(SP[0], 4)],
                 'UCL': [np.round(SP[1], 4)]

                 })

            qroc = np.apply_along_axis(np.quantile,1,rocb,[alpha/2, 1 - alpha/2])

            ROC = pd.DataFrame({'ROC': np.apply_along_axis(np.mean,1,rocb), 'LCL': qroc[:, 0], 'UCL': qroc[:, 1]})



        else:

            AUC = pd.DataFrame(
                {'AUC': [np.round(AUCc, 4)],
                 'sd': [np.nan],
                 'LCL': [np.nan],
                 'UCL': [np.nan]

                 }

            )


        if plot == 'TRUE':

            if B == 0:

                x = np.concatenate((np.array([0]), U, np.array([1])))
                y = np.concatenate((np.array([0]), ROC, np.array([1])))
                plt.plot(x, y, linewidth=1.5, color='blue')
                plt.plot([0, 1], [0, 1], color='black', linewidth=0.8)


            else:

                fig, ax = plt.subplots()

                x = np.concatenate((np.array([0]), U, np.array([1])))
                y = np.concatenate((np.array([0]), ROC['ROC'], np.array([1])))
                plt.plot(x, y, linewidth=1.5, color='blue')

                x_pol_1 = np.flip(np.concatenate((np.array([0]), U, np.array([1]))))
                x_pol_2 = np.concatenate((np.array([0]), U, np.array([1])))
                x_pol = np.concatenate((x_pol_1, x_pol_2))

                y_pol_1 = np.concatenate((np.array([0]), ROC['UCL'], np.array([1])))
                y_pol_2 = np.concatenate((np.array([0]), ROC['LCL'], np.array([1])))
                y_pol = np.concatenate((np.flip(y_pol_1), y_pol_2))

                coordinates_pol = np.array([x_pol, y_pol]).T

                p = Polygon(coordinates_pol,
                            facecolor='skyblue', edgecolor='red',
                            linestyle='--', alpha=0.5)

                ax.add_patch(p)

            plt.xlabel("False positive rate", color='blue')
            plt.ylabel("True positive rate", color='blue')
            plt.show()



        return AUC, ROC, U, censor, M, bw


# if __name__ == '__main__':

#     cenROC_test = cenROC(Y=df_test['pfs'], M=df_test['Density_CD8'], censor=df_test['cnsrpfs'],
#                          t=20, U=None, h=None, bw='NR', method="tra", B=5)

    # cenROC_test = cenROC_test.cenROC(Y=df_test['pfs'], M=df_test['Density_CD8'], censor=df_test['cnsrpfs'],
    #        t=20, U=None, h=None, bw='NR', method="tra",
    #        ktype="normal", ktype1="normal", B=3, alpha=0.05, plot="TRUE")


    # print(cenROC_test.cenROC())
#
    # pass
