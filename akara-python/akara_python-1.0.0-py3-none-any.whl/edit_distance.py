def edit_distance(word1: str, word2: str) -> int:
    """ Calculates the Levenstein Distance between `word1` and `word2`.
    Args:
    ---
    - `word1`: The first word.
    - `word2`: The second word.

    Returns:
    ---
    The distance between `word1` and `word2`
    """
    num_cols = len(word1) + 1
    num_rows = len(word2) + 1

    memoize = [[None for c in range(num_cols)] for r in range(num_rows)]

    for col_idx in range(0, num_cols):
        memoize[0][col_idx] = col_idx

    for row_idx in range(0, num_rows):
        memoize[row_idx][0] = row_idx

    for row_idx in range(1, num_rows):
        for col_idx in range(1, num_cols):
            left_n = memoize[row_idx][col_idx-1]
            top_n = memoize[row_idx-1][col_idx]
            cross_n = memoize[row_idx-1][col_idx-1]

            neighbours = [left_n, top_n, cross_n]
            min_n = min(neighbours)

            if word1[col_idx-1] != word2[row_idx-1]:
                memoize[row_idx][col_idx] = min_n + 1
            else:
                memoize[row_idx][col_idx] = cross_n

    return memoize[num_rows-1][num_cols-1]
