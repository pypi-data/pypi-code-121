import math
from functools import partial
import torch
from torch import tensor
from dl2050utils.core import listify
import matplotlib.pyplot as plt
from dl2050nn.etc import *
from dl2050nn.cbs import *


def merge(os, dest, f):
    for o in os:
        for k,v in f(o).items():
            if k not in dest: dest[k] = v

def get_defaults(d): return getattr(d, '_defaults', {})


def get_p(epf, eps, cycle):
    p = math.floor(epf)/eps if cycle is None or cycle==0 else epf/cycle - math.floor(epf/cycle)
    if p>1.: p = p-math.floor(p)
    return p


def annealer(f):
    def _inner(start, end, cycle): return partial(f, start, end, cycle)
    return _inner

@annealer
def sched_no(start, end, cycle, epf, eps):  return start
@annealer
def sched_lin(start, end, cycle, epf, eps): return start+get_p(epf, eps, cycle)*(end-start)
@annealer
def sched_exp(start, end, cycle, epf, eps): return start*(end/start) ** get_p(epf, eps, cycle)
@annealer
def sched_cos(start, end, cycle, epf, eps): return start+(1+math.cos(math.pi*(1-get_p(epf, eps, cycle))))*(end-start)/2


def combine_scheds(pcts, scheds, cycle):
    assert sum(pcts) == 1.
    pcts = tensor([0] + listify(pcts))
    assert torch.all(pcts >= 0)
    pcts = torch.cumsum(pcts, 0)
    def _inner(epf, eps):
        pos = get_p(epf, eps, cycle)
        idx = (pos>=pcts).nonzero(as_tuple=False).max()
        if idx == len(pcts)-1: idx -= 1
        actual_pos = (pos-pcts[idx]) / (pcts[idx+1]-pcts[idx])
        return scheds[idx](actual_pos*cycle, eps)
    return _inner


def combine_scheds_mult(f1, f2):
    def _inner(epf, eps):
        return f1(epf, eps)*f2(epf, eps)
    return _inner


def sched_cycle(start, end, cycle=1., sched2=None, factor=.1):
    f1 = combine_scheds([0.3, 0.7], [sched_cos(start, end, cycle), sched_cos(end, start, cycle)], cycle)
    if sched2 is None: return f1
    return combine_scheds_mult(f1, sched2(1., factor, None))


class ParamScheduler(Callback):
    def __init__(self, pname, sched_funcs):
        self.pname, self.sched_funcs = pname, listify(sched_funcs)

    def plot(self, eps=4, label=None):
        fig = plt.figure(figsize=(5, 3))
        epf = torch.linspace(0.0,eps,100*eps)
        plt.plot(epf, [self.sched_funcs[0](e, eps) for e in epf], label=label)
        plt.show()
        plt.pause(.001)

    def begin_batch(self): 
        if not self.train: return
        # Pytorch optimizer
        if not hasattr(self.optf, 'hypers'):
            for pg in self.optf.param_groups: pg['lr'] = self.sched_funcs[0](self.epf, self.eps)
            return
        # NN2 optimizer
        fs = self.sched_funcs
        if len(fs)==1: fs = fs*len(self.optf.param_groups)
        for f,h in zip(fs,self.optf.hypers): h[self.pname] = f(self.epf, self.eps)


class Optimizer():
    def __init__(self, params, steppers=[], stats=None, **defaults):
        params = L(params)
        self.param_groups = L(L(p) for p in params) if isinstance(params[0], (L,list)) else L([params])
        self.steppers, self.stats = L(steppers), L(stats)
        merge(self.steppers, defaults, get_defaults)
        self.hypers = [{**defaults} for _ in self.param_groups]
        self.state = {}
        for p,_ in self.all_params():
            self.state[p] = {}
        
    def all_params(self):
        return [(p,hyper) for pg,hyper in zip(self.param_groups,self.hypers)
            for p in pg if p.grad is not None]
        
    def step(self):
        for p,hyper in self.all_params():
            for stat in self.stats:
                if p not in self.state: self.state[p] = {}
                self.state[p] = stat(self.state[p], p, **hyper)
            for step in self.steppers: step(p, **{**self.state[p], **hyper})

    def zero_grad(self):
        for p,_ in self.all_params():
            p.grad.detach_()
            p.grad.zero_()


# Stats

def average_grad(state, p, mom, dampening=False, **kwargs):
    "Keeps track of the avg grads of `p` in `state` with `mom`."
    if 'grad_avg' not in state: state['grad_avg'] = torch.zeros_like(p.grad.data)
    damp = 1-mom if dampening else 1.
    # state['grad_avg'].mul_(mom).add_(damp, p.grad.data) -> OLD DEPRECRATED
    state['grad_avg'].mul_(mom).add_(p.grad.data, alpha=damp) # NEW TO BE TESTED
    return state
average_grad.defaults = dict(mom=0.9)


def average_sqr_grad(state, p, sqr_mom, dampening=True, **kwargs):
    if 'sqr_avg' not in state: state['sqr_avg'] = torch.zeros_like(p.grad.data)
    damp = 1-sqr_mom if dampening else 1.
    # state['sqr_avg'].mul_(sqr_mom).addcmul_(damp, p.grad.data, p.grad.data) # -> OLD DEPRECRATED
    # state['sqr_avg'].mul_(sqr_mom).addcmul_(p.grad.data, p.grad.data, damp) # NEW TO BE TESTED
    state['sqr_avg'].mul_(sqr_mom).addcmul_(p.grad.data, p.grad.data, value=damp)
    return state
average_sqr_grad.defaults = dict(sqr_mom=0.99)


def step_stat(state, p, **kwargs):
    if 'step' not in state: state['step'] = 0
    state['step'] += 1
    return state


# Steps

def weight_decay(p, lr, wd, do_wd=True, **kwargs):
    if do_wd and wd!=0: p.data.mul_(1 - lr*wd)
    return p
#weight_decay.defaults = dict(wd=0.)


def l2_reg(p, lr, wd, do_wd=True, **kwargs):
    if do_wd and wd!=0:
        p.grad.data.add_(p.data, alpha=wd)
    return p
#l2_reg.defaults = dict(wd=0.)


def sgd_step(p, lr, **kwargs):
    p.data.add_(p.grad.data, alpha=-lr)
    return p
#sgd_step._defaults = dict(lr=0.01)


def momentum_step(p, lr, grad_avg, **kwargs):
    p.data.add_(grad_avg, alpha=-lr)
    return p


def debias(mom, damp, step): return damp * (1 - mom**step) / (1-mom)


def adam_step(p, lr, mom, step, sqr_mom, grad_avg, sqr_avg, epsilon, **kwargs):
    "Step for Adam with `lr` on `p`"
    debias1 = debias(mom, 1-mom, step)
    debias2 = debias(sqr_mom, 1-sqr_mom, step)
    # p.data.addcdiv_(-lr / debias1, grad_avg, (sqr_avg/debias2).sqrt() + epsilon)
    p.data.addcdiv_(grad_avg, (sqr_avg/debias2).sqrt()+epsilon, value=-lr/debias1)
    return p
#adam_step._defaults = dict(epsilon=1e-5, lr=0.01,)


def lamb_step(p, lr, mom, step, sqr_mom, grad_avg, sqr_avg, epsilon, **kwargs):
    "Step for LAMB with `lr` on `p`"
    debias1 = debias(mom, 1-mom, step)
    debias2 = debias(sqr_mom, 1-sqr_mom, step)
    r1 = p.data.pow(2).mean().sqrt()
    step = (grad_avg/debias1) / ((sqr_avg/debias2).sqrt()+epsilon)
    r2 = step.pow(2).mean().sqrt()
    q = 1 if r1 == 0 or r2 == 0 else min(r1/r2,10)
    p.data.add_(step, alpha=-lr*q)
    return p
#lamb_step._defaults = dict(epsilon=1e-6, wd=0.)


# Optimizers

def SGD(params, lr=0.01, mom=0., wd=1e-5, decouple_wd=True):
    steppers = [weight_decay] if decouple_wd else [l2_reg]
    steppers.append(sgd_step if mom==0 else momentum_step)
    if mom == 0.:
        return Optimizer(params, steppers, lr=lr, wd=wd)
    else:
        return Optimizer(params, steppers, stats=average_grad, lr=lr, mom=mom, wd=wd)
    
    
def Adam(params, lr=0.01, mom=0.9, sqr_mom=0.99, epsilon=1e-5, wd=1e-5):
    steppers = [l2_reg, adam_step]
    stats = [partial(average_grad, dampening=True), average_sqr_grad, step_stat]
    return Optimizer(params, steppers=steppers, stats=stats, lr=lr, mom=mom, sqr_mom=sqr_mom, epsilon=epsilon, wd=wd)


def Lamb(params, lr=0.01, mom=0.9, sqr_mom=0.99, epsilon=1e-5, wd=1e-5):
    steppers = [l2_reg, lamb_step]
    stats = [partial(average_grad, dampening=True), average_sqr_grad, step_stat]
    return Optimizer(params, steppers=steppers, stats=stats, lr=lr, mom=mom, sqr_mom=sqr_mom, epsilon=epsilon, wd=wd)