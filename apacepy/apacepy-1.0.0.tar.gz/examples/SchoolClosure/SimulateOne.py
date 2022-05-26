import examples.SchoolClosure.SchoolClosureModel as M
from apacepy.epidemic import EpiModel
from examples.SchoolClosure.Plots import plot_trajs

WTP = 0.02
DYNAMIC_TYPE = 'incd + cum incd'  # 'cum incd' | 'incd + delta incd' | 'incd + cum incd' | 'incd + closure status'


def simulate(schools_closed=False, decision_rule='time-based', dynamic_type=None, wtp=None):

    # get model settings
    sets = M.SchoolClosureSettings()
    sets.update_settings(schools_closed=schools_closed, decision_rule=decision_rule,
                         time_on=4, time_off=6, threshold_on=50, threshold_off=20,
                         dynamic_type=dynamic_type, wtp=wtp)

    # make an (empty) epidemic model
    model = EpiModel(id=0, settings=sets)
    # populate an age-structured SIR model
    M.build_school_closure_model(model)

    # simulate
    model.simulate(seed=1909838463)
    # print trajectories
    model.export_trajectories(delete_existing_files=True)

    # print discounted outcomes
    print(model.get_total_discounted_cost_and_health())

    # plot trajectories
    plot_trajs(schools_closed=schools_closed,
               decision_rule=decision_rule,
               prev_multiplier=52,  # to show weeks on the x-axis of prevalence data
               incd_multiplier=52*sets.observationPeriod)  # to show weeks on the x-axis of incidence data


if __name__ == "__main__":
    simulate(schools_closed=False)
    # simulate(schools_closed=True, decision_rule='time-based')
    #
    simulate(schools_closed=True, decision_rule='threshold-based')
    # simulate(schools_closed=True, decision_rule='dynamic', dynamic_type=DYNAMIC_TYPE, wtp=WTP)

