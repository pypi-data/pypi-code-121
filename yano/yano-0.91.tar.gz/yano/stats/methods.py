from scipy import stats

def sign_test(a,b):
    """
    Performs a sign test on the data.
    """
    assert len(a) == len(b), "only the same number of elements can be compared"
    if a==b:return 1.0
    return stats.wilcoxon(a,b).pvalue



