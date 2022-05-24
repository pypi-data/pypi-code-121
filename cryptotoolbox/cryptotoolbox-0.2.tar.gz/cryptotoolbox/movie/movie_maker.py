#!/usr/bin/env python
# coding: utf-8

import matplotlib.pyplot as plt
import matplotlib.animation as manimation
import seaborn as sns
import numpy as np

def createCorrelationBarMovie(rolled_sharpe, saving_path):
    FFMpegWriter = manimation.writers['ffmpeg']
    metadata = dict(title='Movie Test', artist='Matplotlib',
                    comment='Movie support!')
    writer = FFMpegWriter(fps=15, metadata=metadata)
    fig = plt.figure()
    ax = fig.gca()
    with writer.saving(fig, saving_path, 100):
        for row in rolled_sharpe.iterrows():
            ax.clear()
            plt.ylim(-1, 1)
            histo_values = row[1].to_frame()
            histo_values.columns = ['CORR']
            histo_values['STRAT'] = histo_values.index
            histo_values.plot.bar(x='STRAT', y='CORR', rot=90, ax = ax, title = str(row[0]), legend = None)
            writer.grab_frame()

def createCorrelationMovie(stacked_rolled_sharpe, saving_path, fillna = True):
    stacked_rolled_sharpe.index.names = ['ts', 'strat']
    FFMpegWriter = manimation.writers['ffmpeg']
    metadata = dict(title='Movie Test', artist='Matplotlib',
                    comment='Movie support!')
    writer = FFMpegWriter(fps=15, metadata=metadata)
    fig, ax = plt.subplots()

    with writer.saving(fig, saving_path, 100):
        for date in stacked_rolled_sharpe.index.get_level_values('ts').unique():
            ax.clear()
            corr = stacked_rolled_sharpe.loc[date]
            if fillna:
                corr = corr.fillna(0.)

            im = ax.imshow(corr.values)

            # We want to show all ticks...
            ax.set_xticks(np.arange(len(corr.columns)))
            ax.set_yticks(np.arange(len(corr.index)))
            # ... and label them with the respective list entries
            ax.set_xticklabels(corr.columns)
            ax.set_yticklabels(corr.index)

            # Rotate the tick labels and set their alignment.
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                     rotation_mode="anchor")

            # Loop over data dimensions and create text annotations.
            for i in range(len(corr.columns)):
                for j in range(len(corr.index)):
                    text = ax.text(j, i, corr.values[i, j],
                                   ha="center", va="center", color="w")

            ax.set_title("NPX crypto strats correlation")
            fig.tight_layout()
            plt.show()
            writer.grab_frame()
