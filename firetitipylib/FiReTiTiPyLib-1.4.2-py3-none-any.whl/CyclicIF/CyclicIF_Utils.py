
def FindScenes(images: list, verbose: bool=False) -> list:
	scenes = []
	for image in images:
		index = image.index("Scene-")
		index2 = index + 6
		while image[index2] != '_':
			index2 += 1
		scene = image[index +6:index2]
		if scene not in scenes:
			scenes.append(scene)
	
	if verbose:
		print("Scenes found:", *scenes)
	
	return scenes


def FindScenesInCSV(files: list, verbose: bool = False) -> list:
	scenes = []
	for file in files:
		index = file.index("Scene ")
		index2 = index + 6
		while '0' <= file[index2] <= '9' or file[index2] == 'X':
			index2 += 1
		scene = file[index + 6:index2]
		if scene not in scenes:
			scenes.append(scene)
	
	scenes.sort()
	if verbose:
		print("Scenes found:", *scenes)
	
	return scenes
