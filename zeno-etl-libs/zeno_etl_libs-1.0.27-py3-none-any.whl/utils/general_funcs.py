##################################
# month diff calculation
##################################

def month_diff(date_a, date_b):
    """
    This function returns month difference between calendar dates 'date_a' and 'date_b'
    """
    return 12 * (date_a.dt.year - date_b.dt.year) + (date_a.dt.month - date_b.dt.month)
