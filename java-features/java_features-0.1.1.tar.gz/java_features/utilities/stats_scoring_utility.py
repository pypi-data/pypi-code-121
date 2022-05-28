"""Scoring Utility is a module that supports the feature calculation and fundamental 
calculations for similarities scoring.
"""


import numpy as np


#################
# Stats Scoring #
#################


# Statistic Feature for Tokens Sequence Length
PERCENTILES_DEFINE_TOKEN = [5,10,15,20]
PERCENTILE_TOKENS_ALL = []
PERCENTILE_TOKENS_LABEL = []


# Statistic Feature for Main Feature + Style Feature
# determine feature names that will have the percentile feature
ADD_PERCENTILE_FEATURE_COLS = ['CSS','CLTS','CSA','BS','WS','CS','CSSA','CLN','CBLN','CBLN80']
PERCENTILES_DEFINE_FEATURE = [85,90,95]
PERCENTILES_FEATURE_VALUE = []

USED_MAIN_FEATURES = []

def initialize_stats_config(percentiles_define_token, add_percentile_feature_cols, percentiles_define_feature, used_main_features):
    """Initialize for statistics related features config.

    Args:
        percentiles_define_token (list): Percentiles to calculate 'token_less_{percentile}' feature
        add_percentile_feature_cols (list): Column names that will be calculated for '{feature}_more_{percentile}' feature
        percentiles_define_feature (list): Percentiles to calculate '{feature}_more_{percentile}' feature
        used_main_features (list): All used main features

    Returns:
        list: Contains elements from the text

    """
    global PERCENTILES_DEFINE_TOKEN, ADD_PERCENTILE_FEATURE_COLS, PERCENTILES_DEFINE_FEATURE, USED_MAIN_FEATURES

    PERCENTILES_DEFINE_TOKEN = percentiles_define_token
    ADD_PERCENTILE_FEATURE_COLS = add_percentile_feature_cols
    PERCENTILES_DEFINE_FEATURE = percentiles_define_feature
    USED_MAIN_FEATURES = used_main_features

    for i in PERCENTILES_DEFINE_TOKEN:
        p_token_label = f'tokens_less_{str(i).zfill(2)}'
        PERCENTILE_TOKENS_LABEL.append(p_token_label)


def initialize_tokens_percentile(main_codes_df):
    """Initialize specified percentile value for tokens sequence length.

    Args:
        main_codes_df (pandas.DataFrame): Dataframe that contains code information.
            Processed after "build_style_sequence" function

    Returns:
        None

    """
    global PERCENTILE_TOKENS_ALL
    PERCENTILE_TOKENS_ALL = []
    for p_token in PERCENTILES_DEFINE_TOKEN:
        percentile = np.percentile(main_codes_df['sequence_len'], p_token)
        PERCENTILE_TOKENS_ALL.append(percentile)


def build_token_stats_features(result_scoring_df, main_codes_df):
    """Build token statistics features.

    This function will add new statistic feature columns for tokens length.
    The purpose of these stats feature are to find false positive from small / short codes.
    Token length that is shorter than percentile value N will be marked as True, otherwise False.

    Args:
        result_scoring_df (pandas.DataFrame): Dataframe that contains scoring results.
            Processed after "create_features_result_df" function
        main_codes_df (pandas.DataFrame): Dataframe that contains code information.
            Processed after "build_style_sequence" function

    Returns:
        None

    """
    
    all_token_features = []
    
    for index, content in result_scoring_df[['Filename 1', 'Filename 2']].iterrows():
        filename1 = content['Filename 1']
        filename2 = content['Filename 2']
        
        seq_1 = main_codes_df[main_codes_df['filename'] == filename1]['sequence'].values[0]
        len_seq_1 = len(seq_1)

        seq_2 = main_codes_df[main_codes_df['filename'] == filename2]['sequence'].values[0]
        len_seq_2 = len(seq_2)

        if ('TCA' in USED_MAIN_FEATURES):
            average_tokens_between = [np.average([len_seq_1, len_seq_2])]
        else:
            average_tokens_between = []
        
        if('TCD' in USED_MAIN_FEATURES):
            diff_tokens_between = [abs(len_seq_2 - len_seq_1)]
        else:
            diff_tokens_between = []

        # build percentile feature to detect outlier of false positive (high similairty score but not plag because of skeleton file / short file)
        # if either one of the code satisified the condition, then it's counted as a true 
        # (because if code1 is shorter and code2 is longer, the pair will have high score if most parts of code1 exists in code2)
        percentile_tokens_bools = []
        for percentile_val in PERCENTILE_TOKENS_ALL:

            if len_seq_1 <= percentile_val or len_seq_2 <= percentile_val:
                percentile_tokens_bools.append(True)
            else:
                percentile_tokens_bools.append(False)

        current_data =  average_tokens_between + diff_tokens_between + percentile_tokens_bools
        
        all_token_features.append(current_data)
    
    token_features_name = []
    if ('TCA' in USED_MAIN_FEATURES):
        token_features_name.append('TCA')
    
    if ('TCD' in USED_MAIN_FEATURES):
        token_features_name.append('TCD')

    for label in PERCENTILE_TOKENS_LABEL:
        token_features_name.append(label)
    
    if(len(token_features_name) > 0):
        result_scoring_df[token_features_name] = all_token_features


def initialize_features_percentile(result_scoring_df):
    """Initialize specified percentile value for specified main features and style features.

    Args:
        result_scoring_df (pandas.DataFrame): Dataframe that contains scoring results.
            Processed after "create_features_result_df" function

    Returns:
        None

    """

    used_columns = ADD_PERCENTILE_FEATURE_COLS
    used_percentiles = PERCENTILES_DEFINE_FEATURE
    global PERCENTILES_FEATURE_VALUE
    PERCENTILES_FEATURE_VALUE = []

    for used_column in used_columns:
        for used_percentile in used_percentiles:
            percentile_value = np.percentile(result_scoring_df[used_column], used_percentile)
            PERCENTILES_FEATURE_VALUE.append(percentile_value)


def build_main_style_stats_features(result_scoring_df):
    """Build percentile features for main features and style features
    that specified in ADD_PERCENTILE_FEATURE_COLS.

    This function will add new statistic feature columns for them.
    The purpose of these stats features are to find outlier on scoring system that 
    tends to be the plagiarism pair.
    Feature value that is higher than percentile value N will be marked as True, otherwise False.

    Args:
        result_scoring_df (pandas.DataFrame): Dataframe that contains scoring results.
            Processed after "create_features_result_df" function

    Returns:
        None

    """
    all_percentile_feats = []

    if(len(ADD_PERCENTILE_FEATURE_COLS) == 0):
        return
    
    for i, content in result_scoring_df[ADD_PERCENTILE_FEATURE_COLS].iterrows():
        sims_list = content.values
        
        percentile_feats = []
        
        # loop through all score value (sim) and compare them with the pre-calculated percentile value
        for i, sim in enumerate(sims_list):
            for j in range(len(PERCENTILES_DEFINE_FEATURE)):
                
                # take percentile value from PERCENTILES_FEATURE_VALUE (starting from first index to last index)
                percentile_val = PERCENTILES_FEATURE_VALUE[i*len(PERCENTILES_DEFINE_FEATURE)+j]
                
                if(sim >= percentile_val):
                    percentile_feats.append(True)
                else:
                    percentile_feats.append(False)
                    
        
        all_percentile_feats.append(percentile_feats)
        
    
    percentile_features_name = []
    for feature in ADD_PERCENTILE_FEATURE_COLS:
        for percentile in PERCENTILES_DEFINE_FEATURE:
            label = f'{feature}_more_{percentile}'
            percentile_features_name.append(label)
    
    result_scoring_df[percentile_features_name] = all_percentile_feats
    
