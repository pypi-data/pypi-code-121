from requests import get
from os import mkdir

class downloader:
	namedir = "Download"
	def img(link, namedir=namedir):
		try:
			mkdir(namedir)
			name = link.split("/")[-1]
			r = get(link, allow_redirects=True)
			open(f"{namedir}/img-{name}", "wb").write(r.content)
		except FileExistsError:
			name = link.split("/")[-1]
			r = get(link, allow_redirects=True)
			open(f"{namedir}/img-{name}", "wb").write(r.content)
	def code(link, namedir=namedir):
		try:
			mkdir(namedir)
			name = link.split("/")[-1]
			r = get(link, allow_redirects=True)
			open(f"{namedir}/code-{name}", "wb").write(r.content)
		except FileExistsError:
			name = link.split("/")[-1]
			r = get(link, allow_redirects=True)
			open(f"{namedir}/code-{name}", "wb").write(r.content)
	def music(link, namedir=namedir):
		try:
			mkdir(namedir)
			name = link.split("/")[-1]
			r = get(link, allow_redirects=True)
			open(f"{namedir}/music-{name}", "wb").write(r.content)
		except FileExistsError:
			name = link.split("/")[-1]
			r = get(link, allow_redirects=True)
			open(f"{namedir}/music-{name}", "wb").write(r.content)
	def youtube_video(link, namedir=namedir):
		pass