import pandas as pd
import numpy as np
import itertools
import string

import matplotlib.pyplot as plt
from matplotlib import colors

def ImportXls(FName:str):
    ftmp = pd.ExcelFile(FName)
    # extracting metadata information on number of replicates and measurements
    MetaDat = pd.read_excel(FName, ftmp.sheet_names[0])
    # Replicate number
    myReps = MetaDat.loc[MetaDat[MetaDat.columns[0]]=='Replicates:'][MetaDat.columns[1]].values.astype('int')
    # measurement points
    myMeas = MetaDat.loc[MetaDat[MetaDat.columns[0]]=='Measurements:'][MetaDat.columns[1]].values.astype('int')
    
    # extracting data from different sheets
    DataSheets = ftmp.sheet_names[1:]
    BiologAll = np.zeros([len(DataSheets),96])
    TimeVec = np.zeros([len(DataSheets)])
    for indx, DataSheet in enumerate(DataSheets):
        df = pd.read_excel(FName, sheet_name=DataSheet, header=None)
        Dtmp_arr = df.iloc[2:11,1:13].values
        Dtmp_vec = np.ndarray.flatten(Dtmp_arr)
        BiologAll[indx,:] = Dtmp_vec
        TimeVec[indx] = df.iloc[0,1]

    # calculating mean and std for replicates over all measurements
    BiologMean = np.zeros([int(myMeas), 96])
    BiologStdv = np.zeros([int(myMeas), 96])
    for Meas in range(int(myMeas)):
        Tindx = np.arange(Meas, Meas+myReps)
        BiologMean[Meas,:] = np.nanmean(BiologAll[Tindx,:], axis=0)
        BiologStdv[Meas,:] = np.nanstd(BiologAll[Tindx,:], axis=0)

    # # fancy rearrangement of columns to represent mean+std of each replicate
    # # https://stackoverflow.com/questions/20265229/rearrange-columns-of-numpy-2d-array
    Tvec = np.unique(TimeVec).reshape([-1,1])
    # Alpha = [let for let in string.ascii_uppercase[:8]]
    # Num = list(map(str,range(1,13)))
    Columns = WellIDs()
    Columns.insert(0,'Time_h')
    BiologMean_df = pd.DataFrame(data=np.hstack([Tvec,BiologMean]), columns=Columns)
    BiologStdv_df = pd.DataFrame(data=np.hstack([Tvec,BiologStdv]), columns=Columns)
    
    return BiologMean_df, BiologStdv_df
 

def VisualizeWell(myArr, plot_title=None, plot_z_name=None, export_file=None, cmap='viridis'):
    WellShape = np.reshape(myArr, (8,12))

    if cmap == 'discrete5':
#    https://stackoverflow.com/questions/9707676/defining-a-discrete-colormap-for-imshow-in-matplotlib
    	cmap = colors.ListedColormap(['orange', 'yellow', 'blue', 'green'])
#     	bounds = np.arange(0,5)

    plt.figure()
    im = plt.imshow(WellShape, interpolation='none', aspect='equal', cmap=cmap)
    plt.title(plot_title)
    plt.colorbar(label=plot_z_name)
    
    ax = plt.gca();
    
    # Major ticks
    ax.set_xticks(np.arange(0, 12, 1))
    ax.set_yticks(np.arange(0, 8, 1))
    
    # Labels for major ticks
    ax.set_xticklabels(np.arange(1, 13, 1))
    ylabel = [let for let in string.ascii_uppercase[:8]]
    ax.set_yticklabels(ylabel)
    
    # Minor ticks
    ax.set_xticks(np.arange(-.5, 12, 1), minor=True)
    ax.set_yticks(np.arange(-.5, 8, 1), minor=True)
    
    # Gridlines based on minor ticks
    ax.grid(which='minor', color='k', linestyle='-', linewidth=2)
    if export_file:
        plt.savefig(export_file)
    # # visualizing
    # x = np.arange(1,9)
    # y = [let for let in string.ascii_uppercase[:8]]
    # plt.yticks(x, y)
    # plt.imshow(WellShape, extent= [1, 12, 8, 1])
    plt.show()
    
def VisualizeWellSubstrate(myArr, PMIDs, PMTruth, plot_title=None, plot_z_name=None, export_file=None):
    WellShape = np.reshape(myArr, (8,12))

    plt.figure()
    im = plt.imshow(WellShape, interpolation='none', aspect='equal')
    plt.title(plot_title)
    plt.colorbar(label=plot_z_name)
    
    ax = plt.gca();
    
    # Major ticks
    ax.set_xticks(np.arange(0, 12, 1))
    ax.set_yticks(np.arange(0, 8, 1))
    
    # Labels for major ticks
    ax.set_xticklabels(np.arange(1, 13, 1))
    ylabel = [let for let in string.ascii_uppercase[:8]]
    ax.set_yticklabels(ylabel)
    
    # Minor ticks
    ax.set_xticks(np.arange(-.5, 12, 1), minor=True)
    ax.set_yticks(np.arange(-.5, 8, 1), minor=True)
    
    # Gridlines based on minor ticks
    ax.grid(which='minor', color='k', linestyle='-', linewidth=2)
    
    # loop over all wells to label them with substrate ids
    for indx, mypos in enumerate([[r[0],r[1]] for r in itertools.product(np.arange(8), np.arange(12))]):
        if PMTruth[indx]:
            plt.text(mypos[1], mypos[0], PMIDs[indx], va='center', ha='center', fontsize=8)
            
    if export_file:
        plt.savefig(export_file)
    plt.show()
    
def VisualizeConfMatrix(myList, export_file=None):
    OrdCount = list()
    for ordinal in range(4,0,-1):
        OrdCount.append(sum(myList==ordinal))
        
    OrdCount_rel = OrdCount/sum(OrdCount)
	# in PM_df the order of properties is:
	# 0: metabolite not in model
	# 1: Biolog-, iMod+
	# 2: Biolog+, iMod-
	# 3: Biolog-, iMod-
	# 4: Biolog+, iMod+
	# To visualize this as a confusion matrix, the elements 1-4 are normalized to their sum and rearranged as matrix with x-axis representing +,- for Biolog and y-axis +,- for iMod
    OrdCount_c = np.array([OrdCount[ConfIdx] for ConfIdx in [0,3,2,1]])
    plt.imshow(OrdCount_c.reshape(2,2))
    plt.xticks([0,1], ['True','False'])
    plt.xlabel('BIOLOG')
    plt.yticks([0,1], ['True','False'])
    plt.ylabel('iModel')
    for myNum in zip([[r[0],r[1]] for r in itertools.product(np.arange(2), np.arange(2))], OrdCount_c):
        print(myNum)
        plt.text(myNum[0][1], myNum[0][0], myNum[1], va='center', ha='center', fontsize=8)
    plt.title('Growth comparison for {} of {} substrates'.format(sum(OrdCount_c), len(myList)))
    if export_file:
        plt.savefig(export_file)
    plt.show()

 
def SlopeCalc(myArr, zero_max=False):
    '''
    Calculation of linear slopes. First column must be time. If desired ('zero_max' True) only the difference from zero to the last measurement is calculated.
    '''
    myTimes = myArr[:,0]
    myDat = np.delete(myArr,0,1)

    if zero_max:
        mySlope = myDat[-1,:]/myTimes[-1]
    else:
        mySlope = (myDat[1:,:] - myDat[:-1,:]) / np.tile((myTimes[1:]-myTimes[:-1]).reshape(-1,1),(1,myDat.shape[1]))
    
    return mySlope

def WellIDs():
    '''Generates the Well ids'''
    Alpha = [let for let in string.ascii_uppercase[:8]]
    Num = list(map(str,range(1,13)))
    return [r[0]+r[1] for r in itertools.product(Alpha, Num)]

def ConvertMatrixList(myList:list, dimension=[12,8]):
    '''
    Converting a 1D list which was generated from a matrix with stacked columns into a 1D list with stacked rows.

    Parameters
    ----------
    myList : list
        1D representation by stacked columns of matrix.
    dimension: list
        Dimension (columns, rows) of the original matrix. By default a 96-well plate with 12x8
    
    Returns
    -------
        1D representation of stacked rows.

    '''
    myList_matrix = np.array(myList).reshape(dimension)
    return list(np.transpose(myList_matrix).flatten())
