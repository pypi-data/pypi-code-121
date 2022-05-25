import re
import random
from functools import partial
import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt
import matplotlib as mpl
from dl2050utils.core import listify, camel2snake
from dl2050nn.etc import *


def randn(n): return random.randint(0,n)


class Callback():
    _order=0
    def set_learner(self, learner): self.learner=learner
    def __getattr__(self, k): return getattr(self.learner, k)

    @property
    def name(self):
        name = re.sub(r'Callback$', '', self.__class__.__name__)
        return camel2snake(name or 'callback')

    def __call__(self, cb_name):
        f = getattr(self, cb_name, None)
        if f and f(): return True
        return False


class CancelTrainException(Exception): pass
class CancelEpochException(Exception): pass
class CancelBatchException(Exception): pass


class TestCallback(Callback):
    _order=1
    def after_step(self):
        print(self.iter)
        if self.iter>=5: raise CancelTrainException()


class Recorder(Callback):
    def __init__(self): self.begin_fit()
    def begin_fit(self): self.lrs, self.losses1, self.losses2 = [], [], []

    def after_batch(self):
        if self.train: self.losses1.append(self.loss.detach().cpu())
        else: self.losses2.append(self.loss.detach().cpu())
        if not self.train: return
        if not hasattr(self.optf, 'hypers'): # Pytorch optimizer
            self.lrs.append(self.optf.param_groups[-1]['lr'])
        else: # NN2 optimizer
            self.lrs.append(self.optf.hypers[-1]['lr'])

    def plot_lr(self): plt.figure(); plt.plot(self.lrs); plt.show(); plt.pause(.001)
    def plot_loss1(self): plt.figure(); plt.plot(self.losses1); plt.show(); plt.pause(.001)
    def plot_loss2(self): plt.figure(); plt.plot(self.losses2); plt.show(); plt.pause(.001)


class LR_Find(Callback):
    def __init__(self, max_iter=100, min_lr=1e-6, max_lr=1e1):
        self.max_iter, self.min_lr, self.max_lr = max_iter, min_lr, max_lr
        self.best_loss, self.n = 1e9, 0

    def begin_epoch(self):
        print(f'LR Find: bs={self.data.bs}, n_batches={len(self.data.dl1)}')
        
    def begin_batch(self):
        if not self.train: return
        pos = self.n/self.max_iter
        lr = self.min_lr * (self.max_lr/self.min_lr) ** pos
        self.n += 1
        if not hasattr(self.optf, 'hypers'): # Pytorch optimizer
            for pg in self.optf.param_groups: pg['lr'] = lr
        else: # NN2 optimizer
            for pg in self.optf.hypers: pg['lr'] = lr
            
    def after_step(self):
        if self.n>=self.max_iter or self.loss>self.best_loss*10:
            print('Optimal lr found')
            raise CancelTrainException()
        loss = self.loss.detach().cpu().item()
        if loss < self.best_loss: self.best_loss = loss

    def after_cancel_train(self): self.plot()
    # def after_fit(self): self.plot()

    def plot(self):
        _ = plt.figure(figsize=(5, 3))
        plt.xscale('log')
        plt.plot(self.recorder.lrs[:-1], self.recorder.losses1[:-1])
        plt.show()
        plt.pause(.001)


class BalanceScheduler(Callback):
    def __init__(self, p=1., balance_epochs=None): self.p0, self.p, self.balance_epochs = p, p, balance_epochs
    def begin_epoch(self):
        if not self.train: return
        if self.ep == 0:
            self.data.dl1.set_balance(self.p)
            return
        if self.balance_epochs is None: return
        if self.ep>self.balance_epochs: return
        self.p = self.p0*(1-self.ep/self.balance_epochs)
        self.data.dl1.set_balance(self.p)


class TabMix(Callback):
    def __init__(self, p0=.05, p1=.05): self.p0, self.p1 = p0, p1
    def begin_batch(self):
        if not self.train: return
        n0, n1 = self.x.size(0), self.x.size(1)
        mask0 = torch.randint(n0, (int(self.p0*n0/2),))
        for i in mask0:
            mask1 = torch.randint(n1, (int(self.p1*n1),))
            tmp = self.x[i][mask1].clone()
            self.x[i][mask1] = self.x[n0-i-1][mask1]
            self.x[n0-i-1][mask1] = tmp
