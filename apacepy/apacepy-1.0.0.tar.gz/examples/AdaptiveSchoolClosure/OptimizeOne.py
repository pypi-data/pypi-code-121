import apacepy.Calibration as calib
from deampy.Optimization.ApproxPolicyIteration import ApproximatePolicyIteration
from deampy.Optimization.LearningAndExplorationRules import *

import examples.SchoolClosure.SimulateMultiple as S
from examples.AdaptiveSchoolClosure.source.Model import SchoolClosureModelForOpt

N_ITRS = 2000
B = 50      # parameter of the Harmonic learning rule
BETA = 0.4  # parameter of the epsilon exploration rule
Q_FUNC_DEGREE = 2   # degree of polynomial Q-function
L2_PENALTY = 0.01   # l2 regularization penalty


def optimize(dynamic_type):
    """
    :param dynamic_type:
        'cum incd' for using cumulative incidence as feature
        'incd + delta incd' for using incidence and change in incidence as features
        'incd + cum incd' for using incidence and cumulative incidence as features
        'incd + pd status' for using incidence and the status of physical distancing intervention as features
    """

    # get the seeds and probability weights
    seeds, weights = calib.get_seeds_lnl_probs('../SchoolClosure/summaries/open/calibration_summary.csv')

    # get the simulation model of school closure
    sim_model = SchoolClosureModelForOpt(wtp=S.WTP, dynamic_type=dynamic_type, seeds=seeds, weights=weights)

    # optimization algorithm
    api = ApproximatePolicyIteration(
        sim_model=sim_model,
        num_of_actions=1,
        learning_rule=Harmonic(b=B),
        exploration_rule=EpsilonGreedy(beta=BETA),
        discount_factor=1/(1+0.03),
        q_function_degree=Q_FUNC_DEGREE,
        l2_penalty=L2_PENALTY)

    # optimize
    api.minimize(n_iterations=N_ITRS,
                 q_function_csv_file='q-functions/WTP{}-{}/q-functions.csv'.format(S.WTP, dynamic_type))

    # export iterations
    api.export_results(csv_file='optimization_results/WTP{}-{}/iterations.csv'.format(S.WTP, dynamic_type))

    # show the plot of optimization iterations
    api.plot_iterations(moving_ave_window=int(N_ITRS/10),
                        n_last_iterations_to_ave=int(N_ITRS*0.2),
                        fig_size=(5, 6))


if __name__ == '__main__':
    # optimize(dynamic_type='cum incd')
    optimize(dynamic_type='incd + delta incd')
    # optimize(dynamic_type='incd + cum incd')
    # optimize(dynamic_type='incd + closure status')
