#===============================================================================
# methylation_kde.py
#===============================================================================

import seaborn as sns

def methylation_kde(df, output_file, palette='mako_r'):
    """Draw a KDE plot of methylation levels

    Parameters
    ----------
    df
        input data frame of methylation levels
    output_file
        path to output file
    palette
        color palette for discrete methylation levels
    """

    ax = sns.kdeplot(data=df, x='Methylation level (%)',
                    hue='Discrete level', fill=True, palette=palette, cut=0)
    ax.set_xscale('log')
    fig = ax.get_figure()
    fig.set_figwidth(7)
    fig.set_figheight(3)
    fig.tight_layout()
    fig.savefig(output_file)
    fig.clf()