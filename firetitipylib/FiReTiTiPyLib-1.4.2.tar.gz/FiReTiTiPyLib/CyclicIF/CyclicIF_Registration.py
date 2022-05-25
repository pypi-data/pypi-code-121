import gc
import os
import sys
import time

import cv2
import numpy as np
import psutil
import scipy
import skimage
import skimage.morphology as mm
import skimage.registration as skReg

from natsort import humansorted
from skimage.transform import warp

import FiReTiTiPyLib.CyclicIF.CyclicIF_Utils as utils
import FiReTiTiPyLib.ImagesIO as imIO



class Style:
	BLACK = '\033[30m'
	RED = '\033[31m'
	GREEN = '\033[32m'
	YELLOW = '\033[33m'
	BLUE = '\033[34m'
	MAGENTA = '\033[35m'
	CYAN = '\033[36m'
	WHITE = '\033[37m'
	UNDERLINE = '\033[4m'
	RESET = '\033[0m'




class CyclicIF_Registration:
	""" This class performs the registration for cyclic immunofluoresence images.
		Code inspired from https://learnopencv.com/feature-based-image-alignment-using-opencv-c-python/
	"""

	def __init__(self, MaxFeatures: int=2013, Reverse: bool=True, SaveImages: bool=True, Copyright: str=None,
						Debug: bool=False, MonitorMemory: bool=False):
		""" Simple init.
		:param MaxFeatures: Maximum number of features to extract.
		:param Reverse: If True the last round is used as reference, otherwise the first.
		:param SaveImages: Save the images after registration? Useful for debuging.
		:param Debug: Run using debeging mode?
		:param SkipTransformation: If True, the transformations are not performed.
		"""
		self.MaxFeatures = MaxFeatures
		self.Reverse = Reverse
		self.SaveImages = SaveImages
		self.Copyright = Copyright
		self.Debug = Debug
		self.MonitorMemory = MonitorMemory

		#self.Safety = 32760
		self.Warning = 46300
		
		self.MatrixSafety = 0.017
		self.MatrixDiagSafety = 0.023

		self.FD = [self._CreateFeaturesDetector('SIFT', MaxFeatures),
					self._CreateFeaturesDetector('ORB', MaxFeatures),
					self._CreateFeaturesDetector('SIFT', 2*MaxFeatures),
					self._CreateFeaturesDetector('ORB', 2*MaxFeatures),
					self._CreateFeaturesDetector('SIFT', 4*MaxFeatures),
					self._CreateFeaturesDetector('ORB', 4*MaxFeatures),
					self._CreateFeaturesDetector('SIFT', 8*MaxFeatures),
					self._CreateFeaturesDetector('ORB', 8*MaxFeatures)]
		
		self.TargetKP   = np.ndarray(shape=len(self.FD), dtype=object)
		self.TargetDesc = np.ndarray(shape=len(self.FD), dtype=object)
		self.Issues     = np.ndarray(shape=len(self.FD)+1).astype(int)
		
		self.Matcher = cv2.BFMatcher(normType=cv2.NORM_L2, crossCheck=True)
		#self.Matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
		#FLANN_INDEX_KDTREE = 1
		#index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
		#search_params = dict(checks=50)
		#flann = cv.FlannBasedMatcher(index_params, search_params)



	def Run(self, inputdir: str, outputdir: str) -> int:
		""" This method starts the registration.
		:param inputdir: The path to the directory containing the images.
		:param outputdir: The path to the directory where the registered images will be saved.
		:return: The number of errors.
		"""
		nbErrors = 0
		
		if self.Copyright is not None:
			print(self.Copyright)
		
		AllImages = imIO.FindImages(inputdir, NamesOnly=True, verbose=True)
		if self.Debug:
			print(*AllImages, sep='\n')
			sys.stdout.flush()

		Scenes = utils.FindScenes(AllImages, True)
		if self.Debug:
			print(*Scenes, sep='\n')
			sys.stdout.flush()

		os.makedirs(outputdir, exist_ok=True)
		#os.makedirs(outputdir+"/Checks/", exist_ok=True)

		for scene in Scenes:
			print(Style.GREEN + "\n\nRegistrating scene " + scene + Style.RESET)
			startime = time.time()
			
			for i in range(len(self.FD)): # Reset
				self.TargetKP[i] = self.TargetDesc[i] = None
			self.Issues.fill(0)
			gc.collect()

			images = [image for image in AllImages if "Scene-" + scene + "_" in image]
			images = humansorted(images)
			dapis = [image for image in images if "_c1_" in image]
			dapis = humansorted(dapis, reverse=self.Reverse)
			if self.Debug:
				print("Images:")
				print(*images, sep='\n')
				print("Dapis:")
				print(*dapis, sep='\n')
				sys.stdout.flush()
			
			imrefpath = inputdir + "/" + dapis[0]
			print("Reference image: " + imrefpath)
			sys.stdout.flush()
			ImTarget = self._LoadImage(imrefpath, False, True)

			round = self._FindRound(dapis[0])
			toTransform = [image for image in images if round + "_" in image]
			for image in toTransform:
				#shutil.copy(inputdir+"/"+image, outputdir)
				if self.SaveImages:
					im = self._LoadImage(inputdir + "/" + image, True, False)
					imIO.Write(im, True, outputdir + "/" + image)
			
			for i in range(1, len(dapis)):
				round = self._FindRound(dapis[i])
				print("\n - Processing round '%s'." % round)
				sys.stdout.flush()

				impath = inputdir + "/" + dapis[i]
				im = self._LoadImage(impath, False, True)
				
				toTransform = [image for image in images if round + "_" in image]
				
				for level in range(len(self.FD)):
					start = time.time()
					Success = self._UseHomography(inputdir, level, ImTarget, im, toTransform, outputdir)
					if self.Debug:
						print("Level %d done in %fs" % (level, time.time()-start))
					if not Success:
						if self.Debug:
							print(Style.RED + "WARNING - Registration level " + str(level) + " failure."+Style.RESET)
					else:
						break
				
				if not Success:
					print(Style.RED + "Failed to find a transformation matrix => Last chance activated!" + Style.RESET)
					sys.stdout.flush()
					print("Failed to find a transformation matrix => Last chance activated!", file=sys.stderr)
					sys.stderr.flush()
					
					Success = self._LastChance(inputdir, ImTarget, im, toTransform, outputdir)
					
					if not Success:
						nbErrors += 1
						print(Style.RED + "Last chance failed => Registration failed." + Style.RESET)
						sys.stdout.flush()
						print("Last chance failed => Registration failed.", file=sys.stderr)
						sys.stderr.flush()
				
				del im
				gc.collect()
			
			LenIssues = len(self.Issues)
			print(Style.GREEN + "Scene %s done in %fs:" % (scene, time.time() - startime))
			print(" - Issues = " + str(self.Issues))
			print(" - Last chance%s = %d" % (("" if self.Issues[LenIssues-2] <= 1 else "s"), self.Issues[LenIssues-2]))
			print(Style.RED + " - Error%s = %d" % (("" if self.Issues[LenIssues-1] <= 1 else "s"),
													self.Issues[LenIssues-1]) + Style.RESET)
			sys.stdout.flush()
			gc.collect()
		
		return nbErrors

	#sys.exit(0)



	def _UseHomography(self, inputdir: str, Level: int, Target, Image, ToTransform: list, outputdir: str) -> bool:
		if self.Debug:
			print("Registration level %d" % Level)
		
		if self.TargetKP[Level] is None: # Describe target image.
			if self.MonitorMemory:
				print("Memory 0: before 'detectAndCompute(Target): '" + str(self.AvailableMemory()))
			
			self.TargetKP[Level], self.TargetDesc[Level] = self.FD[Level].detectAndCompute(Target, None)
			
			if self.MonitorMemory:
				print("Memory 1: After: '" + str(self.AvailableMemory()))
			
			if self.TargetDesc[Level] is None:
				print(Style.RED + "ERROR 1 - Cannot extract features from target image." + Style.RESET)
				sys.stdout.flush()
				print("ERROR 1 - Cannot extract features from target image.", file=sys.stderr)
				sys.stderr.flush()
				self.Issues[Level] += 1
				return False
		
		imKP, imDesc = self.FD[Level].detectAndCompute(Image, None)
		
		if self.MonitorMemory:
			print("Memory 2: after 'detectAndCompute(Image): '" + str(self.AvailableMemory()))
		
		if imDesc is None:
			print(Style.RED + "ERROR 2 - Cannot extract features from image." + Style.RESET)
			sys.stdout.flush()
			print("ERROR 2 - Cannot extract features from image.", file=sys.stderr)
			sys.stderr.flush()
			self.Issues[Level] += 1
			return False
		
		matches = self.Matcher.match(imDesc, self.TargetDesc[Level])
		
		matches = sorted(matches, key=lambda x: x.distance)
		
		if self.MonitorMemory:
			print("Memory 3: " + str(self.AvailableMemory()))
		
		H = self._FindHomography(matches, self.TargetKP[Level], imKP)
		
		del imKP
		del imDesc
		
		if H is None:
			self.Issues[Level] += 1
			gc.collect()
			return False
		else:
			Hinv = np.linalg.inv(H)
			if self.SaveImages:
				height, width = Target.shape
				for image in ToTransform:
					print("	 -> Transforming '%s'." % (inputdir + "/" + image))
					imRaw = self._LoadImage(inputdir + "/" + image, True, False)[0]
					#warped_img = cv2.warpPerspective(imRaw, H, (width, height), borderMode=cv2.BORDER_CONSTANT, borderValue=0)
					order = 1
					#if "_c1_" not in image: order = 0
					warped_img = warp(imRaw, Hinv, output_shape=(height, width), order=order)
					imIO.Write(warped_img.astype(np.uint16), True, outputdir + "/" + image)
					del imRaw
					del warped_img
		
		gc.collect()
		return True



	def _LastChance(self, inputdir: str, Target, Image, toTransform: list, outputdir: str) -> bool:
		if self.Debug:
			print(Style.GREEN + "Last chance activated." + Style.RESET)
		
		start = time.time()
		
		tarShape = Target.shape
		tarWidth = tarShape[1]
		tarHeight = tarShape[0]
		imShape = Image.shape
		imWidth = imShape[1]
		imHeight = imShape[0]
		
		if imWidth <= tarWidth:
			imSx = 0
			trSx = int((tarWidth - imWidth) / 2.0)
			Lx = imWidth
		else:
			imSx = int((imWidth - tarWidth) / 2.0)
			trSx = 0
			Lx = tarWidth
		
		if imHeight <= tarHeight:
			imSy = 0
			trSy = int((tarHeight - imHeight) / 2.0)
			Ly = imHeight
		else:
			imSy = int((imHeight - tarHeight) / 2.0)
			trSy = 0
			Ly = tarHeight
		
		image = np.ndarray(shape=(tarHeight, tarWidth), dtype=Target.dtype)
		image.fill(0)
		imSqueezed = Image.squeeze()
		image[trSy:trSy+Ly, trSx:trSx+Lx] = imSqueezed[imSy:imSy+Ly, imSx:imSx+Lx]
		
		shift, error, diffphase = skReg.phase_cross_correlation(Target.squeeze(), image, overlap_ratio=0.5)
		
		del image
		del imSqueezed
		
		if self.Debug:
			print("time = " + str(time.time() - start))
			print("Shift=", end='')
			print(shift, end='')
			print(", Error=" + str(error), end='')
			print(", DiffPhase=" + str(diffphase))
		
		if 0.00001 < diffphase:
			self.Issues[len(self.Issues)-1] += 1
			return False

		if self.SaveImages:
			for image in toTransform:
				print("	 -> Transforming '%s'." % (inputdir + "/" + image))
				imRaw = self._LoadImage(inputdir + "/" + image, True, False)[0].squeeze()
				
				imTR = np.ndarray(shape=(tarHeight, tarWidth), dtype=imRaw.dtype)
				imTR.fill(0)
				imTR[trSy:trSy+Ly, trSx:trSx+Lx] = imRaw[imSy:imSy+Ly, imSx:imSx+Lx]
				
				imreg = scipy.ndimage.interpolation.shift(imTR, shift.astype(int))
				imIO.Write(imreg.astype(np.uint16), True, outputdir + "/" + image)
				
				del imRaw
				del imTR
				del imreg
		
		return True



	def _CreateFeaturesDetector(self, name: str, MaxFeatures: int):
		if MaxFeatures <= 0:
			raise Exception("MaxFeatures <= 0")
		lowercase = name.lower()
		if lowercase in {"orb"}:
			if self.Debug:
				print("Features detector: ORB.")
			return cv2.ORB_create(MaxFeatures)
		elif lowercase in {"sift"}:
			if self.Debug:
				print("Features detector: SIFT.")
			return cv2.SIFT_create(MaxFeatures)
		#elif lowercase in {"surf"}:
		#   if self.Debug:
		#       print("Features detector: SURF.")
		#	return cv2.xfeatures2d.SURF_create(400)
		else:
			raise Exception("Unknow features detector. Expected {SIFT, ORB}")



	def _LoadImage(self, path: str, raw: bool, preprocess: bool):
		print("Reading '" + str(path) + "'... ", end='')
		image = imIO.Read(path, True, verbose=False) # Image.open(dapis[0])
		print(str(image.shape) + " successfully.")
		sys.stdout.flush()

		channel, height, width = image.shape
		#if self.Safety < channel or self.Safety < height or self.Safety < width:
		#	raise Exception("Image too big. Max accepted = " + str(self.Safety))
		
		if self.Warning <= channel or self.Warning <= height or self.Warning <= width:
			print("WARNING - Not recommended to register such big images as the processing will likely generate an "
					+ "error with Java if the number of pixels is higher than 2^31. "
					+ "Max recommended = " + str(self.Warning), file=sys.stderr)
			sys.stderr.flush()
		
		if raw:
			return image

		#print("Image [%d,%d]" % (image.min(), image.max()))
		if preprocess:
			min = image.min()
			A = 65535.0 / (image.max() - min)
			B = -A * min
			image = image * A + B

		image /= 65535.0
		image *= 255.0
		#return np.uint8(image.squeeze())
		return mm.white_tophat(np.uint8(image.squeeze()), mm.square(113))



	def _ListToPoints(self, matches, imKP, TargetKP):
		iMatchIdx = [m.queryIdx for m in matches]
		tMatchIdx = [m.trainIdx for m in matches]
		iPoints = np.float32([imKP[j].pt for j in iMatchIdx])
		tPoints = np.float32([TargetKP[j].pt for j in tMatchIdx])
		return iPoints, tPoints



	def _FindRound(self, name: str) -> str:
		index = name.index("_")
		return name[0:index]
	
	
	
	def _FindHomography(self, Matches, TargetKP, imKP, Methods=[cv2.RANSAC, cv2.LMEDS, cv2.RHO],
							Bests=[0.07, 0.13, 0.17, 0.23, 0.31, 0.37, 0.43, 0.53, 0.61, 0.71]):
		
		Homography = np.ndarray(shape=(len(Methods)*len(Bests), 3, 3), dtype=float)
		Result = np.ndarray(shape=(3, 3), dtype=float)
		
		count = 0
		for method in Methods:
			if self.Debug:
				print("Method: " + str(method))
				start = time.time()
			
			for best in Bests:
				length = int(len(Matches) * best)
				if 4 <= length:
					bestMatches = Matches[:length]
					
					imPoints, TargetPoints = self._ListToPoints(bestMatches, imKP, TargetKP)
					"""
					try:
						imMatches = cv2.drawMatches(ImTarget, TargetKP, im, imKP, matches, None)
						cv2.imwrite(outputdir + "/Checks/Scene " + scene + " - Matches " + round + " - Best " + str(best) + ".png",
									imMatches)
					except:
						text = outputdir + "/Checks/Scene " + scene + " - Matches " + round + ".png"
						print(str(Style.RED + "\t Cannot write matching check image: %s" + Style.RESET) % text)
					"""
					H, mask = cv2.findHomography(imPoints, TargetPoints, method, ransacReprojThreshold=11)
					
					valid = False if H is None else self._isValidMatrix(H)
					
					if self.Debug:
						if valid:
							txt = "valid => included"
						else:
							txt = "NOT valid => rejected"
						print("Homography matrix for " + str(best) + ": " + txt)
						print(H)
					
					if valid:
						np.copyto(Homography[count], H)
						count += 1
			
			if self.Debug:
				print("Execution = " + str(time.time() - start) + "s")
		
		if count == 0:
			print(Style.RED + "WARNING - No valid matrix detected." + Style.RESET)
			sys.stdout.flush()
			print("WARNING - No valid matrix detected.", file=sys.stderr)
			sys.stderr.flush()
			return None
		else:
			for y in range(3):
				for x in range(3):
					buffer = Homography[0:count, y, x].copy()
					buffer.sort()
					if 11 <= count:
						remove = 3
					elif 7 <= count:
						remove = 2
					elif 4 <= count:
						remove = 1
					else:
						remove = 0
					Result[y, x] = buffer[remove: len(buffer) - remove].mean()
			
			if self.Debug:
				print("Homography matrix")
				print(Result)
			
			valid = self._isValidMatrix(Result)
			if not valid:
				print(Style.RED + "WARNING - Invalid matrix detected." + Style.RESET)
				sys.stdout.flush()
				print("WARNING - Invalid matrix detected.", file=sys.stderr)
				sys.stderr.flush()
				return None
			
			return Result



	def _isValidMatrix(self, M) -> bool:
		for i in range(3):
			if M[i, i] < 1.0-self.MatrixDiagSafety or 1.0+self.MatrixDiagSafety < M[i, i]:
				return False
		if M[0, 1] < -self.MatrixSafety or self.MatrixSafety < M[0, 1]: return False
		if M[1, 0] < -self.MatrixSafety or self.MatrixSafety < M[1, 0]: return False
		if M[2, 0] < -self.MatrixSafety or self.MatrixSafety < M[2, 0]: return False
		if M[2, 1] < -self.MatrixSafety or self.MatrixSafety < M[2, 1]: return False
		return True



	def AvailableMemory(self):
		#psutil.cpu_percent() # gives a single float value
		#psutil.virtual_memory() # gives an object with many fields
		# you can convert that object to a dictionary
		mymem = dict(psutil.virtual_memory()._asdict())
		#psutil.virtual_memory().percent # you can have the percentage of used RAM
		return psutil.virtual_memory().available * 100 / psutil.virtual_memory().total # Percentage of available memory




if __name__ == "__main__":
	
	inputdir = "/Users/firetiti/Downloads/CyclicIF/cycIFAAP_Example1/Test - 2048x2048/"
	outputdir = "/Users/firetiti/Downloads/CyclicIF/cycIFAAP_Example1/Test - 2048x2048 - Registered/"
	
	#inputdir = "/Users/firetiti/Downloads/CyclicIF/cycIFAAP_Example2/Test - 4096x4096 - Test/"
	#outputdir = "/Users/firetiti/Downloads/CyclicIF/cycIFAAP_Example2/Test - 4096x4096 - Test - Registered/"
	
	cycreg = CyclicIF_Registration(Debug=False, MonitorMemory=False, Reverse=True, SaveImages=True)
	nbErrors = cycreg.Run(inputdir, outputdir)
	sys.exit(nbErrors)
	
	
	from skimage.draw import line_aa

	width = 500 #32760
	height = 1000 #32760
	image = np.uint8(np.random.randint(0, 50, (height, width)))
	#image = np.zeros((width, height), dtype=np.uint8)

	border = 23
	#offset = int(border / 2)

	for i in range(23):
		x1 = np.random.randint(border, width - border)
		x2 = np.random.randint(border, width - border)
		y1 = np.random.randint(border, height - border)
		y2 = np.random.randint(border, height - border)
		rr, cc, val = line_aa(x1, y1, x2, y2)
		image[cc, rr] = val * 255
		image[np.random.randint(border, height - border), np.random.randint(border, width - border)] = 255

	target = np.roll(image, 17, axis=0)
	target = np.roll(target, 17, axis=1)
	print("Images created")

	#fd = cv2.ORB_create(31)
	fd = cv2.SIFT_create(31)

	ImageKP, ImageDesc = fd.detectAndCompute(image, None)
	print("Features extracted from original image")
	sys.stdout.flush()
	TargetKP, TargetDesc = fd.detectAndCompute(target, None)
	print("Features extracted from target image")
	sys.stdout.flush()

	Matcher = cv2.BFMatcher(normType=cv2.NORM_L2, crossCheck=True)
	matches = Matcher.match(ImageDesc, TargetDesc)
	matches.sort(key=lambda x: x.distance, reverse=False)
	bestMatches = matches[:int(len(matches) * 0.51)]

	iMatchIdx = [m.queryIdx for m in bestMatches]
	imPoints = np.float32([ImageKP[j].pt for j in iMatchIdx])

	tMatchIdx = [m.trainIdx for m in bestMatches]
	TargetPoints = np.float32([TargetKP[j].pt for j in tMatchIdx])

	H, mask = cv2.findHomography(imPoints, TargetPoints, cv2.RANSAC, ransacReprojThreshold=11)

	warped_img = cv2.warpPerspective(image, H, (width, height), borderMode=cv2.BORDER_CONSTANT, borderValue=0)
	
	warped_imgnew = warp(image, np.linalg.inv(H), output_shape=(height, width)) * 255.0
	
	diff = abs(warped_imgnew-warped_img)
	print("Min=" + str(diff.min()) + " vs Max=" + str(diff.max()))
	
	from PIL import Image
	imgIm = Image.fromarray(image)
	imgTar = Image.fromarray(target)
	imgWarped = Image.fromarray(warped_img)
	imgWarpedNew = Image.fromarray(warped_imgnew)
	
	print(imgIm.filename)
	
	imgIm.show(title="Image")
	imgTar.show(title="Target")
	imgWarped.show(title="Warped")
	imgWarpedNew.show(title="Warped New")
