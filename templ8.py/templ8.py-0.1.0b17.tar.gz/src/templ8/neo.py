import requests
from pathlib import Path
import os.path as pa
import os
import templ8.programstate as ps

def login():
	loginpath = Path.home() / ".templ8rc"
	lines = open(loginpath, "r").readlines()
	return lines[0].rstrip()
	

def neo():
	state = ps.ProgramState()
	last_change_list = {}
	if os.path.exists("chlist"):
		for i in open("chlist", "r").readlines():
			spl = i.split("<<")
			if len(spl) != 2:
				continue
			last_change_list[Path(spl[0])] = float(spl[1])
	new_change_list = last_change_list
	
	
	apikey = login()
	fls = []
	batch = 0
	finalprint = ""
	files_this_batch = 0
	for subdir, dirs, files in os.walk(state.output_folder):
		for file in files:
			if os.path.splitext(file)[1] != "":
				path = Path(pa.join(subdir, file))
				from_root = Path(*path.parts[1:])
				
				current_last_change = os.stat(path).st_mtime
				if path in last_change_list:
					if float(last_change_list[path]) == float(current_last_change):
						continue
				finalprint += f"{path}\n"
				new_change_list[path] = current_last_change
				if len(fls) <= batch:
					fls.append({})
				fls[batch][str(from_root).replace(os.sep, '/')] = open(path, "rb").read()
				files_this_batch += 1
				if files_this_batch > 50:
					finalprint += "\n\nNEW BATCH\n\n"
					files_this_batch = 0
					batch += 1
	endpoint = f"https://neocities.org/api/upload"
	new_change_text = ""
	for p in new_change_list:
		new_change_text += f"{p}<<{new_change_list[p]}\n"
	open("chlist", "w").write(new_change_text)
	print(finalprint)
	for i in fls:
		response = requests.post(
			endpoint,
			headers={"Authorization": f"Bearer {apikey}"},
			files=i,
		)

		print("Response: ", response.status_code)
		print("Response: ", response.text)
	

			

