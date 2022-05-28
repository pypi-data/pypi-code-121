"""FeaturesCalculation is a module that calculates all supported feature and compile all feature
into a one Dataframe.
The dataframe later can be used as a dataset that serves the purpose to create a machine learning model.
"""

import pandas as pd
import numpy as np
from gst_calculation import gst
import configparser

import sys
from os.path import dirname, abspath
utilities_dir = dirname(abspath(__file__)) +'\\utilities'
sys.path.append(utilities_dir)

from java_raw_tokenizer import tokenize
# preprocess and init functions
from main_utility import get_all_filepaths, preprocess, get_processed_code, generate_init_data
# style scoring
from scoring_utility import consume_mostleft_space, determine_indent_sequence, brace_check, check_charbychar, dup_segment_counter, filter_dup_segment
# main scoring
from scoring_utility import calculate_css, calculate_clts, calculate_csa, calculate_cln, calculate_cbln80, generate_bigram_lines, count_duplicate_patterns

from stats_scoring_utility import initialize_stats_config

# GLOBAL VARIABLES
STYLE_FEATURE_COLS = ['BS','WS','CS']

CONFIG_FROM_FILE = dict()
USED_MAIN_FEATURES = []
USED_STYLE_FEATURES = []

PERCENTILES_DEFINE_TOKEN = []

ADD_PERCENTILE_FEATURE_COLS = []
PERCENTILES_DEFINE_FEATURE = []



def default_config():
    """To set default config if no config file passed.

    Args:
        None

    Returns:
        None

    """
    global USED_MAIN_FEATURES, USED_STYLE_FEATURES, PERCENTILES_DEFINE_TOKEN, ADD_PERCENTILE_FEATURE_COLS, PERCENTILES_DEFINE_FEATURE

    USED_MAIN_FEATURES = ['CSS', 'CLTS', 'CSA', 'CSSA', 'CLN', 'CBLN', 'CBLN80', 'TCA', 'TCD']
    USED_STYLE_FEATURES = ['BS', 'WS', 'CS']

    PERCENTILES_DEFINE_TOKEN = [5,10,15]
    ADD_PERCENTILE_FEATURE_COLS = ['CSS','CLTS','CSA','BS','WS','CS','CSSA','CLN','CBLN','CBLN80']
    PERCENTILES_DEFINE_FEATURE = [85,90,95]


def read_ini(file_path):
    """Read and parse .ini config file. Data stored into CONFIG_FROM_FILE dictionary

    Args:
        file_path (str): File path of config (.ini) file.

    Returns:
        None

    """
    config = configparser.ConfigParser()
    config.read(file_path)
    for section in config.sections():
        for key in config[section]:
            CONFIG_FROM_FILE[key] = config[section][key]


def read_comma_separated(config_text, type=str):
    """Read and parse comma separated elements from config file.
    The parsed element will be converted according to specified type.
    All elements will be returned as list.

    Args:
        config_text (str): Text from config file that has comma separated structure.
        type (type): type of the element (supports all python basic types).

    Returns:
        list: Contains elements from the text

    """
    config_list = config_text.split(',')

    config_list = [x.strip() for x in config_list]
    
    if (len(config_list[0]) == 0):
        config_list = []
    config_list = [type(x) for x in config_list]

    return config_list


def initialize_config(config_filepath=None):
    """Initialize config for defining used features.

    Args:
        config_filepath (str): File path of config (.ini) file
            If set to None, then it will use the default config.

    Returns:
        tuple: Contains statistics configs, will be passed later to initialize stats config.

    """
    global USED_MAIN_FEATURES, USED_STYLE_FEATURES, PERCENTILES_DEFINE_TOKEN, ADD_PERCENTILE_FEATURE_COLS, PERCENTILES_DEFINE_FEATURE

    if (config_filepath == None):
        default_config()
        return PERCENTILES_DEFINE_TOKEN, ADD_PERCENTILE_FEATURE_COLS, PERCENTILES_DEFINE_FEATURE, USED_MAIN_FEATURES
    else:
        read_ini(config_filepath)
        config_keys = list(CONFIG_FROM_FILE.keys())

        # main features
        if 'use_main_features' in config_keys:
            USED_MAIN_FEATURES = read_comma_separated(CONFIG_FROM_FILE['use_main_features'])

        # style features
        if 'use_style_features' in config_keys:
            USED_STYLE_FEATURES = read_comma_separated(CONFIG_FROM_FILE['use_style_features'])

        # token stats
        if 'tokens_stats_percentile' in config_keys:
            PERCENTILES_DEFINE_TOKEN = read_comma_separated(CONFIG_FROM_FILE['tokens_stats_percentile'], int)
            
        # main feature stats
        if 'main_stats_names' in config_keys:
            ADD_PERCENTILE_FEATURE_COLS = read_comma_separated(CONFIG_FROM_FILE['main_stats_names'])
            
            # if there are some percentile feature for main feature
            if len(ADD_PERCENTILE_FEATURE_COLS) > 0:
                PERCENTILES_DEFINE_FEATURE = read_comma_separated(CONFIG_FROM_FILE['main_stats_percentile'], int)
        
        return PERCENTILES_DEFINE_TOKEN, ADD_PERCENTILE_FEATURE_COLS, PERCENTILES_DEFINE_FEATURE, USED_MAIN_FEATURES


def get_code_style_sequence(raw_code):
    """Compile all code style sequence.
    This function will compile all code style sequence (whiteline_sequence, braces_sequence, comments_sequence)
    It also calculates the newline symbol with number 2 for whiteline_sequence.

    Args:
        raw_code (str): Raw code.

    Returns:
        tuple: Contains line_comments_seq, line_braces_seq.
            line_comments_seq = Comment sequence on a line (list)
            line_braces_seq = Braces sequence on a line (list)

    """
    lines = raw_code.split('\n')
    
    whiteline_sequence = []
    braces_sequence = []
    comments_sequence = []
    
    # loop through every lines from the raw code and determine the whiteline, braces, and comments sequence
    for line in lines:
        #new line sequence
        whiteline_sequence.append(2)
        
        line, spaces_counter = consume_mostleft_space(line)
        indent_sequence = determine_indent_sequence(spaces_counter)
        
        whiteline_sequence += indent_sequence
        
        line_comments_seq, line_braces_seq = check_charbychar(line)
        comments_sequence += line_comments_seq
        braces_sequence += line_braces_seq
    
    return whiteline_sequence, braces_sequence, comments_sequence


def build_style_sequence(main_codes_df):
    """Add style sequences to the init DataFrame.

    Args:
        main_codes_df (pandas.DataFrame): Taken from init dataframe.

    Returns:
        None

    """

    if len(USED_STYLE_FEATURES) == 0:
        return
    
    all_styles = []
    
    for i, content in main_codes_df.iterrows():
        raw_code = content['raw_code']
        whiteline_sequence, braces_sequence, comments_sequence = get_code_style_sequence(raw_code)
        all_styles.append([braces_sequence, whiteline_sequence, comments_sequence])
        
    style_sequence_cols = []
    for label in USED_STYLE_FEATURES:
        label += '_sequence'
        style_sequence_cols.append(label)
    
    main_codes_df[style_sequence_cols] = all_styles


def calculate_style_feature(sequence_1, sequence_2):
    """Calculate style sequence using greedy string tiling algorithm.
    The accumulated score / tiles number will be divided with the 
    minimum length between the two sequence.

    Args:
        sequence_1 (list): style sequence 1.
        sequence_1 (list): style sequence 2.

    Returns:
        float: normalized score (between 0-1)

    """
    len_sequence_1 = len(sequence_1)
    len_sequence_2 = len(sequence_2)
    
    gst_styles = gst.calculate(sequence_1,sequence_2)
    total_score = gst_styles[1]
    
    # if style sequence minimum len is 0, then return 0 as the score
    min_len = min(len_sequence_1, len_sequence_2)
    
    if(min_len == 0):
        return 0
    else:
        return total_score / min_len


def calculate_main_features(sequence_line_l, sequence_l, sequence_line_r, sequence_r, line_len_l, same_segment_nerf=False, all_duplicate_line_sequences=None):
    """Compile all main features.

    Args:
        sequence_line_l (list): A list of code lines from code 1.
        sequence_l (str): tokens sequence of code 1.
        sequence_line_r (list): A list of code lines from code 2.
        sequence_r (str): tokens sequence of code 2.
        line_len_l (int): line length of the shorter lines (between code 1 and code 2).
        same_segment_nerf (bool): If set to True, the score will be nerfed 
            (same segment / duplicate segment nerf calculation).
        all_duplicate_line_sequences (dict): Contains pattern as key and count as value.
            Pattern is a list of tokens that are converted into a string.

    Returns:
        tuple: Contains all main features (css, clts, clts_dicts, csa, cln, cbln, cbln80)

    """
    if (same_segment_nerf):
        count_duplicate_patterns(sequence_l, sequence_r, all_duplicate_line_sequences)
    
    if ('CSS' in USED_MAIN_FEATURES):
        css = calculate_css(sequence_l, sequence_r, nerf=same_segment_nerf)
    else:
        css = None
    
    if ('CLTS' in USED_MAIN_FEATURES):
        clts, clts_dicts = calculate_clts(sequence_line_l, sequence_line_r, line_len_l, same_segment_nerf, all_duplicate_line_sequences)
    else:
        clts, clts_dicts = None, None
    
    if ('CSA' in USED_MAIN_FEATURES):
        csa = calculate_csa(css, clts)
    else:
        csa = 0
    
    if('CLN' in USED_MAIN_FEATURES):
        cln = calculate_cln(sequence_line_l, sequence_line_r, nerf=same_segment_nerf)
    else:
        cln = 0
    
    bigram_line_l = generate_bigram_lines(sequence_line_l)
    bigram_line_r = generate_bigram_lines(sequence_line_r)

    if('CBLN' in USED_MAIN_FEATURES):
        cbln = calculate_cln(bigram_line_l, bigram_line_r, nerf=same_segment_nerf)
    else:
        cbln = 0
    
    if('CBLN80' in USED_MAIN_FEATURES):
        cbln80 = calculate_cbln80(bigram_line_l, bigram_line_r, nerf=same_segment_nerf)
    else:
        cbln80 = 0
    
    return (css, clts, clts_dicts, csa, cln, cbln, cbln80)


def create_features_result_df(main_codes_df, same_segment_nerf = False, minimal_pair_have_same_segment=0.25, use_preprocessing=True):
    """Compile all main features and style features into a DataFrame.

    Args:
        main_codes_df (pandas.DataFrame): Taken from init dataframe.
        same_segment_nerf (bool): If set to True, the score will be nerfed 
            (same segment / duplicate segment nerf calculation)
        minimal_pair_have_same_segment (float): Minimum percentage of code pairs having the 
            same pattern (for that pattern to be considered as a duplicate pattern / skeleton code).
            Will be used by filter_dup_segment function.
        use_preprocessing (bool): If set to True, then the model will use preprocess for the
            features calculation, otherwise for False.

    Returns:
        pandas.DataFrame: Contains DataFrame for features result.

    """

    # handle if nerf features
    all_duplicate_line_sequences = None
    if same_segment_nerf:
        duplicate_segments_counter = dup_segment_counter(main_codes_df)
        all_duplicate_line_sequences = filter_dup_segment(main_codes_df, duplicate_segments_counter, minimal_pair_have_same_segment)

    features_data = []
    # start = time.time()
    for i in range(len(main_codes_df)):
        for j in range(i+1, len(main_codes_df)):
            code_data_l = main_codes_df.iloc[i]
            code_data_r = main_codes_df.iloc[j]

            filename_l = code_data_l['filename']

            if use_preprocessing:
                sequence_line_l = code_data_l['sequence_line']
                sequence_l = code_data_l['sequence']
            else:
                sequence_line_l = code_data_l['raw_sequence_line']
                sequence_l = code_data_l['raw_code']
            line_pos_l = code_data_l['line_pos']

            filename_r = code_data_r['filename']
            if use_preprocessing:
                sequence_line_r = code_data_r['sequence_line']
                sequence_r = code_data_r['sequence']
            else:
                sequence_line_r = code_data_r['raw_sequence_line']
                sequence_r = code_data_r['raw_code']

            line_pos_r = code_data_r['line_pos']

            # shortest length of line 
            if use_preprocessing:
                line_len_l = code_data_l['line_len']
            else:
                line_len_l = min(len(sequence_line_l), len(sequence_line_r))

            #WS feature
            if ('WS' in USED_STYLE_FEATURES):
                ws_sequence_l = code_data_l['WS_sequence']
                ws_sequence_r = code_data_r['WS_sequence']
                ws = calculate_style_feature(ws_sequence_l, ws_sequence_r)
            else:
                ws = 0
            
            #BS feature
            if('BS' in USED_STYLE_FEATURES):
                bs_sequence_l = code_data_l['BS_sequence']
                bs_sequence_r = code_data_r['BS_sequence']
                bs = calculate_style_feature(bs_sequence_l, bs_sequence_r)
            else:
                bs = 0

            #CS feature
            if('CS' in USED_STYLE_FEATURES):
                cs_sequence_l = code_data_l['CS_sequence']
                cs_sequence_r = code_data_r['CS_sequence']
                cs = calculate_style_feature(cs_sequence_l, cs_sequence_r)
            else:
                cs = 0

            #CSSA feature
            if('CSSA' in USED_STYLE_FEATURES):
                cssa = np.average([ws,bs,cs])
            else:
                cssa = 0

            shortest_tokens_length = len(sequence_l)
            if len(sequence_r) < shortest_tokens_length:
                shortest_tokens_length = len(sequence_r)

            css, clts, clts_dicts, csa, cln, cbln, cbln80 = calculate_main_features(
                sequence_line_l, sequence_l, sequence_line_r, sequence_r, line_len_l,
                same_segment_nerf, all_duplicate_line_sequences)
            current_data = (filename_l, filename_r, line_pos_l, line_pos_r, shortest_tokens_length, clts_dicts,
                            css, clts, csa, bs, ws, cs, cssa, cln, cbln, cbln80)
            features_data.append(current_data)
            # break
        # break
    
    columns = ['Filename 1', 'Filename 2', 'Line Pos 1', 'Line Pos 2', 'Shortest Token Length', 'CLTS Dicts',
               'CSS', 'CLTS', 'CSA', 'BS', 'WS', 'CS', 'CSSA', 'CLN', 'CBLN', 'CBLN80']
    result_scoring_df = pd.DataFrame(features_data, columns=columns)


    # adjust columns to only used features
    columns = ['Filename 1', 'Filename 2', 'Line Pos 1', 'Line Pos 2', 'Shortest Token Length']
    if ('CLTS' in USED_MAIN_FEATURES):
        columns += ['CLTS Dicts']

    columns += (USED_MAIN_FEATURES + USED_STYLE_FEATURES)

    # remove column names that will be calculated later
    try:
        columns.remove('TCD')
        columns.remove('TCA')
    except:
        pass

    result_scoring_df = result_scoring_df[columns]
    
    return result_scoring_df
