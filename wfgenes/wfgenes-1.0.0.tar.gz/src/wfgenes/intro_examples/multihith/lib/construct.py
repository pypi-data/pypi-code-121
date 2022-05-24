""" Methods for constructing structures with atomistic resolution """

__author__ = 'Ivan Kondov'
__email__ = 'ivan.kondov@kit.edu'
__copyright__ = 'Copyright 2018, Karlsruhe Institute of Technology'


def create_structure(**kwargs):
    """ Generic method to construct a structure with ASE from a dictionary """
    if kwargs['type'] == 'cluster':
        from ase import cluster
        from ase import Atoms
        module = getattr(cluster, kwargs['module'])
        method = getattr(module, kwargs['method']['name'])
        cluster = method(*kwargs['method']['args'], **kwargs['method']['kwargs'])
        return Atoms(cluster)

    if kwargs['type'] in ['slab', 'surface', 'bulk']:
        from ase import build
        method = getattr(build, kwargs['method']['name'])
        return method(*kwargs['method']['args'], **kwargs['method']['kwargs'])

    if kwargs['type'] == 'molecule':
        pass

    if kwargs['type'] == 'polymer':
        pass

    if kwargs['type'] == 'graphene':
        pass

    if kwargs['type'] == 'nanotube':
        pass

    if kwargs['type'] == 'molecular cluster':
        pass

    if kwargs['type'] == 'molecular slab':
        pass

    if kwargs['type'] == 'molecular bulk crystal':
        pass
