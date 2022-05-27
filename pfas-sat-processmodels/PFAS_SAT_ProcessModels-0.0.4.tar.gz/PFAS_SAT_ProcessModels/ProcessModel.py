# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 21:31:49 2020

@author: msmsa
"""
from abc import ABC, abstractmethod
from PFAS_SAT_InputData import CommonData
from .Inventory import Inventory
from matplotlib.sankey import Sankey
import matplotlib.pyplot as plt
import pandas as pd
from copy import deepcopy


class ProcessModel(ABC):
    def __init__(self, CommonDataObject, InventoryObject):
        if CommonDataObject:
            self.CommonData = CommonDataObject
        else:
            self.CommonData = CommonData()

        if InventoryObject:
            self.Inventory = InventoryObject
        else:
            self.Inventory = Inventory(CommonDataObject=self.CommonData)

    @property
    @abstractmethod
    def ProductsType(self):
        pass

    @abstractmethod
    def calc(self):
        pass

    @abstractmethod
    def setup_MC(self, seed=None):
        pass

    @abstractmethod
    def MC_Next(self):
        pass

    @abstractmethod
    def report(self):
        pass

    def plot_sankey(self, **kwargs):
        Data = self.report().sum().sort_values(ascending=False)
        Total = sum(self.Inc_flow.PFAS)
        flows = [1]
        labels = ['Incoming PFAS']
        orientations = [0]
        pathlengths = [0.7]
        for j, i in enumerate(Data.index):
            flows.append(-round(Data[i] / Total, 4))
            labels.append(i.replace(' ', '\n'))
            if j in [0, 1, 2]:
                pathlengths.append(0.35)
            elif j in [3, 4]:
                pathlengths.append(0.8)
            else:
                pathlengths.append(1.2)

            if j == 0:
                Or = 0
            elif j % 2 == 1:
                Or = -1
            else:
                Or = 1
            orientations.append(Or)

        margin = 1.4 if 'margin' not in kwargs else kwargs['margin']
        offset = 0.25 if 'offset' not in kwargs else kwargs['offset']
        gap = 0.7 if 'gap' not in kwargs else kwargs['gap']

        Sankey(flows=flows, labels=labels, alpha=0.5, orientations=orientations,
               pathlengths=pathlengths, gap=gap, offset=offset, margin=margin).finish()
        plt.axis('off')

    def plot_sankey_report(self, **kwargs):
        margin = 1.4 if 'margin' not in kwargs else kwargs['margin']
        offset = 0.25 if 'offset' not in kwargs else kwargs['offset']
        gap = 0.7 if 'gap' not in kwargs else kwargs['gap']
        figsize = (12, 5) if 'figsize' not in kwargs else kwargs['figsize']

        compound_1 = "PFHxA"
        compound_2 = "PFOA"
        compound_3 = "PFOS"

        if 'sorted_index' not in kwargs:
            sorted_index = self.report().loc[compound_1].sort_values(ascending=False).index
        else:
            sorted_index = kwargs['sorted_index']

        def _plot_sankey_compound(compound, ax):
            Data = self.report().loc[compound]
            Total = self.Inc_flow.PFAS[compound]
            flows = [1]
            labels = [compound]
            orientations = [0]
            pathlengths = [0.7]
            for j, i in enumerate(sorted_index):
                if float('%.2g' % (Data[i] / Total)) >= 0.1:
                    flows.append(-float('%.2g' % (Data[i] / Total)))
                else:
                    flows.append(-float('%.1g' % (Data[i] / Total)))
                # Revising the label format
                lenn = 0
                label = ''
                for d in i.split(' '):
                    lenn += len(d)
                    if lenn > 10:
                        label += '\n' + d
                        lenn = 0
                    else:
                        label += ' ' + d
                labels.append(label)
                if j in [0, 1, 2]:
                    pathlengths.append(0.35)
                elif j in [3, 4]:
                    pathlengths.append(0.8)
                else:
                    pathlengths.append(1.2)

                if j == 0:
                    Or = 0
                elif j % 2 == 1:
                    Or = -1
                else:
                    Or = 1
                orientations.append(Or)
            Sankey(ax=ax, flows=flows, labels=labels, alpha=0.5, orientations=orientations,
                   pathlengths=pathlengths, gap=gap, offset=offset, margin=margin).finish()
            ax.axis('off')

        fig = plt.figure(figsize=figsize)
        ax1 = fig.add_subplot(1, 3, 1, xticks=[], yticks=[],
                              title=compound_1)
        ax2 = fig.add_subplot(1, 3, 2, xticks=[], yticks=[],
                              title=compound_2)
        ax3 = fig.add_subplot(1, 3, 3, xticks=[], yticks=[],
                              title=compound_3)

        _plot_sankey_compound(compound_1, ax1)
        _plot_sankey_compound(compound_2, ax2)
        _plot_sankey_compound(compound_3, ax3)

        return fig

    def SA(self, inputflow, stream, n, figsize):
        self.setup_MC()
        for i in range(100):
            inpt = self.MC_Next()
            self.calc(inputflow)
            res = self.report().loc['PFOA']
            if i == 0:
                columns = []
                for j in inpt:
                    columns.append(j[0])
                for j in res.index:
                    columns.append(j)
                output = pd.DataFrame(columns=columns, dtype=float)
            row = []
            for j in inpt:
                row.append(j[1])
            for j in res:
                row.append(j)
            output.loc[i] = row

        corr_data = output.corr(method='pearson')

        # ploting the DataFrame
        for x in res.index:
            columns.remove(x)

        col = deepcopy(columns)

        for j in col:
            for x in self.CommonData.PFAS_Index:
                if x in str(j):
                    try:
                        columns.remove(j)
                    except Exception:
                        pass

        corr_data_plot = corr_data[stream][columns]
        sorted_corr = corr_data_plot.abs().sort_values(ascending=False)

        if len(sorted_corr.index) <= n:
            index = sorted_corr.index
        else:
            index = sorted_corr.index[0:n]
        fig = plt.figure(figsize=figsize)
        ax_plot_corr = fig.add_subplot(1, 1, 1)
        ax_plot_corr = corr_data_plot[index].plot(kind='barh', ax=ax_plot_corr)
        # set lables
        ax_plot_corr.set_xlabel('Correlation with mass of PFOA in {}'.format(stream), fontsize=18)
        ax_plot_corr.set_xlim(-1, 1)
        ax_plot_corr.tick_params(axis='both', which='major', labelsize=18, rotation='auto')
        ax_plot_corr.tick_params(axis='both', which='minor', labelsize=16, rotation='auto')
        return(output)
