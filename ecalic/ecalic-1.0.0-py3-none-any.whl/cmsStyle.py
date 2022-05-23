import matplotlib.pyplot as plt
import os

plt.style.use(os.path.dirname(__file__) + '/data/fStyle.mplstyle')

def polishPlot( ax, xTitle=None, yTitle=None,
                legTitle = None, legLoc = 'upper left',
                prelim = True, simu = False, year = None, lumi = None,
                xRange = None, yRange= None ):
    if legTitle != None:
        leg = ax.legend(title=legTitle,loc=legLoc)
        plt.setp(leg.get_title(),fontsize='x-large')

    if xRange: ax.set_xlim(xRange[0],xRange[1])
    if yRange: ax.set_ylim(yRange[0],yRange[1])

    if yTitle != None: ax.set_ylabel( yTitle, ha = 'right', y = 1)
    if xTitle != None: ax.set_xlabel( xTitle, ha = 'right', x = 1)

    logo = 'CMS'
    if simu   : logo += ' $Simulation$'
    if prelim : logo += ' $Preliminary$'
    if year != None: logo += ' ' + str(year)
    ax.set_title( logo, loc='left', fontweight='bold')

    if lumi != None:
        ax.set_title('%2.1f fb$^{-1}$ (13 TeV)' % lumi , loc='right')

def ecalModuleBoundaries( ax ):
        for xmodule in [-85,-65,-45,-25,0,25,45,65,85]:
            ax.axvline(xmodule, color = 'k', linestyle = '--')
