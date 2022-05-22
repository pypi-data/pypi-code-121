import platform, requests, os, shutil
from pypandoc.pandoc_download import download_pandoc

def pandoc():
	download_pandoc()


# This is a script made by a friend before we knew that the above function was a thing
def pandoc_kali():
	version = 'https://github.com/jgm/pandoc/releases/latest'
	version = requests.get(version, allow_redirects=True)
	version = version.url.rsplit('/', 1)[-1]

	platforms = {"Windows":"windows-x86_64.zip", "Linux":"linux-amd64.tar.gz", "Darwin":"macOS.zip"}
	the_platform = platforms[platform.system()]

	path = "/bin/pandoc"
	extension = ""
	if platform.system() == "Windows":
	  path = "/pandoc"
	  extension = ".exe"

	all_together = f"pandoc-{version}-{the_platform}"

	url = f"https://github.com/jgm/pandoc/releases/download/{version}/{all_together}"
	open(all_together, "wb").write(requests.get(url, allow_redirects=True).content)
	if the_platform == "Linux":
	  import tarfile
	  b = tarfile.open("./"+all_together)
	  b.extractall("./pandoc")
	  b.close()
	else:
	  shutil.unpack_archive("./"+all_together,"./pandoc")

	os.remove(all_together)
	shutil.move(f"./pandoc/pandoc-{version}{path}{extension}", f".{path}{extension}")
	shutil.rmtree("./pandoc")
