import numpy as np
from matplotlib import pyplot as plt
from pprint import pprint
from scipy.fft import fft2, ifft2
import sys
import matplotlib
import h5py
from datetime import datetime


class Kuramoto2d:
    def __init__(self, Nx, Ny, K):
        self.Nx = Nx
        self.Ny = Ny
        self.theta = np.zeros((Nx, Ny))
        self.omega = np.zeros((Nx, Ny))
        self.w = np.zeros((Nx, Ny))
        self.K = K

        self.meshX, self.meshY = np.meshgrid(np.arange(0, Nx), np.arange(0, Ny))

    def init_freq(self, omega0, gamma, seed=None):

        self.omega0 = omega0
        self.gamma = gamma

        if not seed is None:
            np.random.seed(seed)
        self.omega = np.random.standard_cauchy((self.Nx, self.Ny)) * gamma + omega0

    def set_freq(self, omega):
        self.omega = omega

    def init_phase(self, seed=None):
        if not seed is None:
            np.random.seed(seed)
        self.theta = np.random.uniform(0, np.pi*2, (self.Nx, self.Ny))

    def set_phase(self, theta):
        self.theta = theta

    def set_weights(self, w):
        self.w = w
        self.wk = fft2(self.w)
        self.Zmax = np.sum(w)
    
    def theta_dot(self, theta1):
        z = np.exp(1j*theta1)
        zk = fft2(z)
        Z = ifft2(self.wk*zk)
        return self.omega + self.K*np.abs(Z)*np.sin(np.angle(Z)-np.angle(z))

    def evolve(self, dt, t_max, t_digits=3, cycle=29, extra_prefix=''):
        t = 0
        d = 0
        while t < t_max:
            k1 = self.theta_dot(self.theta)
            k2 = self.theta_dot(self.theta + dt*k1/2)
            k3 = self.theta_dot(self.theta + dt*k2/2)
            k4 = self.theta_dot(self.theta + dt*k3)
            self.theta += dt * (k1 + 2*k2 + 2*k3 + k4) / 6

            t += dt
            d += 1

            if d >= cycle:
                d = 0
                Z0 = self.get_Z0()
                R0 = np.round(np.abs(Z0), 3)
                Phi0 = np.round(np.angle(Z0), 3)
                sys.stdout.write(f'\r  {extra_prefix}   {np.round(t, t_digits)}/{t_max}   |   Z0={R0, Phi0}                                  ')
                sys.stdout.flush()
        return t

    def evolve_and_record_hdf(self, dt, batch_size, t_max, fname):
        f = h5py.File(fname, 'w', )
        f.create_dataset('omega', dtype='f', data=self.omega.tolist())
        f.create_dataset('weight', dtype='f', data=self.w.tolist())
        f.create_dataset('theta', dtype='f', data=[self.theta.tolist()], chunks=(1, self.Nx, self.Ny), maxshape=(None, self.Nx,
                                                                                                                 self.Ny))
        t = 0
        f.create_dataset('t', dtype='f', data=[t], chunks=(1,), maxshape=(None,))
        f.attrs['time'] = datetime.now().strftime('%Y.%m.%d-%H:%m:%S') 

        chunk_ind = 0

        while t < t_max:
            chunk_ind += 1
            delta_t = self.evolve(dt, dt*batch_size, cycle=batch_size//2, extra_prefix=f'{np.round(t, 3)}/{t_max}\t  |   ')
            t += delta_t

            f['theta'].resize(chunk_ind+1, axis=0)
            f['theta'][chunk_ind] = self.theta.tolist()
            f['t'].resize(chunk_ind+1, axis=0)
            f['t'][chunk_ind] = t
        sys.stdout.flush()
        print()

        return f

    def get_Z0(self):
        return get_Z0(self.theta, self.Nx, self.Ny)

    def get_Z(self):
        return get_Z(self.theta, self.wk)

    def draw_plots(self, show=True):
        ax1 = plt.subplot(1, 3, 1)
        ax2 = plt.subplot(1, 3, 2)
        ax3 = plt.subplot(1, 3, 3)

        cf1 = ax1.pcolormesh(self.meshX, self.meshY, self.theta % (2*np.pi), cmap='hsv', vmin=0, vmax=np.pi*2, shading='auto')
        ax1.set_aspect('equal', 'box')
        ax1.set_xticks([0, self.Nx])
        ax1.set_yticks([0, self.Ny])

        Z = self.get_Z() 
        
        cf2 = ax2.imshow(complex_array_to_rgb(Z/self.Zmax, rmax=1), extent=(0,self.Nx,0,self.Ny), origin='lower',
                         aspect='equal')

        ax2.set_aspect('equal', 'box')
        ax2.set_xticks([0, self.Nx])
        ax2.set_yticks([0, self.Ny])
        
        Z0 = self.get_Z0()

        ax3.set_xlim(-1, 1)
        ax3.set_ylim(-1, 1)
        ax3.plot([np.real(Z0)], [np.imag(Z0)])
        ax3.set_aspect('equal', 'box')

        ax3.plot([0, 0], [-1, 1], lw=1, color='black')
        ax3.plot([-1, 1], [0, 0], lw=1, color='black')
        
        plt.colorbar(cf1, ax=[ax1, ax2, ax3], location='top', fraction=0.05)

        if show:
            plt.show()
        
        return ax1, ax2, ax3

def get_Z0(theta, Nx, Ny):
    return np.sum(np.exp(1j*theta)) / (Nx*Ny)

def get_Z(theta, wk):
    zk = fft2(np.exp(1j*theta))
    Z = ifft2(wk*zk)
    return Z


def power_weights(nu, Nx, Ny):
    w = np.zeros((Nx, Ny))

    for i in range(Nx):
        for j in range(Ny):
            if i == 0 and j == 0:
                w[i][j] = 0
            else:
                w[i][j] = 1 / np.sqrt(min(i**2, (i-Nx)**2) + min(j**2, (j-Ny)**2)) ** nu
    return w


#--- plot utils
def complex_array_to_rgb(X, theme='dark', rmax=None):
    '''Takes an array of complex number and converts it to an array of [r, g, b],
    where phase gives hue and saturaton/value are given by the absolute value.
    Especially for use with imshow for complex plots.'''
    absmax = rmax or np.abs(X).max()
    Y = np.zeros(X.shape + (3,), dtype='float')
    Y[..., 0] = (np.angle(X)) / (2 * np.pi) % 1
    if theme == 'light':
        Y[..., 1] = np.clip(np.abs(X) / absmax, 0, 1)
        Y[..., 2] = 1
    elif theme == 'dark':
        Y[..., 1] = 1
        Y[..., 2] = np.clip(np.abs(X) / absmax, 0, 1)
    Y = matplotlib.colors.hsv_to_rgb(Y)
    return Y



