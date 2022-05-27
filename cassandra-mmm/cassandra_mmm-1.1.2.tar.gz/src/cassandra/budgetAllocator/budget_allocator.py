import pandas as pd
import numpy as np
from cassandra.data.trasformations.trasformations import saturation, saturation_hill
from cassandra.budgetAllocator.utils import get_opt_algoritm
import warnings



def budget_allocator(df, name_date_column, medias, all_features, model, spends, response_get_budget,
                     lower_bounds, upper_bounds, df_aggregated, df_all_decomp, date_get_budget, maxeval,
                     saturation_type='hill', algoritm='LD_MMA', number_tail=15):
    warnings.filterwarnings("ignore")

    def getVals(df, name_date_column, all_features, date_get_budget='', number_tail=number_tail):
        if date_get_budget:
            get_vals_df = df.copy()
            get_vals_df.drop(get_vals_df[get_vals_df[name_date_column] > date_get_budget].index)
            full_row = pd.DataFrame(get_vals_df.tail(number_tail).mean()).T
        else:
            full_row = df.tail(number_tail).mean()

        row = full_row[all_features].copy()

        return row

    def getResp(df_all_decomp, name_date_column, all_features, date_get_budget='', number_tail=number_tail):
        if date_get_budget:
            get_vals_df = df_all_decomp.copy()
            get_vals_df.drop(get_vals_df[get_vals_df[name_date_column] > date_get_budget].index)
            full_row = pd.DataFrame(get_vals_df.tail(number_tail).mean()).T
        else:
            full_row = df_all_decomp.tail(number_tail).mean()

        row = full_row[all_features].copy()

        return row

    def myFunc(x, grad=[]):

        data = {}

        if saturation_type == 'hill':
            for m in medias:
                data[m] = [saturation_hill(x[medias.index(m)], df_aggregated.loc[
                    df_aggregated['canale'] == m, 'saturation_alpha'].iloc[0], df_aggregated.loc[
                                               df_aggregated['canale'] == m, 'saturation_gamma'].iloc[0])]
        else:
            for m in medias:
                data[m] = [saturation(x[medias.index(m)], df_aggregated.loc[
                    df_aggregated['canale'] == m, 'saturation_theta'].iloc[0])]

        dic = pd.DataFrame.from_dict(data)

        new_df = getVals(df, name_date_column, all_features, date_get_budget, number_tail).copy()

        for column in dic:
            new_df[column] = dic[column].iloc[0]

        return model.predict(new_df)[0]

    opt = get_opt_algoritm(algoritm, medias, lower_bounds, upper_bounds, spends, maxeval, myFunc)

    budget_spends = opt.optimize(spends)

    # THIS PART IS A TEST
    new_resp_df = getResp(df_all_decomp, name_date_column, all_features, date_get_budget, number_tail)
    new_resp_pred_df = pd.DataFrame()

    if saturation_type == 'hill':
        for m in medias:
            new_resp_pred_df[m] = [saturation_hill(budget_spends[medias.index(m)],
                                                   df_aggregated.loc[
                                                       df_aggregated['canale'] == m, 'saturation_alpha'].iloc[0],
                                                   df_aggregated.loc[
                                                       df_aggregated['canale'] == m, 'saturation_gamma'].iloc[0])]
    else:
        for m in medias:
            new_resp_pred_df[m] = [saturation(budget_spends[medias.index(m)],
                                              df_aggregated.loc[df_aggregated['canale'] == m, 'saturation_theta'].iloc[
                                                  0])]

    budget_allocator_df = pd.DataFrame()
    budget_allocator_df['canale'] = medias
    for index, row in budget_allocator_df.iterrows():
        budget_allocator_df.at[index, 'actual_spend'] = round(spends[index], 2)
        budget_allocator_df.at[index, 'optimal_spend'] = round(budget_spends[index], 2)
        budget_allocator_df.at[index, 'actual_response'] = round(new_resp_df[row['canale']][0],
                                                                 2)  # df_aggregated.loc[index, 'xDecompAgg']
        budget_allocator_df.at[index, 'optimal_response'] = round(
            new_resp_pred_df[row['canale']][0] * df_aggregated.loc[index, 'coef'],
            2)  # budget_spends[index] * df_aggregated.loc[index, 'coef']
        budget_allocator_df.at[index, 'actual_total_spend'] = round(np.sum(spends), 2)
        budget_allocator_df.at[index, 'optimal_total_spend'] = round(np.sum(budget_spends), 2)
        budget_allocator_df.at[index, 'actual_total_response'] = round(new_resp_df.sum(axis=1)[0],
                                                                       2)  # response_get_budget
        budget_allocator_df.at[index, 'optimal_total_response'] = round(opt.last_optimum_value(), 2)

    return budget_allocator_df

    # def getVals(df, name_date_column, all_features, date_get_budget):

    # full_row = df.loc[df[name_date_column] == date_get_budget]
    # print(full_row)
    # row = full_row[all_features].copy()
    # print(row)

    # return row
