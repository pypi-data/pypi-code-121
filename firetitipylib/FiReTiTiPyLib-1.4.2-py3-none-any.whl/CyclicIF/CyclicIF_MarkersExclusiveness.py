import glob
import sys

import matplotlib.pyplot as plt
import numpy as np
import os
import pandas
import scipy
import seaborn

from . import CyclicIF_Utils as Utils



def DrawPlots(OutputDir: str, Scene: str, Features, FeatureNames, Target: str,
				FigSize: int, nCols: int, nRows: int, Density: bool=False):
	length = len(FeatureNames)
	
	figs, axs = plt.subplots(ncols=nCols, nrows=nRows, figsize=(FigSize * nCols, int(FigSize * length / nCols)))
	
	for j, feature2 in zip(range(length), FeatureNames):
		if Target != feature2:
			
			X = Features[[Target, feature2]]
			Indexes = X[(X[Target] < 5.0) | (X[feature2] < 5.0)].index
			X = X.drop(Indexes)
			
			if Density:
				values = np.vstack([X[Target], X[feature2]])
				kernel = scipy.stats.gaussian_kde(values)(values)
				plot = seaborn.scatterplot(data=X, x=Target, y=feature2, c=kernel,
											cmap="viridis", ax=axs[int(j / nCols), j % nCols])
			else:
				plot = seaborn.scatterplot(data=X, x=Target, y=feature2,
											cmap="viridis", ax=axs[int(j / nCols), j % nCols])
	
	#plt.savefig(OutputDir + "/Scene " + Scene + " - " + feature1 + ".pdf", format="pdf", dpi=150)
	plt.savefig(OutputDir + "/Scene " + Scene + " - " + Target + ".png", dpi=100)
	#figs.savefig(OutputDir + "/Scene " + Scene + " - " + feature1 + ".png", dpi=150)
	#figs.savefig(OutputDir + "/Scene " + Scene + " - " + featrue1 + ".pdf", format="pdf", dpi=150)
	#plt.show()
	plt.clf()
	plt.close(figs)



def PlotPairs(FeaturesDir: str, Scene: str, FigureSize: int=6, Density: bool=False, Marker: str=None):
	Features = pandas.read_csv(FeaturesDir + "/Scene " + str(Scene) + " - Mean Intensities.csv")
	Features = Features.drop(0)
	#ColumnNames = list(Features.columns)
	MarkersMasks = Features.columns.str.contains('Nuclei|Rings|Rims|Cells')
	Markers = Features.columns[MarkersMasks]
	length = len(Markers)
	ncols = 4
	nrows = int(length / ncols) + (0 if length % ncols == 0 else 1)
	
	if Marker is None:
		for i in range(length):
			print(' - Ploting scene ' + str(Scene) + ' - ' + Markers[i])
			DrawPlots(FeaturesDir + "/Scene " + Scene + " - Markers Excelusiveness/", Scene, Features, Markers, i,
						FigureSize, ncols, nrows, Density)
		print('Scene ' + str(Scene) + ' done.')
	else:
		TargetsMasks = Features.columns.str.contains(Marker)
		Targets = Features.columns[TargetsMasks]
		if Targets.empty:
			raise Exception("Cannot find marker '" + str(Marker) + "'.")
		#TargetsColumns = [Features.columns.get_loc(t) for t in Targets]
		for name in Targets:
			print(' - Ploting scene ' + str(Scene) + ' - ' + name)
			DrawPlots(FeaturesDir + "/Scene " + Scene + " - Markers Excelusiveness/", Scene, Features, Markers, name,
						FigureSize, ncols, nrows, Density)
		print('Scene ' + str(Scene) + ' done for marker ' + str(Marker) + '.')



def PlotExclusiveness(Path: str, FigureSize: int=6, Density: bool=False, Marker: str=None):
	csv = glob.glob(Path + "/*.csv")
	Scenes = Utils.FindScenesInCSV(csv, True)
	for scene in Scenes:
		os.makedirs(Path + "/Scene " + scene + " - Markers Excelusiveness/", exist_ok=True)
		PlotPairs(Path, scene, FigureSize, Density, Marker)



if __name__ == '__main__':
	#dir = "/Users/firetiti/NetBeans/FiReTiTiLiB/Test - 2048x2048 - Features/"
	dir = "/Users/firetiti/NetBeans/FiReTiTiLiB/Test - 4096x4096 - Features/"
	#dir = "/Users/firetiti/Downloads/CyclicIF/Features Tests/Koei/WO-394 - Top - Features/"
	#dir = "/Users/firetiti/Downloads/CyclicIF/Features Tests/Koei/WO-406 - Features/"
	#dir = "/Users/firetiti/Downloads/CyclicIF/Features Tests/Zeynep/not_registered/38592-6 - Features/"
	#dir = "/Users/firetiti/Downloads/CyclicIF/Features Tests/Zeynep/not_registered/48411-6 - Features/"
	
	try:
		PlotExclusiveness(dir, Marker="B7H6")
	except Exception as ex:
		print(ex)
		sys.exit(1)
	
	sys.exit(0)
	
	print('All done.')
