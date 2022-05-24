from pandas import read_csv

def FPLdata():
    '''
    Read in the weekly-updated Fantasy Premier League football data from the
    GitHub repository https://github.com/andrewl776/fplmodels. Returns a dataframe
    (`pandas.core.frame.DataFrame`).

    The function takes no arguments.

    Example:
    from pyFPLdata import FPLdata
    FPLdata()
    '''
    fpl_data = read_csv("https://raw.githubusercontent.com/andrewl776/fplmodels/master/data/players_by_gameweek_csv.csv")
    fpl_data = fpl_data.dropna(axis = 0, subset=["next_gw_points"])
    return(fpl_data)