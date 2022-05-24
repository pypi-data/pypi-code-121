""" ACFDT-RPA energy with VASP (contribution from Eric Hermes) """
from ase.calculators.vasp import Vasp
from shutil import copy

def get_acfdt_energy(species, common_params, nomega=10, acfdt_algo='RPAR',
                     acfdt_precfock='Fast', gamma_point=False, loptics=False):
    # step 1
    calc1 = Vasp(ediff=1e-8, **common_params)
    species.set_calculator(calc1)
    species.get_potential_energy()
    copy('OUTCAR', 'OUTCAR.1')
    copy('OSZICAR', 'OSZICAR.1')
    copy('vasprun.xml', 'vasprun.1.xml')

    # step 2
    calc2 = Vasp(algo='eigenval',
                 nelm=1,
                 lwave=False,
                 lhfcalc=True,
                 aexx=1.0,
                 precfock='Fast',
                 **common_params)

    species.set_calculator(calc2)
    try:
        species.get_potential_energy()
    except UnboundLocalError:
        pass
    copy('OUTCAR', 'OUTCAR.2')
    copy('OSZICAR', 'OSZICAR.2')
    copy('vasprun.xml', 'vasprun.2.xml')

    nbands = None
    eexx = None
    ehfc = None

    with open('OUTCAR.2', 'r') as f:
        for line in f:
            if line.startswith(" maximum number of plane-waves:"):
                nbands = int(line.split()[-1])
            elif line.startswith("  energy without entropy ="):
                eexx = float(line.split()[-1])
            elif line.startswith("  exchange ACFDT corr."):
                ehfc = float(line.split()[4])
                break
    if None in [nbands, eexx, ehfc]:
        raise ValueError('Could not parse HF OUTCAR!')

    if gamma_point:
        nbands = nbands * 2

    # step 3
    calc3 = Vasp(nbands=nbands,
                 algo='Exact',
                 nelm=1,
                 loptics=loptics,
                 **common_params)

    species.set_calculator(calc3)
    species.get_potential_energy()
    copy('OUTCAR', 'OUTCAR.3')
    copy('OSZICAR', 'OSZICAR.3')
    copy('vasprun.xml', 'vasprun.3.xml')

    # step 4
    calc4 = Vasp(nbands=nbands,
                 algo=acfdt_algo,
                 nomega=nomega,
                 precfock=acfdt_precfock,
                 **common_params)
    
    species.set_calculator(calc4)
    try:
        species.get_potential_energy()
    except UnboundLocalError:
        pass
    copy('OUTCAR', 'OUTCAR.4')
    copy('OSZICAR', 'OSZICAR.4')
    copy('vasprun.xml', 'vasprun.4.xml')

    with open('OUTCAR.4', 'r') as f:
        for line in f:
            if line.startswith("  converged value"):
                erpa = float(line.split()[2])

    return erpa, eexx, ehfc
