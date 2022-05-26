import apacepy.Calibration as calib
from deampy.Optimization.ApproxPolicyIteration import MultiApproximatePolicyIteration
from deampy.Optimization.LearningAndExplorationRules import *

from examples.AdaptiveSchoolClosure.source.Model import SchoolClosureModelForOpt

WTP = 0.02
N_ITRS = 1000
IF_PARALLEL = False
B = [25, 50]
BETA = [0.4, 0.5]
Q_FUNC_DEGREES = [2]
L2_PENALTIES = [0.01]


def optimize(wtp, dynamic_type):

    # get the seeds and probability weights
    seeds, weights = calib.get_seeds_lnl_probs('../SchoolClosure/summaries/open/calibration_summary.csv')

    # build models
    n = len(B) * len(BETA) * len(Q_FUNC_DEGREES) * len(L2_PENALTIES)
    models = []
    for i in range(n):
        models.append(SchoolClosureModelForOpt(
            wtp=wtp, dynamic_type=dynamic_type, seeds=seeds, weights=weights))

    optimizer = MultiApproximatePolicyIteration(
        sim_models=models,
        num_of_actions=1,
        learning_rules=[Harmonic(b=b) for b in B],
        exploration_rules=[EpsilonGreedy(beta=beta) for beta in BETA],
        q_function_degrees=Q_FUNC_DEGREES,
        l2_penalties=L2_PENALTIES)

    optimizer.minimize_all(n_iterations=N_ITRS,
                           n_last_itrs_to_find_minimum=int(N_ITRS*0.2),
                           if_parallel=IF_PARALLEL,
                           folder_to_save_iterations='optimization_results/WTP{}-{}'.format(wtp, dynamic_type),
                           q_functions_folder='q-functions/WTP{}-{}'.format(wtp, dynamic_type),
                           optimal_q_functions_csvfile='q-functions/WTP{}-{}/q-functions.csv'.format(wtp, dynamic_type))

    optimizer.plot_iterations(moving_ave_window=int(N_ITRS / 10), fig_size=(5, 6),
                              n_last_iterations_to_ave=int(N_ITRS*0.2),
                              folder_to_save_figures='optimization_figures/WTP{}-{}'.format(wtp, dynamic_type))


if __name__ == '__main__':
    optimize(wtp=WTP, dynamic_type='incd + cum incd')
