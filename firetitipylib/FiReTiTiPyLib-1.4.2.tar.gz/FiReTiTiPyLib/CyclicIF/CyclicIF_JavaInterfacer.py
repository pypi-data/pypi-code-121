import os
import pandas
import sys


Java_Path = "java"
Javac_Path = "javac"


# ----------------------------------------------------- Cyclic IF -----------------------------------------------------
def Run(Parameters: dict, JavaJarsPath: str=None):
	""" This function calls the cyclic IF segmentation pipeline using the given parameters.
		Args:
			:param Parameters: A dictionary containing all the parameters.
			:param JavaJarsPath: .
	"""
	
	Keys = ['nbCPU', 'Experiment', 'Images_Directory', 'Python_Path', 'Java_Xms', 'Java_Xmx',
			'Registration_Technique', 'Registration_Reverse',
			'SegmentNuclei_RoundToSegment',
			'SegmentNuclei_Model', 'SegmentNuclei_BorderEffectSize', 'SegmentNuclei_BatchSize',
			'SegmentNuclei_CheckOverlap', 'SegmentNuclei_SaveNuclei', 'SegmentNuclei_Threshold',
			'SegmentCells_DilationRatio',
			'ExitAfterSegmentation', 'Background_Subtraction',
			'FE_SaveImages', 'FE_BiasedFeaturesOnly', 'FE_DistanceFromBorder',
			'Segmentation', 'Registration_And_Segmentation', 'FeaturesExtraction', 'QualityControl']
	
	for key in Parameters.keys():
		if key not in Keys:
			print("Unknown parameter: '" + key + "'", file=sys.stderr)
			print(*Keys, sep='\n')
			raise Exception("Unknown parameter: '" + key + "'")
	
	if JavaJarsPath is None:
		Java_ClassPath = "-classpath .:FiReTiTiLiB.jar:lib/*:."
	else:
		Java_ClassPath = "-classpath .:" + JavaJarsPath + "/FiReTiTiLiB.jar:" + JavaJarsPath + "/lib/*:."
	
	if 'Java_Xms' in Parameters and Parameters['Java_Xms'] is not None:
		if not isinstance(Parameters['Java_Xms'], str):
			raise Exception("Parameter 'Java_Xms' must be a string, '"
							+ str(Parameters['Java_Xms']) + "' found.")
		else:
			Java_Xms = Parameters['Java_Xms']
	else:
		Java_Xms = "8G"
	
	if 'Java_Xmx' in Parameters and Parameters['Java_Xmx'] is not None:
		if not isinstance(Parameters['Java_Xmx'], str):
			raise Exception("Parameter 'Java_Xmx' must be a string, '"
							+ str(Parameters['Java_Xmx']) + "' found.")
		else:
			Java_Xmx = Parameters['Java_Xmx']
	else:
		Java_Xmx = "12G"
	
	Java_Options = "-noverify -Xms" + Java_Xms + " -Xmx" + Java_Xmx
	
	
	
	java = open("cycIFAAP.java", "w")
	
	java.write('import softwares.ohsu.cyclicif.CyclicIF;\n')
	
	java.write('public class cycIFAAP\n')
	java.write('{\n\n')
	
	java.write('public static void main(String[] args) throws Exception\n')
	java.write('\t{\n')
	
	if 'nbCPU' not in Parameters: raise Exception("'nbCPU' parameter missing.")
	java.write('\tfinal int nbCPU = ' + str(Parameters['nbCPU']) + ' ;\n\n')
	
	if 'Python_Path' in Parameters and Parameters['Python_Path'] is not None:
		Python_Path = Parameters['Python_Path']
	else:
		Python_Path = os.path.join(os.__file__.split("lib/")[0], "bin", "python") #sys.executable
		if not os.path.exists(Python_Path):
			Python_Path = os.path.join(os.__file__.split("lib/")[0], "bin", "python3")  #sys.executable
			if not os.path.exists(Python_Path):
				raise Exception("Cannot automatically find python path. Use parameter 'Python_Path' to specify it.")
	java.write('\tfinal String Python_Path = "' + Python_Path + '" ;\n\n')
	
	if 'Images_Directory' not in Parameters:
		raise Exception("'Images_Directory' parameter missing.")
	java.write('\tfinal String PathToData = "' + Parameters['Images_Directory'] + '" ;\n\n')
	
	java.write('\tCyclicIF cif = new CyclicIF(20, Python_Path, nbCPU) ;\n\n')
	
	if 'Experiment' not in Parameters: raise Exception("Experiment type missing.")
	java.write('\tcif.Experiment = cif.' + Parameters['Experiment'] + ' ;\n')
	
	if 'Registration_Technique' in Parameters and Parameters['Registration_Technique'] is not None:
		if not isinstance(Parameters['Registration_Technique'], str):
			raise Exception("Parameter 'Registration_Technique' must be a string, '"
							+ str(Parameters['Registration_Technique']) + "' found.")
		else:
			java.write('\tcif.Registration = "%s" ;\n' % Parameters['Registration_Technique'])
	
	if 'Registration_Reverse' in Parameters and Parameters['Registration_Reverse'] is not None:
		if not isinstance(Parameters['Registration_Reverse'], bool):
			raise Exception("Parameter 'Registration_Reverse' must be a boolean, '"
							+ str(Parameters['Registration_Reverse']) + "' found.")
		elif Parameters['Registration_Reverse']:
			java.write('\tcif.Registration_Reverse = true ;\n')
		else:
			java.write('\tcif.Registration_Reverse = false ;\n')
	
	if 'SegmentNuclei_RoundToSegment' not in Parameters or Parameters['SegmentNuclei_RoundToSegment'] is None:
		java.write('\tcif.SegmentNuclei_RoundToSegment = "ZProjection" ;\n')
	elif not isinstance(Parameters['SegmentNuclei_RoundToSegment'], str):
		raise Exception("Parameter 'SegmentNuclei_RoundToSegment' must be a string, '"
						+ str(Parameters['SegmentNuclei_RoundToSegment']) + "' found.")
	else:
		java.write('\tcif.SegmentNuclei_RoundToSegment = "%s" ;\n' % Parameters['SegmentNuclei_RoundToSegment'])
	
	if 'SegmentNuclei_Model' not in Parameters or Parameters['SegmentNuclei_Model'] is None:
		raise Exception("Parameter 'SegmentNuclei_Model' (model name, string) must be defined.")
	elif not isinstance(Parameters['SegmentNuclei_Model'], str):
		raise Exception("Parameter 'SegmentNuclei_Model' (model name, string) must be a string, '"
						+ str(Parameters['SegmentNuclei_Model']) + "' found.")
	else:
		java.write('\tcif.SegmentNuclei_Model = "%s" ;\n' % Parameters['SegmentNuclei_Model'])
	
	if 'SegmentNuclei_BatchSize' not in Parameters or Parameters['SegmentNuclei_BatchSize'] is None:
		java.write('\tcif.SegmentNuclei_BatchSize = 3 ;\n')
	elif isinstance(Parameters['SegmentNuclei_BatchSize'], int) and 0 < Parameters['SegmentNuclei_BatchSize']:
		java.write('\tcif.SegmentNuclei_BatchSize = %d ;\n' % Parameters['SegmentNuclei_BatchSize'])
	else:
		raise Exception("Wrong value for parameter 'BatchSize', positive integer expected, '"
						+ str(Parameters['SegmentNuclei_BatchSize']) + "' found.")
	
	if 'SegmentNuclei_BorderEffectSize' not in Parameters or Parameters['SegmentNuclei_BorderEffectSize'] is None:
		java.write('\tcif.SegmentNuclei_BorderEffectSize = 73 ;\n')
	elif isinstance(Parameters['SegmentNuclei_BorderEffectSize'], int) \
		and 0 < Parameters['SegmentNuclei_BorderEffectSize']:
		java.write('\tcif.SegmentNuclei_BorderEffectSize = %d ;\n' % Parameters['SegmentNuclei_BorderEffectSize'])
	else:
		raise Exception("Wrong value for parameter 'SegmentNuclei_BorderEffectSize', positive integer expected, '"
						+ str(Parameters['SegmentNuclei_BorderEffectSize']) + "' found.")
	
	if 'SegmentNuclei_CheckOverlap' not in Parameters or Parameters['SegmentNuclei_CheckOverlap'] is None:
		java.write('\tcif.SegmentNuclei_CheckOverlap = 7 ;\n')
	elif isinstance(Parameters['SegmentNuclei_CheckOverlap'], int) and 0 < Parameters['SegmentNuclei_CheckOverlap']:
		java.write('\tcif.SegmentNuclei_CheckOverlap = %d ;\n' % Parameters['SegmentNuclei_CheckOverlap'])
	else:
		raise Exception("Wrong value for parameter 'SegmentNuclei_CheckOverlap', positive integer expected, '"
						+ str(Parameters['SegmentNuclei_CheckOverlap']) + "' found.")
	
	if 'SegmentNuclei_Threshold' not in Parameters or Parameters['SegmentNuclei_Threshold'] is None:
		java.write('\tcif.SegmentNuclei_Threshold = 0.07f ;\n')
	elif isinstance(Parameters['SegmentNuclei_Threshold'], float) and 0.0 < Parameters['SegmentNuclei_Threshold']:
		java.write('\tcif.SegmentNuclei_Threshold = (float)%f ;\n' % Parameters['SegmentNuclei_Threshold'])
	else:
		raise Exception("Wrong value for parameter 'SegmentNuclei_CheckOverlap', positive float expected, '"
						+ str(Parameters['SegmentNuclei_CheckOverlap']) + "' found.")
	
	if 'SegmentNuclei_SaveNuclei' not in Parameters or Parameters['SegmentNuclei_SaveNuclei'] is None:
		java.write('\tcif.SegmentNuclei_SaveNuclei = false ;\n')
	elif isinstance(Parameters['SegmentNuclei_SaveNuclei'], bool):
		if Parameters['SegmentNuclei_SaveNuclei']:
			java.write('\tcif.SegmentNuclei_SaveNuclei = true ;\n')
		else:
			java.write('\tcif.SegmentNuclei_SaveNuclei = false ;\n')
	else:
		raise Exception("Wrong value for parameter 'SegmentNuclei_SaveNuclei', boolean (True/False) expected, '"
						+ str(Parameters['SegmentNuclei_SaveNuclei']) + "' found.")
	
	if 'SegmentCells_DilationRatio' not in Parameters or Parameters['SegmentCells_DilationRatio'] is None:
		java.write('\tcif.SegmentCells_DilationRatio = 1.0 ;\n')
	elif isinstance(Parameters['SegmentCells_DilationRatio'], float) and \
		0.0 < Parameters['SegmentCells_DilationRatio']:
		java.write('\tcif.SegmentCells_DilationRatio = %f ;\n' % Parameters['SegmentCells_DilationRatio'])
	else:
		raise Exception("Wrong value for parameter 'SegmentCells_DilationRatio', positive float expected, '"
						+ str(Parameters['SegmentCells_DilationRatio']) + "' found.")
	
	if 'Background_Subtraction' not in Parameters or Parameters['Background_Subtraction'] is None \
		or Parameters['Background_Subtraction']:
		java.write('\tcif.Background_Subtraction = true ;\n')
	elif Parameters['Background_Subtraction'] is False:
		java.write('\tcif.Background_Subtraction = false ;\n')
	else:
		raise Exception("Wrong value for parameter 'Background_Subtraction', True or False expected, '"
						+ str(Parameters['Background_Subtraction']) + "' found.")
	
	ExitAfterSegmentation = "false"
	if 'ExitAfterSegmentation' in Parameters and Parameters['ExitAfterSegmentation'] is not None:
		if not isinstance(Parameters['ExitAfterSegmentation'], bool):
			raise Exception("'ExitAfterSegmentation' parameter must be boolean.")
		elif Parameters['ExitAfterSegmentation']:
			ExitAfterSegmentation = "true"
		else:
			ExitAfterSegmentation = "false"
	
	SkipRegistration = False
	if 'Segmentation' in Parameters and Parameters['Segmentation'] is not None:
		if not isinstance(Parameters['Segmentation'], bool):
			raise Exception("'Segmentation' parameter must be boolean.")
		elif Parameters['Segmentation']:
			java.write('\tcif.Registration_And_Segmentation(PathToData, true, '+ExitAfterSegmentation+') ;\n\n')
			SkipRegistration = True
	
	if 'Registration_And_Segmentation' in Parameters and Parameters['Registration_And_Segmentation'] is not None:
		if not isinstance(Parameters['Registration_And_Segmentation'], bool):
			raise Exception("'Registration_And_Segmentation' parameter must be boolean.")
		elif Parameters['Registration_And_Segmentation']:
			if SkipRegistration:
				raise Exception("Parameters 'Registration' and 'Registration_And_Segmentation' cannot be both True.")
			else:
				java.write('\tcif.Registration_And_Segmentation(PathToData, false, '+ExitAfterSegmentation+') ;\n\n')
	
	
	
	if 'FE_SaveImages' not in Parameters or Parameters['FE_SaveImages'] is None \
		or Parameters['FE_SaveImages'] is False:
		java.write('\tcif.FE_SaveImages = false ;\n')
	elif Parameters['FE_SaveImages']:
		java.write('\tcif.FE_SaveImages = true ;\n')
	else:
		raise Exception("Wrong value for parameter 'FE_SaveImages', True or False expected, '"
						+ Parameters['FE_SaveImages'] + "' found.")
	
	if 'FE_BiasedFeaturesOnly' not in Parameters or Parameters['FE_BiasedFeaturesOnly'] is None \
		or Parameters['FE_BiasedFeaturesOnly']:
		java.write('\tcif.FE_BiasedFeaturesOnly = true ;\n')
	elif isinstance(Parameters['FE_BiasedFeaturesOnly'], bool):
		if Parameters['FE_BiasedFeaturesOnly']:
			java.write('\tcif.FE_BiasedFeaturesOnly = true ;\n')
		else:
			java.write('\tcif.FE_BiasedFeaturesOnly = false ;\n')
	else:
		raise Exception("Wrong value for parameter 'FE_BiasedFeaturesOnly', True or False expected, '"
						+ Parameters['FE_BiasedFeaturesOnly'] + "' found.")
	
	if 'FE_DistanceFromBorder' not in Parameters or Parameters['FE_DistanceFromBorder'] is None \
		or Parameters['FE_DistanceFromBorder'] is False:
		java.write('\tcif.FE_DistanceFromBorder = false ;\n')
	elif Parameters['FE_DistanceFromBorder']:
		java.write('\tcif.FE_DistanceFromBorder = true ;\n')
	else:
		raise Exception("Wrong value for parameter 'FE_DistanceFromBorder', True or False expected, '"
						+ Parameters['FE_DistanceFromBorder'] + "' found.")
	
	if 'FE_Rim_Size' not in Parameters or Parameters['FE_Rim_Size'] is None:
		java.write('\tcif.FE_Rim_Size = 3f ;\n')
	elif isinstance(Parameters['FE_Rim_Size'], float):
		java.write('\tcif.FE_Rim_Size = %f ;\n' % Parameters['FE_Rim_Size'])
	else:
		raise Exception("Wrong value for parameter 'FE_Rim_Size', positive float value expected, '"
						+ str(Parameters['FE_Rim_Size']) + "' found.")
	
	if 'FeaturesExtraction' in Parameters and Parameters['FeaturesExtraction'] is not None \
		and Parameters['FeaturesExtraction']:
		java.write('\tcif.FeaturesExtraction(PathToData) ;\n\n')
	
	
	
	if 'QualityControl' in Parameters and Parameters['QualityControl'] is not None \
		and Parameters['QualityControl']:
		java.write('\tcif.QualityControl(PathToData) ;\n\n')
	
	
	
	java.write('\tSystem.exit(0) ;\n')
	java.write('\t}\n')
	java.write('}\n')
	java.close()
	
	exit = os.system(Javac_Path + " " + Java_ClassPath + " cycIFAAP.java")
	print("Java compilation done and exited with status " + str(exit) + "\n")
	
	exit = os.system(Java_Path + " " + Java_Options + " " + Java_ClassPath + " cycIFAAP")
	print("Processing done and exited with status " + str(exit))
	
	os.remove("cycIFAAP.java")
	os.remove("cycIFAAP.class")





# ------------------------------------------------ Evaluate Detection ------------------------------------------------
def EvaluateDetection(Prediction: str, GroundTruth: str, Overlap: float, SaveImageAs: str,
						JavaJarsPath: str=None, JavaXms: str="4G", JavaXmx: str="8G"):
	""" This function calls the measures.Evaluations.Detection method.
		Args:
			Prediction (str): .
			GroundTruth (str): .
			Overlap (float): .
			SaveImageAs (str): .
	"""
	
	java = open("EvaluateDetection.java", "w")
	
	java.write('import measures.Evaluations;\n')
	java.write('import init.Initializer;\n\n')
	
	java.write('public class EvaluateDetection\n')
	java.write('{\n\n')
	
	java.write('public static void main(String[] args) throws Exception\n')
	java.write('\t{\n')
	java.write('\tInitializer.Start() ;\n')
	
	java.write('\tEvaluations.Detection("')
	java.write(Prediction)
	java.write('", "')
	java.write(GroundTruth)
	java.write('", (float)')
	java.write(str(Overlap))
	java.write(', "')
	java.write(SaveImageAs)
	java.write('", "tmp.csv") ;\n')
	
	java.write('\tSystem.exit(0) ;\n')
	java.write('\t}\n')
	java.write('}\n')
	java.close()
	
	if JavaJarsPath is None:
		Java_ClassPath = "-classpath .:FiReTiTiLiB.jar:lib/*:."
	else:
		Java_ClassPath = "-classpath .:" + JavaJarsPath + "/FiReTiTiLiB.jar:" + JavaJarsPath + "/lib/*:."
	
	Java_Options = "-noverify -Xms" + JavaXms + " -Xmx" + JavaXmx
	
	exit = os.system(Javac_Path + " " + Java_ClassPath + " EvaluateDetection.java")
	print("Java compilation done and exited with status " + str(exit) + "\n")
	
	exit = os.system(Java_Path + " " + Java_ClassPath + " " + Java_Options + " EvaluateDetection")
	print("Processing done and exited with status " + str(exit))
	
	file = pandas.read_csv("tmp.csv")
	line = file.to_numpy()
	
	os.remove("EvaluateDetection.java")
	os.remove("EvaluateDetection.class")
	os.remove("tmp.csv")
	
	return line[0, 0], line[0, 1], line[0, 2]







if __name__ == "__main__":
	Parameters = {'nbCPU': 12,  # Number of CPU / cores you wish to use.
			'Experiment': "CROPS", # Can be 'CROPS' or 'TMA'.
			#'Python_Path': "...", # If necessary, give the entire / absolute path to your python.
			#'Java_Xms': '4G', # How much memory to allocate when the job starts.
			#'Java_Xmx': '8G', # How much memory maximum to allocate.
			#'Registration_Technique': "OpenCV", #Which registration technique to use?
			'Registration_Reverse': True, # If True the last round dapi image will be used as reference instead of the first round dapi image.
			'SegmentNuclei_RoundToSegment': 'R1', #ZProjection', # Which round to segment? By default the consensus/z-projection.
			'SegmentNuclei_Model': 'MaskRCNN_512x512_Norm=B - 9686_831_8976 - 20201009.pt', # The deep learning segmentation model to use.
			#'SegmentNuclei_Model': 'CellPose-cpu-30-0.4', # In this example, CellPose will use CPUs and the number is the CellPose diameter parameter.
			#'SegmentNuclei_BorderEffectSize': 73, # Nuclei segmentation parameter.
			#'SegmentNuclei_BatchSize': 3, # Nuclei segmentation parameter.
			#'SegmentNuclei_CheckOverlap': 7, # Nuclei segmentation parameter.
			#'SegmentNuclei_SaveNuclei': False, # Nuclei segmentation parameter.
			#'SegmentNuclei_Threshold': 0.07, # Nuclei segmentation parameter.
			'ExitAfterSegmentation': True, # If True, the pipeline will stop after cell segmentation, and skip background subtraction and exclusive markers.
			#'Background_Subtraction': True, # If True, the background subtraction will be performed for each marker and used during features extraction.
			'Images_Directory': "/Users/firetiti/Downloads/CyclicIF/cycIFAAP_Example1/Test - 2048x2048/", # The directory containing the images to process. Always make a backup!!!
			#'FE_SaveImages': True, # If True, all the resulting / check images will be saved.
			#'FE_BiasedFeaturesOnly': True, # If True, only the biased (intensity based) features will be extracted.
			#'FE_DistanceFromBorder': True, # If True, the distance from the sample border will be computed.
			#'FE_Rim_Size': 3f, # The rim size/dimensions/width.
			#'Segmentation': False, # If True, it performs the segmentation, but skips the registration.
			'Registration_And_Segmentation': True, # If True, this starts the registration and segmentation.
			#'FeaturesExtraction': True, # If True, this starts the features extraction.
			#'QualityControl': False, # If True, this starts the quality control.
			}
	
	
	import FiReTiTiPyLib.CyclicIF.CyclicIF_JavaInterfacer as cycIFji
	cycIFji.Run(Parameters, JavaJarsPath=os.path.dirname(os.path.abspath(__file__)), JavaXms="4G", JavaXmx="8G")