"""Implementation for evolutionary multitasking (EM)"""
from math import tanh
from operator import itemgetter
from collections import defaultdict
from ase.ga.population import Population
from ase.ga.convergence import Convergence
from ase.ga import get_raw_score
import numpy as np


class MultitaskPopulation(Population):                                      
    """Different tasks are assigned to different niches. The candidates
    are ranked according to the effective fitness, given by the shortest 
    distance between the raw score of the marked niche and the upper 
    envelope after adding the individual. The raw score is given by the 
    fitness gain in the maximum-gained niche. **The raw scores of each 
    configuration for all tasks must be provided as a Numpy array in
    atoms.info['data']['raw_scores']**. After providing the raw scores, 
    **the effective score of each configuration is automatically 
    calculated and stored in atoms.info['key_value_pairs']['raw_score']**.
    The niches that benefit the most from each configuration are stored in
    atoms.info['data']['niches'], and the dominating niche is stored in
    atoms.info['key_value_pairs']['dominating_niche'].

    Parameters
    ----------
    num_tasks: int
        The number of tasks.

    exp_function: bool, default True
        If True use an exponential function for ranking the fitness.
        If False use the same as in Population.

    exp_prefactor: float, default 0.5
        The prefactor used in the exponential fitness scaling function.
    """

    def __init__(self, data_connection, population_size, num_tasks,
                 comparator=None, logfile=None, use_extinct=False,
                 exp_function=True, exp_prefactor=0.5, rng=np.random):
        self.exp_function = exp_function
        self.exp_prefactor = exp_prefactor
        self.vf = lambda x: x.info['key_value_pairs']['dominating_niche']
        # The current fitness is set at each update of the population
        self.current_fitness = None

        Population.__init__(self, data_connection, population_size,
                            comparator, logfile, use_extinct, rng=rng)
        self.max_scores = np.full(num_tasks, np.NINF, dtype=float)
        self.dominating_niches = np.full(num_tasks, -1, dtype=int)
        self.rep_no_gain = 0

    def get_rank(self, candidates):
        rank = np.array([-1] * len(candidates))
        # Remember the order when decreasing rank later
        order = dict((candidates[i].info['key_value_pairs']['gaid'], i)
                     for i in range(len(candidates)))

        # Group candidates in niches according to the variable
        # function vf and also sort them according to raw score
        self.set_vf_dict(candidates, key=get_raw_score, reverse=True)
        # Decrease the rank of the not best candidates in each niche
        for vf, li in self.vf_dict.items():
            for i, c in enumerate(li):
                rank[order[c.info['key_value_pairs']['gaid']]] -= i

        return rank

    def set_vf_dict(self, candidates, **sort_arguments):
        d = defaultdict(list)
        for c in candidates:
            d[self.vf(c)].append(c)
        if sort_arguments:
            for cl in d.values():
                cl.sort(**sort_arguments)
        self.vf_dict = d

    def __get_fitness__(self, candidates):
        expf = self.exp_function
        rfit = self.get_rank(candidates)

        if not expf:
            rmax = max(rfit)
            rmin = min(rfit)
            T = rmin - rmax
            # If using obj_rank probability, must have non-zero T val.
            # pop_size must be greater than number of permutations.
            # We test for this here
            msg = "Equal fitness for best and worst candidate in the "
            msg += "population! Fitness scaling is impossible! "
            msg += "Try with a larger population."
            assert T != 0., msg
            return 0.5 * (1. - np.tanh(2. * (rfit - rmax) / T - 1.))
        else:
            return self.exp_prefactor ** (-rfit - 1)

    def update(self, new_cand):
        """The update method in Population will add to the end of
        the population, that can't be used here since the fitness
        will potentially change for all candidates when new are added,
        therefore just recalc the population every time. New candidates
        are required (must not be added before calling this method).
        The maximum gain dynamic niching (MGDN) algorithm is executed.
        """

        # Update the upper envelope
        prev_max_scores = self.max_scores.copy()
        gained_ids = []
        for i, a in enumerate(new_cand):
            scores = a.info['data']['raw_scores']
            gained_niches = np.argwhere(scores > self.max_scores)
            if gained_niches.size != 0:
                self.max_scores[gained_niches] = scores[gained_niches]
                gained_ids.append(i)

        # Update the array that records the niche dominating other gained niches
        # with the requirements of: 1. contributes to the updated upper envelope;
        # 2. maximum in gain compared to the previous upper envelope
        first_generation = np.any(prev_max_scores == np.NINF)
        for i in gained_ids:
            scores = new_cand[i].info['data']['raw_scores']
            maxed_niches = np.argwhere(scores == self.max_scores)
            if maxed_niches.size != 0:
                if first_generation:
                    dominating_niche = int(max(maxed_niches, key=lambda x: scores[x]))
                else:
                    dominating_niche = int(max(maxed_niches, key=lambda x:
                                               scores[x] - prev_max_scores[x]))
                self.dominating_niches[maxed_niches] = dominating_niche

        # Caculate the effective fitness and assign a niche for each new candidate
        for i in range(len(new_cand)):
            scores = new_cand[i].info['data']['raw_scores']
            min_loss_niche = np.argmax(scores - self.max_scores)
            dominating_niche = self.dominating_niches[min_loss_niche]
            f_eff = float(np.around(scores[min_loss_niche] - 
                          self.max_scores[min_loss_niche], 8))
            new_cand[i].info['key_value_pairs']['raw_score'] = f_eff
            new_cand[i].info['key_value_pairs']['dominating_niche'] = dominating_niche
            new_cand[i].info['data']['niches'] = np.argwhere(
                self.dominating_niches==dominating_niche).flatten() 

        # Update the fitness of all previously-relaxed candidates if fitness     
        # is gained at any niche from the new generation (niche migration)
        updated_cand = []
        if gained_ids and len(self.pop) > 0:
            # Update the database        
            prev_cand = self.dc.get_all_relaxed_candidates()
            del_ids = [] 
            for a in prev_cand:
                scores = a.info['data']['raw_scores']
                min_loss_niche = np.argmax(scores - self.max_scores)
                dominating_niche = self.dominating_niches[min_loss_niche]
                f_eff = float(np.around(scores[min_loss_niche] - 
                              self.max_scores[min_loss_niche], 8))
                a.info['key_value_pairs']['raw_score'] = f_eff
                a.info['key_value_pairs']['dominating_niche'] = dominating_niche
                a.info['data']['niches'] = np.argwhere(
                    self.dominating_niches==dominating_niche).flatten() 
                updated_cand.append(a)
                gaid = a.info['confid']
                del_ids.append(gaid)
            self.dc.c.delete(del_ids)
            self.rep_no_gain = 0
        else:
            self.rep_no_gain += 1

        self.dc.add_more_relaxed_candidates(updated_cand + new_cand)
        self.pop = []            
        self.__initialize_pop__()
        
        self._write_log()

    def __initialize_pop__(self):
        # Get all relaxed candidates from the database
        ue = self.use_extinct
        all_cand = self.dc.get_all_relaxed_candidates(use_extinct=ue)
        all_cand.sort(key=get_raw_score, reverse=True)

        if len(all_cand) > 0:
            fitf = self.__get_fitness__(all_cand)
            all_sorted = list(zip(fitf, all_cand))
            all_sorted.sort(key=itemgetter(0), reverse=True)
            sort_cand = []
            for _, t2 in all_sorted:
                sort_cand.append(t2)
            all_sorted = sort_cand

            # Fill up the population with the self.pop_size most stable
            # unique candidates.
            i = 0
            while i < len(all_sorted) and len(self.pop) < self.pop_size:
                c = all_sorted[i]
                c_vf = self.vf(c)
                i += 1
                eq = False
                for a in self.pop:
                    a_vf = self.vf(a)
                    # Only run comparator if the variable_function (self.vf)
                    # returns the same. If it returns something different the
                    # candidates are inherently different.
                    # This is done to speed up.
                    if a_vf == c_vf:
                        if self.comparator.looks_like(a, c):
                            eq = True
                            break
                if not eq:
                    self.pop.append(c)
        self.current_fitness = self.__get_fitness__(self.pop)
        self.all_cand = all_cand

    def get_two_candidates(self):
        """Returns two candidates for pairing employing the
        roulete wheel selection scheme described in
        R.L. Johnston Dalton Transactions,
        Vol. 22, No. 22. (2003), pp. 4193-4207
        """

        if len(self.pop) < 2:
            self.update()

        if len(self.pop) < 2:
            return None

        # Use saved fitness
        fit = self.current_fitness
        fmax = max(fit)
        c1 = self.pop[0]
        c2 = self.pop[0]
        while c1.info['confid'] == c2.info['confid']:
            nnf = True
            while nnf:
                t = self.rng.randint(len(self.pop))
                if fit[t] > self.rng.rand() * fmax:
                    c1 = self.pop[t]
                    nnf = False
            nnf = True
            while nnf:
                t = self.rng.randint(len(self.pop))
                if fit[t] > self.rng.rand() * fmax:
                    c2 = self.pop[t]
                    nnf = False

        return (c1.copy(), c2.copy())


class MultitaskGenerationRepetitionConvergence(Convergence):                      
    """Returns True if the latest finished population is stagnated 
    (no fitness gain in any task) for number_of_generations.

    Parameters
    ----------
    number_of_generations: int
        How many generations need to be equal before convergence.

    max_generations: int, default indefinte
        The maximum number of generations the GA is allowed to run.
    """

    def __init__(self, population_instance, 
                 number_of_generations,
                 max_generations=100000000):
        Convergence.__init__(self, population_instance)
        self.numgens = number_of_generations
        self.maxgen = max_generations

    def converged(self):
        size = self.pop.pop_size
        cur_gen_num = self.pop.dc.get_generation_number(size)

        if cur_gen_num >= self.maxgen:
            return True

        if cur_gen_num <= 1:
            return False

        if self.pop.rep_no_gain >= self.numgens:
            return True

        return False

