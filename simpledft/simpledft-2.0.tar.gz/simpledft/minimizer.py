from .dft import get_grad, get_n_total, orth, solve_poisson
from .energies import get_E
from .xc import lda_slater_x, lda_vwn_c


def scf_step(scf):
    '''Perform one SCF step for a DFT calculation.'''
    scf.Y = orth(scf.atoms, scf.op, scf.W)
    scf.n = get_n_total(scf.atoms, scf.op, scf.Y)
    scf.phi = solve_poisson(scf.atoms, scf.op, scf.n)
    scf.exc = lda_slater_x(scf.n)[0] + lda_vwn_c(scf.n)[0]
    scf.vxc = lda_slater_x(scf.n)[1] + lda_vwn_c(scf.n)[1]
    return get_E(scf)


def sd(scf, Nit, beta=1e-5, etol=1e-6):
    '''
        Steepest descent minimization algorithm.
        An SCF algorithm.
        Latex: List. 3.21
               Fig. 3.2
    '''
    Elist = []

    for i in range(Nit):
        E = scf_step(scf)
        Elist.append(E)
        print('Nit: {}  \tEtot: {:.6f} Eh'.format(i + 1, E), end='\r')
        if i > 1 and abs(Elist[i - 1] - Elist[i]) < etol:
            print('\nSCF converged.')
            return E
        g = get_grad(scf.atoms, scf.op, scf.W, scf.Y, scf.n, scf.phi, scf.vxc, scf.pot)
        scf.W = scf.W - beta * g
    print('\nSCF not converged!')
    return E
