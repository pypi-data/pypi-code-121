import time
import numpy as np
from random import random, seed
from ase.ga.data import PrepareDB
from ase.ga.data import DataConnection
from ase.ga.utilities import closest_distances_generator
from ase.ga.utilities import get_all_atom_types
from ase.ga.startgenerator import StartGenerator
from ase.ga.population import Population
from ase.ga.standard_comparators import InteratomicDistanceComparator
from ase.ga.cutandsplicepairing import CutAndSplicePairing
from ase.ga.offspring_creator import OperationSelector
from ase.ga.standardmutations import MirrorMutation
from ase.ga.standardmutations import RattleMutation
from ase.ga.standardmutations import PermutationMutation
from ase.ga.parallellocalrun import ParallelLocalRun
from ase.optimize import BFGS
from calculators import classmap
from ase.ga import get_parametrization
from ase.ga.utilities import get_atoms_connections, get_atoms_distribution
from ase.ga.utilities import get_angles_distribution
from ase.ga.utilities import get_rings, get_neighborlist


def combine_parameters(conf):
    # Get and combine selected parameters
    parameters = []
    gets = [get_atoms_connections(conf) + get_rings(conf) +
            get_angles_distribution(conf) + get_atoms_distribution(conf)]
    for get in gets:
        parameters += get
    return parameters


class GASimulation(object):
    """ The main class """

    # class wide objects
    da = None
    calc = None
    pairing = None
    mutations = None
    comparator = None
    phase = 0 # 1, 2
    parallel = False
    screening = False
    find_neighbors = None
    perform_parametrization = None

    def __init__(self, parameters):

        self.params = parameters
        self.ga_params = parameters['genetic algorithm']
        self.va_params = parameters['variate']
        self.calc_params = parameters['calculator']['parameters']

        self.check_state()
        print('Phase', self.phase)


    def check_state(self):
        # test whether the database exists
        if self.da is None:
            filename = str(self.ga_params['db file'])
            try:
                self.da = DataConnection(filename)
            except IOError as err:
                string = 'DB file ' + filename + ' not found'
                if string in err:
                    self.phase = 0
                    return
                else:
                    raise

        try:
            n_rel = len(self.da.get_all_relaxed_candidates())
            n_unr = self.da.get_number_of_unrelaxed_candidates()
        except:
            raise
        else:
            if n_unr > 0:
                self.phase = 1
            elif n_rel > 0:
                self.phase = 2
            else:
                self.phase = 0


    def create_initial_population(self):
        """ Constructs the substrate and the initial individuals """
        from ase import Atoms
        from ase.io import read
        from ase.constraints import FixAtoms
        from construct import create_structure

        self.check_state()
        assert self.phase == 0, 'population cannot be initialized twice'

# redundant to run-step.py

        # load / construct the substrate
        if self.params['substrate'] is None:
            self.substrate = Atoms()
        else:
            substr_params = self.params['substrate']
            if substr_params['input structure'] is not None:
                # load the structure from params
                substr = substr_params['input structure']
            elif substr_params['input file'] is not None:
                # read the structure from file
                substr = read(substr_params['input file'])
            else:
                # construct the structure
                substr = create_structure(**substr_params['construct'])

            # constraints
            if 'constrain all atoms' in substr_params:
                if substr_params['constrain all atoms']:
                    substr.set_constraint(FixAtoms(mask=len(substr) * [True]))
                elif substr_params['constraints']:
                    pass

            # magmoms
            if 'initial magnetic moments' in substr_params:
                magmoms = substr_params['initial magnetic moments']
                if type(magmoms) is list:
                    substr.set_initial_magnetic_moments(magmoms)
                else:
                    substr.set_initial_magnetic_moments(len(substr)*[magmoms])
            self.substrate = substr

# end of redundant section

        # construct the variate
        p0, v1, v2, v3 = self.get_variate_box()

        # define the closest distance between two atoms
        unique_atom_types = get_all_atom_types(self.substrate, 
            self.va_params['composition'])
        cd = closest_distances_generator(
            atom_numbers = unique_atom_types,
            ratio_of_covalent_radii = 
                self.ga_params['ratio of covalent radii']
        )

        # create the starting population
        sg = StartGenerator(slab=self.substrate,
                            atom_numbers=self.va_params['composition'],
                            closest_allowed_distances=cd,
                            box_to_place_in=[p0, [v1, v2, v3]])

        # generate the starting population
        self.starting_population = [sg.get_new_candidate() 
            for i in range(self.ga_params['population size'])]

        if 'initial magnetic moments' in self.va_params:
            for individual in self.starting_population:
                individual.set_initial_magnetic_moments(
                    self.substrate.get_initial_magnetic_moments().tolist() +
                    self.va_params['initial magnetic moments']
                )

        # initialize the database
        pdb = PrepareDB(
            db_file_name = str(self.ga_params['db file']),
            simulation_cell = self.substrate,
            stoichiometry = self.va_params['composition']
        )

        # save the starting population
        for a in self.starting_population:
            pdb.add_unrelaxed_candidate(a)


    def initialize_simulation(self):
        """ Initialize the different components of the GA """

        self.check_state()
        assert self.phase > 0, 'simulation can start only with some population'

        if 'number of procs' in self.ga_params.keys():
            if self.ga_params['number of procs'] > 1:
                self.parallel = True
                self.parallel_local_run = ParallelLocalRun(
                    data_connection = self.da,
                    tmp_folder = self.ga_params['temporary folder'],
                    n_simul = self.ga_params['number of procs'],
                    calc_script = self.ga_params['calc script']
                )
                print('Parallel mode turned on')

        atom_numbers_to_optimize = self.da.get_atom_numbers_to_optimize()
        n_to_optimize = len(atom_numbers_to_optimize)
        slab = self.da.get_slab()
        all_atom_types = get_all_atom_types(slab, atom_numbers_to_optimize)

        blmin = closest_distances_generator(
                all_atom_types,
                ratio_of_covalent_radii = 
                    self.ga_params['ratio of covalent radii']
        )

        self.comparator = InteratomicDistanceComparator(
            n_top = n_to_optimize,
            pair_cor_cum_diff = 0.015,
            pair_cor_max = 0.7,
            dE = 0.02,
            mic = False
        )

        self.pairing = CutAndSplicePairing(slab, n_to_optimize, blmin)

        if len(set(self.va_params['composition'])) != 1:
            ml = [1., 1., 1.]
            ms = [
                MirrorMutation(blmin, n_to_optimize),
                RattleMutation(blmin, n_to_optimize),
                PermutationMutation(n_to_optimize)
            ]
        else:
            ml = [1., 1.]
            ms = [
                MirrorMutation(blmin, n_to_optimize),
                RattleMutation(blmin, n_to_optimize)
            ]
        self.mutations = OperationSelector(ml, ms)

        if 'rng seed' in list(self.ga_params.keys()):
            seed(self.ga_params['rng seed'])

        if 'screening' in list(self.ga_params.keys()):
            if self.ga_params['screening'] is not None:
                self.screening = True
                self.find_neighbors = get_neighborlist
                self.perform_parametrization = combine_parameters


    def relax_structures(self):
        """ Relax all unrelaxed structures (e.g. the starting population) """

        self.check_state()
        assert self.phase > 0, 'no structures to optimize'

        self.create_calculator()
        while self.da.get_number_of_unrelaxed_candidates() > 0:
            a = self.da.get_an_unrelaxed_candidate()
            self.relax_structure(a)

        if self.parallel:
            while self.parallel_local_run.get_number_of_jobs_running() > 0:
                time.sleep(5.)


    def create_population(self):
        if self.screening:
            self.create_population_with_screening()
        else:
            self.create_population_without_screening()


    def create_population_without_screening(self):
        """ Create new population """

        self.check_state()
        assert self.phase > 1, 'all structures must be relaxed first'
        assert all((self.comparator, self.pairing, self.mutations))

        self.create_calculator()

        population = Population(
            data_connection = self.da,
            population_size = self.ga_params['population size'],
            comparator = self.comparator
        )

        """ test new candidates """
        for i in range(self.ga_params['individuals to test']):
            print('Starting configuration number {0}'.format(i))
            a1, a2 = population.get_two_candidates()
            a3, desc = self.pairing.get_new_individual([a1, a2])
            if a3 is None:
                continue
            self.da.add_unrelaxed_candidate(a3, description=desc)

            # Check if we want to do a mutation
            if random() < self.ga_params['mutation probability']:
                a3_mut, desc = self.mutations.get_new_individual([a3])
                if a3_mut is not None:
                    self.da.add_unrelaxed_step(a3_mut, desc)
                    a3 = a3_mut

            # Relax the new candidate
            self.relax_structure(a3)
            population.update()

        if self.parallel:
            while self.parallel_local_run.get_number_of_jobs_running() > 0:
                time.sleep(5.)


    def create_population_with_screening(self):
        """ Create new population """
        self.check_state()
        assert self.phase > 1, 'all structures must be relaxed first'
        assert all((self.comparator, self.pairing, self.mutations))

        self.create_calculator()

        population = Population(
            data_connection = self.da,
            population_size = self.ga_params['population size'],
            comparator = self.comparator
        )

        # create the regression expression for estimating the energy
        all_trajs = self.da.get_all_relaxed_candidates()
        sampled_points = []
        sampled_energies = []
        for conf in all_trajs:
            no_of_conn = list(get_parametrization(conf))
            if no_of_conn not in sampled_points:
                sampled_points.append(no_of_conn)
                sampled_energies.append(conf.get_potential_energy())

        sampled_points = np.array(sampled_points)
        sampled_energies = np.array(sampled_energies)

        if len(sampled_points) > 0 and len(sampled_energies) >= len(sampled_points[0]):
            weights = np.linalg.lstsq(sampled_points, sampled_energies)[0]
        else:
            weights = None

        """ Test new candidates """
        for i in range(self.ga_params['individuals to test']):
            print('Starting configuration number {0}'.format(i))
            a1, a2 = population.get_two_candidates()

            # Select the "worst" parent energy to which the child will be compared
            ce_a1 = self.da.get_atoms(a1.info['relax_id']).get_potential_energy()
            ce_a2 = self.da.get_atoms(a2.info['relax_id']).get_potential_energy()
            comparison_energy = min(ce_a1, ce_a2)

            a3, desc = self.pairing.get_new_individual([a1, a2])
            if a3 is None:
                continue
            if self.should_we_skip(a3, comparison_energy, weights):
                continue
            self.da.add_unrelaxed_candidate(a3, description=desc)

            if random() < self.ga_params['mutation probability']:
                a3_mut, desc_mut = self.mutations.get_new_individual([a3])
                if (a3_mut is not None and
                    not self.should_we_skip(a3_mut, comparison_energy, weights)):
                    self.da.add_unrelaxed_step(a3_mut, desc_mut)
                    a3 = a3_mut

            # Relax the new candidate
            self.relax_structure(a3)
            population.update()

        if self.parallel:
            while self.parallel_local_run.get_number_of_jobs_running() > 0:
                time.sleep(5.)


    def should_we_skip(self, conf, comparison_energy, weights):
        parameters = combine_parameters(conf)
        st = self.ga_params['screening']['skip threshold']
        sp = self.ga_params['screening']['skip probability']
        # Return if weights not defined (too few completed
        # calculated structures to make a good fit)
        if weights is None:
            return False
        regression_energy = sum(p * q for p, q in zip(weights, parameters))
        # Skip with sp likelihood if energy appears to go up st eV or more
        if (regression_energy - comparison_energy) > st and random() < sp:
            return True
        else:
            return False


    def get_population(self):
        from ase.io import write
        write('all_candidates.traj', self.da.get_all_relaxed_candidates())


    def get_variate_box(self):
        """ Define the volume in which the variate structure is optimized
        the volume is defined by a corner position (p0)
        and three spanning vectors (v1, v2, v3) """

        par = self.va_params['box']
        if par['type'] == 'ontop':
            pos = self.substrate.get_positions()
            cell = self.substrate.get_cell()
            p0 = np.array([0., 0., max(pos[:, 2]) + par['origin']])
            v1 = cell[0, :] * par['v1 factor']
            v2 = cell[1, :] * par['v2 factor']
            v3 = cell[2, :]
            v3[2] = par['v3 value']
        elif par['type'] == 'centered':
            a = par['outer']
            b = par['inner']
            self.substrate.set_cell([a, a, a])
            cell = self.substrate.get_cell()
            p0 = np.array([(a-b)/2, (a-b)/2, (a-b)/2]) 
            v1 = cell[0, :]*b/a
            v2 = cell[1, :]*b/a
            v3 = cell[2, :]*b/a
        else:
            p0, v1, v2, v3 = ()
        return p0, v1, v2, v3


    def open_db(self):
        self.da = DataConnection(str(self.ga_params['db file']))


    def show_initial_population(self):
        from ase.visualize import view
        view(self.starting_population)


    def create_calculator(self):
        if self.calc is None:
            calc_name = self.params['calculator']['name']
            self.calc = classmap[calc_name](**self.calc_params)


    def relax_structure(self, a):
        import warnings
        if self.parallel:
            self.parallel_local_run.relax(a)
        else:
            a.set_calculator(self.calc)
            print('Relaxing starting candidate {0}'.format(a.info['confid']))
            try:
                if self.params['calculator']['optimize']:
                    self.calc.calculate(a)
                else:
                    dyn = BFGS(a, trajectory=None, logfile=None)
                    dyn.run(
                        fmax = abs(self.calc_params['ediffg']),
                        steps = self.calc_params['nsw']
                    )
                energy = a.get_potential_energy()
                if hasattr(self.calc, 'converged'):
                    assert self.calc.converged
                assert energy is not None
                a.info['key_value_pairs']['raw_score'] = - energy
            except(RuntimeError, AssertionError):
                self.da.c.update(a.info['confid'], relaxed=-1)
                message = 'Candidate {0} will be skipped'.format(a.info['confid'])
                warnings.warn(message)
            else:
                self.da.add_relaxed_step(a, find_neighbors=self.find_neighbors, 
                    perform_parametrization=self.perform_parametrization)


