# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 11:29:42 2020

@author: Mojtaba Sardarmehni
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = "14"


class Flow:
    def __init__(self, CommonData, ZeroFlow=False, **kwargs):
        self._CommonData = CommonData
        self._PFAS_Index = CommonData.PFAS_Index
        if not ZeroFlow:
            self.mass = None        # kg
            self.ts = None          # kg
            self.moist = None       # kg
            self.C = None           # kg
            self.bulk_dens = None   # kg/m3
            self.PFAS = pd.Series(data=[0.0 for i in self._PFAS_Index], index=self._PFAS_Index, dtype=float)  # μg
        else:
            self.mass = 0        # kg
            self.ts = 0          # kg
            self.moist = 0       # kg
            self.C = 0           # kg
            self.bulk_dens = 0   # kg/m3
            self.PFAS = pd.Series(data=[0.0 for i in self._PFAS_Index], index=self._PFAS_Index, dtype=float)  # μg

        for key, value in kwargs.items():
            setattr(self, key, value)

    def set_flow(self, mass_flow, ts_cont=None, C_cont=None, PFAS_cont=None, bulk_dens=None, **kwargs):
        self.mass = mass_flow
        self.ts = mass_flow * ts_cont if not pd.isna(ts_cont) else None
        self.moist = mass_flow * (1 - ts_cont) if not pd.isna(ts_cont) else None
        self.C = self.ts * C_cont if (not pd.isna(ts_cont) and not pd.isna(C_cont)) else None
        self.bulk_dens = bulk_dens if not pd.isna(bulk_dens) else None

        if PFAS_cont:
            self.PFAS = pd.Series([PFAS_cont[i] * self.mass for i in self._PFAS_Index], index=self._PFAS_Index, dtype=float)

        for key, value in kwargs.items():
            if key == 'VS_cont':
                setattr(self, 'VS', value * self.ts)
                setattr(self, 'Ash', (1 - value) * self.ts)

            if key == 'Ash_cont':
                setattr(self, 'VS', (1 - value) * self.ts)
                setattr(self, 'Ash', value * self.ts)

            elif key == 'vol_flow':
                setattr(self, 'vol', value)
            elif key == 'density':
                setattr(self, 'vol', self.mass / value)
            else:
                setattr(self, key, value)

    def get_Ccont(self):
        return (self.C / self.ts)

    def get_TScont(self):
        return (self.ts / self.mass)

    def get_Moistcont(self):
        return (self.moist / self.mass)

    def get_PFAScont(self):
        if self.mass == 0 and self.vol > 0:
            return (self.PFAS / self.vol)
        return (self.PFAS / self.mass)

    def set_FlowType(self, FlowType):
        self.FlowType = FlowType

    def report(self):
        report = pd.DataFrame(columns=['Parameter', 'Unit', 'Amount'])
        report.loc[0] = ['Mass flow', 'kg', self.mass]
        report.loc[1] = ['Solids flow', 'kg', self.ts]
        report.loc[2] = ['Moisture flow', 'kg', self.moist]
        i = 3
        if 'vol' in self.__dict__:
            report.loc[i] = ['Volume flow', 'L', self.vol]
            i += 1
        if 'VS' in self.__dict__:
            report.loc[i] = ['VS flow', 'kg', self.VS]
            i += 1
        report.loc[i] = ['Carbon flow', 'kg', self.C]
        i += 1
        for j in self.PFAS.index:
            report.loc[i] = [j, 'μg', self.PFAS[j]]
            i += 1
        return(report)

    def plot_PFAS(self, kind='pie', ax=None, **kwargs):
        if kind == 'pie':
            figsize = kwargs.get('figsize') if kwargs.get('figsize') else (5, 5)
        else:
            figsize = kwargs.get('figsize') if kwargs.get('figsize') else (10, 4)
        fontsize = kwargs.get('fontsize') if kwargs.get('fontsize') else 14
        title = kwargs.get('title') if kwargs.get('title') else None

        if ax is None and kind != 'mix':
            fig, ax = plt.subplots(1, 1, figsize=figsize)
        elif ax is None and kind == 'mix':
            fig, (ax, ax2) = plt.subplots(1, 2, figsize=figsize, gridspec_kw={'width_ratios': [6, 1]})

        # https://stackoverflow.com/questions/46692643/
        def autopct(pct):
            return ('%1.f%%' % pct) if pct > 5 else ''

        if kind == 'pie':
            cm = plt.get_cmap('tab20')
            n = len(self._PFAS_Index)
            ax.pie(x=self.PFAS,
                   autopct=autopct,
                   textprops=dict(color="w"),
                   colors=cm(np.arange(n) / n))
            ax.legend(self.PFAS.index,
                      bbox_to_anchor=(1, 0, 0.5, 1),
                      loc='center left', ncol=2)
        elif kind == 'bar':
            ax.bar(x=self.PFAS.index,
                   height=self.PFAS)
            ax.set_ylabel(f'μg in {self.mass} kg')
            if 'rotation' in kwargs:
                ax.tick_params(axis='x', rotation=kwargs.get('rotation'))
        elif kind == 'mix':
            cm = plt.get_cmap('tab20')
            n = len(self.PFAS.index)
            colors = cm(np.arange(n) / n)

            ax.bar(x=self.PFAS.index, height=self.PFAS, color=colors)
            ax.tick_params(axis='x', rotation=45)

            pd.DataFrame(self.PFAS / self.PFAS.sum() * 100).T.plot.bar(stacked=True, ax=ax2, color=colors)
            ax2.get_legend().remove()

            def format_lable(values):
                lables = []
                for x in values:
                    lables.append(autopct(x))
                return lables

            for c in ax2.containers:
                ax2.bar_label(c, label_type='center', labels=format_lable(c.datavalues), color='w',
                              font={'weight': 'bold', 'size': 14})

            ax2.xaxis.set_ticklabels(['PFAS'])
            ax2.tick_params(axis='x', rotation=0)

            ax.set_ylabel('Mass of PFAS (μg)')
            ax2.set_ylabel('Percent of total PFAS (%)')

            fig.tight_layout()
            ax.set_title(title, fontsize=fontsize)
            return fig, (ax, ax2)

        ax.set_title(title, fontsize=fontsize)
        return fig
