import math

import numpy as np


def get_E(scf):
    '''
        Calculate energy contributions.
        Latex: Eq. 2.49
    '''
    Ekin = get_Ekin(scf.atoms, scf.op, scf.Y)
    Ecoul = get_Ecoul(scf.op, scf.n, scf.phi)
    Exc = get_Exc(scf.op, scf.n, scf.exc)
    Een = get_Een(scf.n, scf.pot)
    return Ekin + Ecoul + Exc + Een + scf.Eewald


def get_Ekin(atoms, op, W):
    '''
        Calculate the kinetic energy.
        Latex: Eq. 2.37
    '''
    F = np.diag(atoms.f)
    T = -0.5 * np.trace(F @ (W.conj().T @ op.L(W)))
    return np.real(T)


def get_Ecoul(op, n, phi):
    '''
        Calculate the Coulomb energy.
        Latex: Eq. 2.40 + Eq. 2.41 (as in Eq. 2.49)
    '''
    Ecoul = 0.5 * n.conj().T @ op.Jdag(op.O(phi))
    return np.real(Ecoul)


def get_Exc(op, n, exc):
    '''
        Calculate the exchange-correlation energy.
        Latex: Eq. 2.39
    '''
    Exc = n.conj().T @ op.Jdag(op.O(op.J(exc)))
    return np.real(Exc)


def get_Een(n, Vreciproc):
    '''
       Calculate the electron-ion interaction.
       Latex: Eq. 2.38
    '''
    Een = Vreciproc.conj().T @ n
    return np.real(Een)


def get_Eewald(atoms, gcut=2, gamma=1e-8):
    '''
        Calculate the Ewald energy.
        Latex: Eq. A.12 ff.
    '''
    Natoms = len(atoms.atom)
    X = atoms.X
    Z = atoms.Z
    Omega = atoms.Omega
    R = atoms.R

    t1, t2, t3 = R
    t1m = np.sqrt(t1 @ t1)
    t2m = np.sqrt(t2 @ t2)
    t3m = np.sqrt(t3 @ t3)

    g1, g2, g3 = 2 * np.pi * np.linalg.inv(R.conj().T)
    g1m = np.sqrt(g1 @ g1)
    g2m = np.sqrt(g2 @ g2)
    g3m = np.sqrt(g3 @ g3)

    gexp = -np.log(gamma)
    nu = 0.5 * np.sqrt(gcut**2 / gexp)

    x = np.sum(Z**2)
    totalcharge = np.sum(Z)

    Eewald = -nu * x / np.sqrt(np.pi)
    Eewald += -np.pi * totalcharge**2 / (2 * Omega * nu**2)

    tmax = np.sqrt(0.5 * gexp) / nu
    mmm1 = np.rint(tmax / t1m + 1.5)
    mmm2 = np.rint(tmax / t2m + 1.5)
    mmm3 = np.rint(tmax / t3m + 1.5)

    dX = np.empty(3)
    T = np.empty(3)
    for ia in range(Natoms):
        for ja in range(Natoms):
            dX = X[ia] - X[ja]
            ZiZj = Z[ia] * Z[ja]
            for i in np.arange(-mmm1, mmm1 + 1):
                for j in np.arange(-mmm2, mmm2 + 1):
                    for k in np.arange(-mmm3, mmm3 + 1):
                        if (ia != ja) or ((abs(i) + abs(j) + abs(k)) != 0):
                            T = i * t1 + j * t2 + k * t3
                            rmag = np.sqrt(np.sum((dX - T)**2))
                            Eewald += 0.5 * ZiZj * math.erfc(rmag * nu) / rmag

    mmm1 = np.rint(gcut / g1m + 1.5)
    mmm2 = np.rint(gcut / g2m + 1.5)
    mmm3 = np.rint(gcut / g3m + 1.5)

    G = np.empty(3)
    for ia in range(Natoms):
        for ja in range(Natoms):
            dX = X[ia] - X[ja]
            ZiZj = Z[ia] * Z[ja]
            for i in np.arange(-mmm1, mmm1 + 1):
                for j in np.arange(-mmm2, mmm2 + 1):
                    for k in np.arange(-mmm3, mmm3 + 1):
                        if (abs(i) + abs(j) + abs(k)) != 0:
                            G = i * g1 + j * g2 + k * g3
                            GX = np.sum(G * dX)
                            G2 = np.sum(G**2)
                            x = 2 * np.pi / Omega * np.exp(-0.25 * G2 / nu**2) / G2
                            Eewald += x * ZiZj * np.cos(GX)
    return Eewald
