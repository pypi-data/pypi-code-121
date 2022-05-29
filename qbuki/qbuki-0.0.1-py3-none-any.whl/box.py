import numpy as np
import scipy as sc

from .utils import *

class Box:
    @classmethod
    def from_kraus_operators(cls, K, post_measurement_states=None):
        if len(K.shape) == 2:
            K = K.reshape(1, *K.shape)
        box = Box([], post_measurement_states=post_measurement_states)
        box.K = K
        return box

    def __init__(self, E, post_measurement_states=None):
        self.K = np.array([sc.linalg.sqrtm(e) for e in E])
        self.post_measurement_states = post_measurement_states if type(post_measurement_states) != type(None) else None
        self.inverted = False

    def dim(self):
        return self[:].shape[0]
    
    def __len__(self):
        return len(self.K)

    def __getitem__(self, key):
        if type(key) == slice:
            return np.transpose(self.K[key].conj(), axes=(0,2,1)) @ self.K[key] 
        else:
            return self.K[key].conj().T @ self.K[key]

    def __setitem__(self, key, value):
        if type(key) == slice:
            self.K[key] = np.array([sc.linalg.sqrtm(v) for v in value])
        else:
            self.K[key] = sc.linalg.sqrtm(value)
   
    def __iter__(self):
        return self[:].__iter__()

    def __invert__(self):
        self.inverted = True if not self.inverted else False
        return self

    def __post_measurement_states__(self):
        return np.array([a/a.trace() for a in self[:]]) if type(self.post_measurement_states) == type(None) else self.post_measurement_states

    def __or__(self, other):
        C = np.array([[(a.conj().T @ b).trace() for b in other.__post_measurement_states__()] for a in self[:]])
        if not self.inverted:
            return C
        else:
            self.inverted = False
            return spectral_inverse(C)
    
    def __xor__(self, other):
        B = other[:] if type(other.post_measurement_states) == type(None) else other.post_measurement_states
        G = np.array([[(a.conj().T @ b).trace() for b in B] for a in self[:]])
        if not self.inverted:
            return G
        else:
            self.inverted = False
            return spectral_inverse(G)

    def __and__(self, other):
        K = np.array([np.kron(a, b) for b in other.K for a in self.K])
        if  type(self.post_measurement_states) == type(None) and type(other.post_measurement_states) == None:
            post_measurement_states = None
        else:
            post_measurement_states = np.array([np.kron(a, b) for b in other.__post_measurement_states__() for a in self.__post_measurement_states__()])
        return Box.from_kraus_operators(K, post_measurement_states=post_measurement_states)

    def __add__(self, other):
        K = np.concatenate([self.K, other.K])
        if  type(self.post_measurement_states) == type(None) and type(other.post_measurement_states) == type(None):
            post_measurement_states = None
        else:
            post_measurement_states = np.concatenate([self.__post_measurement_states__(), other.__post_measurement_states__()])
        return Box.from_kraus_operators(K, post_measurement_states=post_measurement_states)

    def __mul__(self, other):
        return Box.from_kraus_operators(np.sqrt(other)*self.K, post_measurement_states=self.post_measurement_states)

    def __rmul__(self, other):
        return self.__mul__(other)
 
    def __truediv__(self, other):
        return self.__mul__(1/other)

    def sum(self):
        return sum(self)

    def bias(self):
        return np.array([e.trace() for e in self[:]])

    def quantumness(self, p=2):
        S = np.linalg.svd(np.eye(len(self)) - (~self|self), compute_uv=False)
        return np.sum(S**p)**(1/p) if p != np.inf else np.max(S)

    def upgrade(self, i, dims):
        K = np.array([upgrade(k, i, dims) for k in self.K])
        post_measurement_states = np.array([upgrade(s, i, dims) for s in self.post_measurement_states]) \
                if type(self.post_measurement_states) != type(None) else None
        return Box.from_kraus_operators(K, post_measurement_states=post_measurement_states)        

    def __lshift__(self, other):
        if len(other.shape) == 1 or other.shape[1] == 1:
            return sum([self[i]*c/self[i].trace() for i, c in enumerate((~self|self) @ other)])
        else:
            return np.array([(e.conj().T @ other).trace() for e in self[:]]).reshape(len(self), 1)

    def __lt__(self, other):
        K = np.array([sum([b @ a @ b.conj().T for b in self.K]) for a in other.K])
        post_measurement_states = np.array([sum([b @ s @ b.conj().T for b in self.K]) for s in other.post_measurement_states]) \
            if type(other.post_measurement_states) != type(None) else None
        return Box.from_kraus_operators(K, post_measurement_states=post_measurement_states)

    def samples(self, rho, n=1):
        return np.random.choice(list(range(len(self))), size=n, p=np.squeeze((self << rho).real))
