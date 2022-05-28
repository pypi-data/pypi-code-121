"""Scoring Utility is a module that supports the feature calculation and fundamental 
calculations for similarities scoring.
"""


from Levenshtein import ratio
import re
import copy

import operator as op
from functools import reduce
from collections import defaultdict
from gst_calculation import gst

SAME_LINE_LENGTH = 0
SAME_SEQUENCE_LENGTH = 0


##############################
# Style Scoring Fundamentals #
##############################


def consume_mostleft_space(line):
    """Consumes mostleft space to count spaces.

    Args:
        line (str): A line from a code.

    Returns:
        tuple: Contains line, spaces_count.
            line = cleaned line from mostleft space (str)
            spaces_count = count of how many space character (int)

    """
    spaces_count = 0
    for index in range(len(line)):
        char = line[index]
        if(char != ' '):
            
            # remove mostleft space character (" ") from the line
            line = line[index:]
            return (line, spaces_count)
        
        spaces_count += 1
    return (line, spaces_count)


def determine_indent_sequence(space_count):
    """Determine indent sequence and return it.

    Args:
        space_count (int): Count of spaces (" ").

    Returns:
        list: Sequence of indents (consist of number 1).

    """
    if space_count % 4 == 0:
        return [1] * (space_count // 4)
    elif space_count % 2 == 0:
        return [1] * (space_count // 2)
    else:
        # if not 2/4 multiples, then indent counted as 1 space
        return [1] * space_count


BRACES_CHARS_COMPILE = re.compile('[{}]')
def brace_check(char, current_position, line_length):
    """Checking brace symbol and it's number from the predefined rules.
    It will return sequence of brace and number symbol depending on the brace location.
    These are the numbers that will be used for the sequence with corresponding location rule:
    - 1 = Brace on the mostleft line
    - 2 = Brace on the mostright line 
    - 3 = Brace on the middle of line
    - 4 = Brace on the line by itself

    Args:
        char (str): Brace character.
        current_position (int): The position / index that the brace was found.
        line_length (int): Total characters in the line.

    Returns:
        list: Sequence of braces and it's number.

    """
    result = BRACES_CHARS_COMPILE.findall(char)
    if (len(result) > 0):
        if (line_length == 1):
            return [char,4]
        elif (current_position == 0):
            return [char,1]
        elif (current_position == line_length-1):
            return [char,2]
        else:
            return [char,3]
    
    return []


def check_charbychar(line):
    """Checking character by character on the line of a code.
    This function is to compile comments sequence and braces sequence.

    Args:
        line (str): Line of a code.

    Returns:
        tuple: Contains line_comments_seq, line_braces_seq.
            line_comments_seq = Comment sequence on a line (list)
            line_braces_seq = Braces sequence on a line (list)

    """
    line = line.replace(' ','')
    line_length = len(line)
    
    line_comments_seq = []
    line_braces_seq = []
    
    if(line_length == 0):
        return line_comments_seq, line_braces_seq
    
    current_position = 0
    while True:
        char = line[current_position]
        
        # ============== COMMENT CHECK SECTION ==============
        # check single line comment
        if (char == '/'):
            # check if next char is also '/'
            try:
                if (line[current_position+1] == '/'):
                    current_position += 2

                    # comment at a newline
                    if(current_position == 2):
                        line_comments_seq.append(1)

                    # comment after a code
                    else:
                        line_comments_seq.append(2)
            except:
                break
                
        
        #stopping condition
        if(current_position >= line_length):
            break
        char = line[current_position]
        
        
        #check ending of multi line comment
        if (char == '*'):
            # check if next char is also '/'
            try:
                if (line[current_position+1] == '/'):
                    current_position += 2
                    line_comments_seq.append(3)
            except:
                break
        
        # ============================
        
        #stopping condition
        if(current_position >= line_length):
            break
        char = line[current_position]
        
        
        # ========== BRACES CHECK SECTION ===========
        brace_check_result = brace_check(char, current_position, line_length)
        line_braces_seq += brace_check_result
        
        #stopping condition
        if(current_position >= line_length - 1):
            break
        
        current_position += 1
    return line_comments_seq, line_braces_seq




##################################
# Same Segments Nerf Calculation #
##################################


def ncr(n, r):
    """Combination calculation nCr.
    The method of selection of 'r' objects from a set of 'n' objects
    where the order of selection does not matter.

    Args:
        n (int): numerator, count of n objects.
        r (int): denominator, count of selection.

    Returns:
        int: Combination result.

    """
    r = min(r, n-r)
    numer = reduce(op.mul, range(n, n-r, -1), 1)
    denom = reduce(op.mul, range(1, r+1), 1)
    return numer // denom 


def dup_segment_counter(main_codes_df):
    """Code duplicated segment counter.
    This function will loop through all combination of pairs between all codes.
    It will use greedy string tiling to count pattern that have more than 5 tiles.

    Args:
        main_codes_df (pandas.DataFrame): Taken from init dataframe.

    Returns:
        dict: Contains pattern as key and count as value.
            Pattern is a list of tokens that are converted into a string.

    """
    duplicate_segments_counter = defaultdict(int)
    for i in range(len(main_codes_df)):
        for j in range(i+1, len(main_codes_df)):
            data_l = main_codes_df.iloc[i]
            data_r = main_codes_df.iloc[j]

            filename_l = data_l['filename']
            filename_r = data_r['filename']

            sequence_lines_l = data_l['sequence_line']
            sequence_lines_r = data_r['sequence_line']

            result = gst.calculate(sequence_lines_l, sequence_lines_r, minimal_match=3)

            # store matched segments that consists of >= 5 lines
            # (if > 50% of the comparison contains that segment, consider that as the base skeleton, don't calculate the similarity from that block)

            same_segments = result[0]
            total_same_lines = result[1]

            for same_segment in same_segments:
                score = same_segment['score']
                if score >= 5:
                    start_pos_l = same_segment['token_1_position']
                    start_pos_r = same_segment['token_2_position']
                    end_pos_l = start_pos_l + same_segment['length']
                    end_pos_r = start_pos_r + same_segment['length']
                    duplicate_l = sequence_lines_l[start_pos_l:end_pos_l]
                    duplicate_segments_counter[str(duplicate_l)] += 1
    
    return duplicate_segments_counter


# minimal fraction of submission pair that must have same pattern to make that pattern considered to be a duplicate pattern
MINIMAL_PAIR_HAVE_SAME_SEGMENT = 0.25
def filter_dup_segment(main_codes_df, duplicate_segments_counter, minimal_pair_have_same_segment=0.25):
    """Filter duplicate segments from all duplicate_segments_counter.
    The default assumption for a valid duplicate segment is 
    atleast 25% of code pairs have the same pattern.
    
    Sample calculation:
    If there are submission of 220 codes, The filter will need atleast 
    25% * 220 = 55 submissions have the same pattern. 
    It's about 1485 pairs (55C2) having the same pattern accross all of the submissions.

    Args:
        main_codes_df (pandas.DataFrame): Taken from init dataframe.
        duplicate_segments_counter (dict): Contains pattern as key and count as value.
            Pattern is a list of tokens that are converted into a string.
        minimal_pair_have_same_segment: Minimum percentage of code pairs having the same pattern
            (for that pattern to be considered as a duplicate pattern / skeleton code)

    Returns:
        dict: Contains pattern as key and count as value.
            Pattern is a list of tokens that are converted into a string.
            Already filtered using lower bound counted using minimal_pair_have_same_segment.

    """
    all_submission_len = len(main_codes_df)
    minimal_submissions_same_pattern = int(minimal_pair_have_same_segment * all_submission_len)
    minimal_pairs_same_pattern = ncr(minimal_submissions_same_pattern, 2)
    sorted_dups = dict(sorted(duplicate_segments_counter.items(), key=lambda item: item[1], reverse=True))
    
    # total_pairs_count = 0
    all_duplicate_line_sequences = []
    for key,val in list(sorted_dups.items())[:20]:
        if(val > minimal_pairs_same_pattern):
            key_list = eval(key)
            all_duplicate_line_sequences.append(key_list)
        else:
            break
    
    # sort from the lengthiest one, check every pattern from the longest one
    all_duplicate_line_sequences = sorted(all_duplicate_line_sequences, key=len, reverse=True)
    
    return all_duplicate_line_sequences


def count_duplicate_patterns(sequence_l, sequence_r, all_duplicate_line_sequences):
    """Count duplicate pattern between two sequence.

    Args:
        sequence_l (str): tokens sequence of code 1.
        sequence_r (str): tokens sequence of code 2.
        all_duplicate_line_sequences (dict): The product of filter_dup_segment.

    Returns:
        None

    """
    sequence_l_copy = copy.deepcopy(sequence_l)
    sequence_r_copy = copy.deepcopy(sequence_r)
    global SAME_LINE_LENGTH, SAME_SEQUENCE_LENGTH
    SAME_LINE_LENGTH = 0
    SAME_SEQUENCE_LENGTH = 0
    
    for duplicate_line_sequence in all_duplicate_line_sequences:    
        # combine patterns to a single string, determine if the string of token sequence is exist in both of the code
        # if it exists, add the penalty
        dup_combined = ''.join(duplicate_line_sequence).strip()
        
        if(dup_combined in sequence_l_copy and dup_combined in sequence_r_copy):
            sequence_l_copy = sequence_l_copy.replace(dup_combined,'')
            sequence_r_copy = sequence_r_copy.replace(dup_combined,'')
            dup_line_len = len(duplicate_line_sequence)
            dup_combined_len = len(dup_combined)
            SAME_LINE_LENGTH += dup_line_len
            SAME_SEQUENCE_LENGTH += dup_combined_len




#############################
# Main Scoring Fundamentals #
#############################


def lev_ratio(sequence_l, sequence_r):
    """Will do a calculation of levenshtein ratio based on minimal levenshtein distance.
    Operation of delete and insertion have a cost of 1, while substitution operation has a cost of 2.
    The final ratio is calculated with: total_cost / (length of sequence_l + length of sequence_r)

    Args:
        sequence_l (str): The string sequence 1.
        sequence_r (str): The string sequence 2.

    Returns:
        float: Rounded to 4 precision of levenshtein ratio.

    """
    return round(ratio(sequence_l, sequence_r), 4)


def __extract_scores_generator(line, sequence_line, scorer=lev_ratio):
    for line_r in sequence_line:
        yield (line_r, scorer(line, line_r))


def extract_best(line, sequence_line, scorer=lev_ratio):
    """Extract best score from comparing a sequence and list of sequences.
    The default scorer is levenshtein ratio. Any kind string similarity scorer that
    have 2 parameter of string and return a float/int score would work.

    Args:
        line (str): A string for base comparison.
        sequence_line (list): A list of strings that functions as target comparison.

    Returns:
        tuple: Best Score that contains line_compare, score
            line_compare = The target line that compared to base line (base comparison)
            score = The score / similarity between line and line_compare

    """
    all_datas = __extract_scores_generator(line, sequence_line)
        
    return max(all_datas, key=lambda x: x[1])


def generate_bigram_lines(lines):
    """Produces bigram line sequence from list of lines.

    Args:
        lines (list): A list of tokenized code lines.

    Returns:
        list: Converted lines into a bigram lines sequence.

    """
    if(len(lines) <= 1):
        return lines
    lines_bigram = []
    for i in range(len(lines)-1):
        lines_bigram.append(lines[i]+lines[i+1])
    return lines_bigram



########################
# Scoring Calculations #
########################


def calculate_css(sequence_l, sequence_r, nerf=False):
    """Calculate Code Structure Similarity.
    Code Structure Similarity (CSS) use levenshtein ratio for 
    scoring / similarity between two string sequence.

    Args:
        sequence_l (str): tokens sequence of code 1
        sequence_r (str): tokens sequence of code 2
        nerf (bool): If set to True, the score will be nerfed 
            (same segment / duplicate segment nerf calculation)

    Returns:
        float: Score between 0-1.

    """
    css = lev_ratio(sequence_l,sequence_r)
    
    if(nerf):
        reduce_score = (SAME_SEQUENCE_LENGTH * 2) / (len(sequence_l) + len(sequence_r))
        return max(css - reduce_score,0)
    return css


def calculate_clts(sequence_line_l,sequence_line_r, line_len_l, nerf=False, all_duplicate_line_sequences=None):
    """Calculate Code Line Tiles Similarity.
    Code Line Tiles Similarity (CLTS) use greedy string tiling for 
    scoring / similarity between two string sequence.

    Args:
        sequence_line_l (list): A list of code lines from code 1.
        sequence_line_r (list): A list of code lines from code 2.
        line_len_l (int): the lines length of shorter code (between code 1 and code 2)
        nerf (bool): If set to True, the score will be nerfed 
            (same segment / duplicate segment nerf calculation)
        all_duplicate_line_sequences (dict): The product of filter_dup_segment.

    Returns:
        float: Score between 0-1.

    """
    gst_calculate = gst.calculate(sequence_line_l,sequence_line_r,3)
    gst_score = gst_calculate[1]
    
    gst_tiles = []
    if nerf:
        gst_tiles = []
        for tile in gst_calculate[0]:
            tile_1_start = tile['token_1_position']
            tile_1_end = tile_1_start + tile['length']
            tile_code_1 = sequence_line_l[tile_1_start:tile_1_end]
            
            # if the tile doesn't exist in duplicate sequences, then append the tile (show the tile)
            if tile_code_1 not in all_duplicate_line_sequences:
                gst_tiles.append(tile)
                
    else:
        gst_tiles = gst_calculate[0]
    
    if nerf:
        clts = max((gst_score - SAME_LINE_LENGTH),0) / line_len_l
    else:
        clts = gst_score / line_len_l
    
    return max(clts,0), gst_tiles


def calculate_csa(css, clts):
    """Calculate Code Similarity Average.
    Code Similarity Average (CSA) averages between CSS and CLTS.

    Args:
        css (float): CSS Score
        clts (float): CLTS Score

    Returns:
        float: Score between 0-1.

    """
    csa = (css+clts)/2
    return csa


def calculate_cln(sequence_line_l, sequence_line_r, nerf=False):
    """Calculate Common Line Normalized.
    Common Line Normalized (CLN) will count the ratio of duplicated lines 
    between two sets of line sequences.

    Args:
        sequence_line_l (list): A list of code lines from code 1.
        sequence_line_r (list): A list of code lines from code 2.
        nerf (bool): If set to True, the score will be nerfed 
            (same segment / duplicate segment nerf calculation)

    Returns:
        float: Score between 0-1.

    """
    lensequence_line_l = len(set(sequence_line_l))
    lensequence_line_r = len(set(sequence_line_r))
    total_len = len(set(sequence_line_l)) + len(set(sequence_line_r))
    
    set_between = list(set(sequence_line_l) | set(sequence_line_r))
    union_size = len(set_between)
    
    if(nerf):
        duplicated_lines = max(total_len - union_size - SAME_LINE_LENGTH, 0)
    else:
        duplicated_lines = total_len - union_size
    
    CLN = duplicated_lines/min(lensequence_line_l,lensequence_line_r)
    return CLN


def calculate_cbln80(bigram_line_l, bigram_line_r, nerf=False):
    """Calculate Common Bigram Line Normalized 80.
    Common Bigram Line Normalized 80 (CBLN80) will calculate ratio of 
    bigram line sequence that has levenshtein ratio > 80%.

    Args:
        bigram_line_l (list): A list of bigram code lines from code 1.
        bigram_line_r (list): A list of bigram code lines from code 2.
        nerf (bool): If set to True, the score will be nerfed 
            (same segment / duplicate segment nerf calculation)

    Returns:
        float: Score between 0-1.

    """
    bigram_line_l_dup = copy.deepcopy(bigram_line_l)
    bigram_line_r_dup = copy.deepcopy(bigram_line_r)
    
    lenbigram_line_l_dup = len(bigram_line_l_dup)
    lenbigram_line_r_dup = len(bigram_line_r_dup)
    
    counter80 = 0
    counter85 = 0
    for i in range(len(bigram_line_l_dup)):
        
        if len(bigram_line_r_dup) == 0:
            break
        
        fuzz_result = extract_best(bigram_line_l_dup[i], bigram_line_r_dup)        
        
        if(fuzz_result[1] > 0.8):
            bigram_line_r_dup.remove(fuzz_result[0])
            counter80 += 1
            
        
    if(nerf):
        nerf_score = max((SAME_LINE_LENGTH - 1), 0)
        CBLN80 = max((counter80 - nerf_score),0) / lenbigram_line_l_dup
    else:
        CBLN80 = counter80 / lenbigram_line_l_dup
    return CBLN80