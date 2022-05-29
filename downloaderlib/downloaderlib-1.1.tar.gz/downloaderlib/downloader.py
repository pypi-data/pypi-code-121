from requests import get
from os import mkdir
def downloader(namedir, link):
	try:
		mkdir(namedir)
		name = link.split("/")[-1]
		r = get(link, allow_redirects=True)
		open(f"{namedir}/{name}", "wb").write(r.content)
	except FileExistsError:
		name = link.split("/")[-1]
		r = get(link, allow_redirects=True)
		open(f"{namedir}/{name}", "wb").write(r.content)