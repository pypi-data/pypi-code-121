import time
import os
import numpy as np
import pandas as pd
import pickle
import gc
import torch
import matplotlib.pyplot as plt
from IPython.display import display
from dl2050utils.ju import disablePrint, enablePrint, force_print
from dl2050nn.etc import *
from dl2050nn.cbs import Callback
from dl2050nn.metrics import *


def key_metric(learner): return 4+len(learner.metrics)

def metrics_str(metrics):
    if not len(metrics): return ''
    s = ' M: ['
    for v in metrics: s += f'{v:.4f}, '
    s = s[:-2] + ']'
    return s


def log_str(ep, t, loss1, loss2, metrics1, metrics2, new_best, valid=False):
    s = f'Ep: {ep}\tT: {t2s(t)}:{int(t)%60:02d}\tL1: {loss1:.4f} '
    s += metrics_str(metrics1)
    if valid:
        s += f'\tL2: {loss2:.4f} '
        s += metrics_str(metrics2)
    if new_best: s += ' *'
    return s


def printProgressBar(i, n, prefix, w=50):
    p = float(i+1)/n
    filled = int(w*p)
    s = f'\033[31m{"█"*filled}\033[37m{"█"*(w-filled)}\033[0m'
    if p<1.: print(f'\r{prefix} | {s} | {100*p:.1f}%', end='\r')
    else: print(f'\r{" "*(w+len(prefix)+25)}', end='\r')


def plot_init(x_min, x_max):
    plt.ion()
    fig = plt.figure(figsize=(12, 3))
    ax = fig.add_axes([0.2, 0.2, .8, 0.8])
    ax.xaxis.set_ticks(np.arange(x_min, x_max, max(1,int((x_max-x_min))//10)))
    ax.yaxis.set_ticks(np.arange(0., 2.5, .5))
    ax.plot([], [], [], [],)
    return fig, ax


def plot_update(fig, ax, x, y1, y2):
    ax.lines[0].set_xdata(x), ax.lines[0].set_ydata(y1)
    if y2 is not None: ax.lines[1].set_xdata(x), ax.lines[1].set_ydata(y2)
    ax.relim()
    ax.autoscale()
    fig.canvas.draw()


def plot_df(df):
    fig = plt.figure(figsize=(12, 3))
    ax1, ax2 = fig.add_subplot(121), fig.add_subplot(122)
    df.plot(x='Epoch', y=['Loss_1', 'Loss_2'], ax=ax1)
    df.plot(x='Epoch', y=['accuracy_1', 'accuracy_2'], ax=ax2)
    plt.show()
    time.sleep(.01)


class LoggerCallback(Callback):
    
    def __init__(self, mode=None, file_=False, maximize=True, ep_stats=True):
        self.file, self.maximize, self.ep_stats = file_, maximize, ep_stats
        self.mode = ('ipynb' if in_ipynb() else 'console') if mode is None else mode
        if file_:
            fname, dirname = get_log_fname(self.path)
            if not os.path.exists(dirname): os.makedirs(dirname)
            self.logf = open(fname, 'w', 1)
        self.best = 0.0 if self.maximize else 1e9
        self.results = []
        self.y_ep, self.y2_ep, self.stats_1, self.stats_2, self.t0, self.t1 = None, None, None, None, 0, 0
        self.df, self.df_best = None, None
        print(f'Logging to {self.mode}')
        if self.file: print(f'Logging to file: {self.fname}')
        pd.options.display.float_format = '{:,.4f}'.format
        
    def reset_stats(self):
        self.y_ep = torch.tensor([]).long() if self.data.clsf else torch.tensor([]).float()
        self.y2_ep = torch.tensor([]).float()
        self.loss_t, self.n, self.metrics_v = 0., 0, [0.]*len(self.metrics)
        
    def stats(self):
        if self.y_ep is None or self.y2_ep is None: return [0.]*(1+len(self.metrics))
        self.metrics_v = [m(self.y2_ep, self.y_ep) for m in self.metrics]
        return [self.loss_t/self.n] + self.metrics_v
    
    def accumulate(self):
        k = self.x.shape[0]
        loss = self.loss.detach().cpu().item()
        self.loss_t += loss*k
        self.n += k
        self.y_ep = torch.cat((self.y_ep, self.y.detach().cpu()))
        self.y2_ep = torch.cat((self.y2_ep, self.y2.detach().cpu()))

    def update_historic(self):
        row = [self.ep, self.t2] + [self.loss1] + [e for e in self.metrics1] + [self.loss2] + [e for e in self.metrics2]
        self.results.append(row)
        self.df = pd.DataFrame(self.results, columns=self.cols)
       
    def log_epoch(self):
        if self.mode == 'ipynb' and self._plot and self.eps > 1:
            x = self.df['Epoch'].values
            y = self.df[['Loss_1', 'Loss_2']].values
            y0, y1 = y[:,0], y[:,1] if self.data.dl2 is not None else None
            plot_update(self.fig, self.ax, x, y0, y1)
        s = log_str(self.ep, self.t2, self.loss1, self.loss2, self.metrics1, self.metrics2, self.new_best, valid=self.data.dl2 is not None)
        print(s)

    def begin_fit(self):
        if self.data.dl2 is None: self.best = 1e9
        if self.mode == 'ipynb' and self._plot and self.eps > 1: self.fig, self.ax = plot_init(0, self.eps)
        self.cols = ['Epoch', 'Time', 'Loss_1'] + [f'{e.__name__}_1' for e in self.metrics] + ['Loss_2'] + [f'{e.__name__}_2' for e in self.metrics]
        
    def begin_epoch(self):
        self.t0 = time.time()
        self.reset_stats()
        
    def begin_validate(self):
        self.t1 = time.time() - self.t0
        self.stats_1 = [v for v in self.stats()]
        self.reset_stats()
            
    def after_loss(self):
        with torch.no_grad(): self.accumulate()
        
    def after_batch(self):
        printProgressBar(self.iter, self.iters, f'Ep: {self.ep:d} {"train" if self.train else "eval"}:')

    def after_epoch(self):
        self.t2 = time.time() - self.t0 if self.t0 is not None else time.time()
        self.stats_2 = [v for v in self.stats()] if self.data.dl2 is not None else [0]*len(self.stats_1)
        self.loss1, self.loss2 = self.stats_1[0], self.stats_2[0] if self.data.dl2 is not None else 0.
        self.metrics1, self.metrics2 = [v for v in self.stats_1[1:]], [v for v in self.stats_2[1:]]
        loss_metric = not len(self.metrics) or self.data.dl2 is None
        self.new_best = False
        if loss_metric:
            if self.data.dl2 is None:
                self.new_best = self.loss1 < self.best
                if self.new_best: self.best = self.loss1
            else:
                self.new_best = self.loss2 < self.best
                if self.new_best: self.best = self.loss2
        else:
            self.new_best = (self.maximize and self.metrics2[0]>self.best) or (not self.maximize and self.metrics2[0]<self.best)
            if self.new_best: self.best = self.metrics2[0]
        self.update_historic()
        self.log_epoch()
        if self.new_best:
            self.df_best = self.df[self.df['Epoch']==self.ep]
            if self._save: self.save()
        
    def after_fit(self):
        print(f'\nBest: {self.best:.4f}')
        plt.ioff()

    def show_best(self): display(self.df_best)

    def plot_loss1_metric2(self):
        if self.df is None: return
        col_ids = [2, 4+len(self.metrics)]
        z = self.df.iloc[:,col_ids].values
        plot(*list(zip(*z))); plt.show(); time.sleep(.01)


class Runner:
    def __init__(self, path, data, get_learner, nruns=10, eps=10, name='Runner', desc='', load=False):
        self.get_learner, self.data = get_learner, data
        self.nruns, self.eps, self.name, self.desc = nruns, eps, name, desc
        if not Path(f'{path}/runners').exists(): Path(f'{path}/runners').mkdir()
        self.fname = f'{path}/runners/{name}'
        self.learner, self.df, self.best = None, None, 0.
        if load: self.load()

    def __call__(self, mute=True):
        self.best, self.best_file = 0., None
        if mute: disablePrint()
        for i in range(self.nruns):
            force_print(f'\rRun {i}')
            learner = self.get_learner(self.data, name= f'{self.name}_{i}', plot=False)
            self.learner = learner
            learner.fit(self.eps)
            learner.load(mute=True)
            df1 = learner.logger.df_best
            df1['Best'] = ''
            self.df = df1.copy() if self.df is None else pd.concat((self.df,df1),ignore_index=True)
            if learner.logger.best > self.best:
                self.best, self.best_file = learner.logger.best, f'{self.name}_{i}'
                print(f'New best: {self.best:.4f}')
                display(self.df.iloc[[-1]])
            self.df['Best'] = ''
            self.df.loc[self.df.iloc[:,key_metric(learner)]==self.best, 'Best'] = '*'
            self.save()
            learner.close()
            del learner
            gc.collect()
        self.save()
        print(f'\nBest file: {self.best_file}')
        display(self.df)
        enablePrint()

    def save(self):
        meta = {'desc': self.desc, 'best': self.best, 'best_file': self.best_file}
        pickle.dump(meta, open(self.fname+'.pickle', 'wb'))
        self.df.to_csv(self.fname+'.csv', index=False)

    def load(self):
        p_pickle, p_csv = Path(f'{self.fname}.pickle'), Path(f'{self.fname}.csv')
        if not p_pickle.exists() or not p_csv.exists(): return
        meta = pickle.load(open(self.fname+'.pickle', 'rb'))
        if not 'cols' in meta or not 'best' in meta or not 'best_file' in meta: return
        print(f'Loaded from file {self.fname}: {meta}')
        self.desc, self.best, self.best_file = meta['desc'], meta['best'], meta['best_file']
        self.df = pd.read_csv(self.fname+'.csv')
        self.df['Best'] = self.df['Best'].fillna('')

    def df_best(self):
        if self.learner is None: return None
        return self.df[self.df.iloc[:,key_metric(self.learner)]==self.best].iloc[[0]]
