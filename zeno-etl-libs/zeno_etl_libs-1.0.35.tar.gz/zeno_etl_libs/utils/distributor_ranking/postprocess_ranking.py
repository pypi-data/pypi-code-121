import pandas as pd


def postprocess_ranking_dc(features_rank, volume_fraction):
    tech_input = features_rank.copy()
    # drop cases for tech input where all 3 distributor assigned are NULL.
    # Since they automatically need to go to dc drug type level.
    tech_input = tech_input[~((tech_input['final_dist_1'].isna()) & (
        tech_input['final_dist_2'].isna()) & (
                                  tech_input['final_dist_3'].isna()))]

    tech_input['final_dist_1'] = tech_input['final_dist_1'].fillna(
        tech_input['final_dist_2'])
    tech_input['final_dist_1'] = tech_input['final_dist_1'].fillna(
        tech_input['final_dist_3'])

    tech_input.loc[tech_input['final_dist_1'] ==
                   tech_input['final_dist_2'], 'final_dist_2'] = float('NaN')

    tech_input.loc[tech_input['final_dist_1'] ==
                   tech_input['final_dist_3'], 'final_dist_3'] = float('NaN')

    tech_input['final_dist_2'] = tech_input['final_dist_2'].fillna(
        tech_input['final_dist_3'])
    tech_input.loc[tech_input['final_dist_2'] ==
                   tech_input['final_dist_3'], 'final_dist_3'] = float('NaN')

    # append dc_drug_type entries as separate rows in tech input
    dc_drug_type_entries = features_rank[
        ['dc_id', 'drug_type', 'request_type', 'dc_drug_type_level_dist_1',
         'dc_drug_type_level_dist_2',
         'dc_drug_type_level_dist_3']].drop_duplicates().rename(
        columns={'dc_drug_type_level_dist_1': 'final_dist_1',
                 'dc_drug_type_level_dist_2': 'final_dist_2',
                 'dc_drug_type_level_dist_3': 'final_dist_3'
                 })

    dc_drug_type_entries['drug_id'] = float('NaN')

    dc_drug_type_entries['volume_fraction'] = volume_fraction

    dc_drug_type_entries = dc_drug_type_entries[
        ['dc_id', 'drug_id', 'drug_type', 'request_type', 'volume_fraction',
         'final_dist_1', 'final_dist_2', 'final_dist_3']]

    tech_input = pd.concat([tech_input, dc_drug_type_entries])

    # append enterprise_drug_type entries as separate rows in tech input
    enterprise_drug_type_entries = features_rank[
        ['drug_type', 'request_type', 'enterprise_drug_type_level_dist_1',
         'enterprise_drug_type_level_dist_2',
         'enterprise_drug_type_level_dist_3']].drop_duplicates().rename(
        columns={'enterprise_drug_type_level_dist_1': 'final_dist_1',
                 'enterprise_drug_type_level_dist_2': 'final_dist_2',
                 'enterprise_drug_type_level_dist_3': 'final_dist_3'})

    enterprise_drug_type_entries['dc_id'] = float('NaN')
    enterprise_drug_type_entries['drug_id'] = float('NaN')

    enterprise_drug_type_entries['volume_fraction'] = volume_fraction

    enterprise_drug_type_entries = enterprise_drug_type_entries[
        ['dc_id', 'drug_id', 'drug_type', 'request_type', 'volume_fraction',
         'final_dist_1', 'final_dist_2', 'final_dist_3']]

    tech_input = pd.concat([tech_input, enterprise_drug_type_entries])

    tech_input["store_id"] = float('NaN')
    tech_input["franchisee_id"] = 1 # ZIPPIN PHARMA
    tech_input = tech_input[['dc_id', 'store_id', 'franchisee_id', 'drug_id',
                             'drug_type', 'request_type', 'volume_fraction',
                             'final_dist_1', 'final_dist_2', 'final_dist_3']]

    tech_input = tech_input.drop_duplicates()

    return tech_input


def postprocess_ranking_franchisee(features_rank, volume_fraction):
    tech_input = features_rank.copy()
    # drop cases for tech input where all 3 distributor assigned are NULL.
    # Since they automatically need to go to store drug type level.
    tech_input = tech_input[~((tech_input['final_dist_1'].isna()) & (
        tech_input['final_dist_2'].isna()) & (tech_input['final_dist_3'].isna()))]

    tech_input['final_dist_1'] = tech_input['final_dist_1'].fillna(
        tech_input['final_dist_2'])
    tech_input['final_dist_1'] = tech_input['final_dist_1'].fillna(
        tech_input['final_dist_3'])

    tech_input.loc[tech_input['final_dist_1'] ==
                   tech_input['final_dist_2'], 'final_dist_2'] = float('NaN')

    tech_input.loc[tech_input['final_dist_1'] ==
                   tech_input['final_dist_3'], 'final_dist_3'] = float('NaN')

    tech_input['final_dist_2'] = tech_input['final_dist_2'].fillna(tech_input['final_dist_3'])
    tech_input.loc[tech_input['final_dist_2'] ==
                   tech_input['final_dist_3'], 'final_dist_3'] = float('NaN')

    tech_input = tech_input[['store_id', 'franchisee_id', 'drug_id', 'drug_type',
        'request_type', 'volume_fraction','final_dist_1', 'final_dist_2', 'final_dist_3']]

    # append store_drug_type entries as separate rows in tech input
    store_drug_type_entries = features_rank[
        ['store_id', 'franchisee_id', 'drug_type', 'request_type',
         'store_drug_type_level_dist_1', 'store_drug_type_level_dist_2',
         'store_drug_type_level_dist_3']].drop_duplicates().rename(
        columns={'store_drug_type_level_dist_1': 'final_dist_1',
                 'store_drug_type_level_dist_2': 'final_dist_2',
                 'store_drug_type_level_dist_3': 'final_dist_3'
                 })

    store_drug_type_entries['drug_id'] = float('NaN')

    store_drug_type_entries['volume_fraction'] = volume_fraction

    store_drug_type_entries = store_drug_type_entries[
        ['store_id', 'franchisee_id', 'drug_id', 'drug_type', 'request_type',
         'volume_fraction', 'final_dist_1', 'final_dist_2', 'final_dist_3']]

    tech_input = pd.concat([tech_input, store_drug_type_entries], sort=False)

    tech_input['dc_id'] = float('NaN')
    tech_input = tech_input[['dc_id', 'store_id', 'franchisee_id', 'drug_id',
                             'drug_type', 'request_type', 'volume_fraction',
                             'final_dist_1', 'final_dist_2', 'final_dist_3']]

    tech_input = tech_input.drop_duplicates()

    return tech_input

