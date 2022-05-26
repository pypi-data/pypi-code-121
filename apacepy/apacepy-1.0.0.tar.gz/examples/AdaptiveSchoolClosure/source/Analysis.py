import apacepy.analysis.Scenarios as S
from examples.AdaptiveSchoolClosure import ROOT

WTP = 0.02


def report_loss_in_nmb(file_name):

    # read scenarios into a dataframe
    df_threshold_based = S.ScenarioDataFrame(
        csv_file_name=file_name)

    df_threshold_based.print_cost_effect_loss_in_nmb(
        cost_outcome_name='Duration of School closure',
        effect_outcome_name='Incidence (after epidemic warm-up)',
        cost_multiplier=52,
        effect_multiplier=1,
        sig_digits=4,
        wtp_value=WTP)


if __name__ == '__main__':

    report_loss_in_nmb(file_name=ROOT.ROOT_DIR + '/scenarios/scenarios-threshold-based.csv')
    report_loss_in_nmb(file_name=ROOT.ROOT_DIR + '/scenarios/scenarios-dynamic.csv')
