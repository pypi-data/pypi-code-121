import nlopt
import numpy as np


def getBudget(df, name_date_column, name_target_column, medias, date_get_budget='', number_tail=15):
    if date_get_budget:
        new_df = df.copy()
        new_df.drop(new_df[new_df[name_date_column] > date_get_budget].index, inplace=True)
        full_row = new_df.tail(number_tail).mean()
    else:
        full_row = df.tail(number_tail).mean()

    spends = []

    for m in medias:
        spends.append(full_row[m])

    response = full_row[name_target_column]
    return spends, response


def getVals(df, name_date_column, all_features, date_get_budget='', number_tail=15):
    if date_get_budget:
        new_df = df.copy()
        new_df.drop(new_df[new_df[name_date_column] > date_get_budget].index, inplace=True)
        full_row = new_df.tail(number_tail).mean()
    else:
        full_row = df.tail(number_tail).mean()

    row = full_row[all_features].copy()

    return row


def get_opt_algoritm(algoritm, medias, lower_bounds, upper_bounds, spends, maxeval, myFunc):
    if algoritm in ['GN_DIRECT', 'LD_SLSQP', 'GN_CRS2_LM', 'GD_STOGO', 'LN_BOBYQA', 'LN_NEWUOA', 'LD_CCSAQ']:
        if algoritm == 'GN_DIRECT':
            opt = nlopt.opt(nlopt.GN_DIRECT, len(medias))

        elif algoritm == 'LD_SLSQP':
            opt = nlopt.opt(nlopt.LD_SLSQP, len(medias))

        elif algoritm == 'GN_CRS2_LM':
            opt = nlopt.opt(nlopt.GN_CRS2_LM, len(medias))

        elif algoritm == 'GD_STOGO':
            opt = nlopt.opt(nlopt.GD_STOGO, len(medias))

        elif algoritm == 'LN_BOBYQA':
            opt = nlopt.opt(nlopt.LN_BOBYQA, len(medias))

        elif algoritm == 'LN_NEWUOA':
            opt = nlopt.opt(nlopt.LN_NEWUOA, len(medias))

        else:
            opt = nlopt.opt(nlopt.LD_CCSAQ, len(medias))

        lower_boundaries = np.multiply(lower_bounds, spends)
        upper_boundaries = np.multiply(upper_bounds, spends)

        opt.set_lower_bounds(lower_boundaries)
        opt.set_upper_bounds(upper_boundaries)

        opt.set_max_objective(myFunc)

        opt.set_xtol_rel(1e-14)
        opt.set_maxeval(maxeval)

    else:
        if algoritm == 'GN_ISRES':
            opt = nlopt.opt(nlopt.GN_ISRES, len(medias))

        elif algoritm == 'GN_AGS':
            opt = nlopt.opt(nlopt.GN_AGS, len(medias))

        elif algoritm == 'LN_COBYLA':
            opt = nlopt.opt(nlopt.LN_COBYLA, len(medias))

        elif algoritm == 'GN_ESCH':
            opt = nlopt.opt(nlopt.GN_ESCH, len(medias))

        elif algoritm == 'AUGLAG':
            opt = nlopt.opt(nlopt.AUGLAG, len(medias))

        else:
            opt = nlopt.opt(nlopt.LD_MMA, len(medias))

        lower_boundaries = np.multiply(lower_bounds, spends)
        upper_boundaries = np.multiply(upper_bounds, spends)

        opt.set_lower_bounds(lower_boundaries)
        opt.set_upper_bounds(upper_boundaries)

        opt.set_max_objective(myFunc)
        opt.add_inequality_constraint(lambda z, grad: sum(z) - np.sum(spends), 1e-8)

        # rate of improvement, below which we are done
        opt.set_xtol_rel(1e-14)
        opt.set_maxeval(maxeval)

    return opt
