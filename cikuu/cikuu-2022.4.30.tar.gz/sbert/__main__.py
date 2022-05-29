#pip install -U sentence-transformers
import fire ,json
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

def readline(infile, sepa=None):
	with open(infile, 'r') as fp:
		while True:
			line = fp.readline()
			if not line: break
			yield line.strip().split(sepa) if sepa else line.strip()

class util(object):
	def __init__(self): pass 

	def vec(self, infile, outfile=None): 
		''' gzjc.snt -> gzjc.vec_source  '''
		if not outfile : outfile = infile.split('.')[0] + ".vec"
		print ("started:", infile, flush=True)
		with open(outfile, 'w') as fw: 
			for line in readline(infile): 
				vec = model.encode(line.strip())
				arr = {'snt': line.strip(), 'vec': vec.tolist()}
				fw.write(json.dumps(arr) + "\n")
		print ("finished:", infile)

if __name__ == '__main__':
	fire.Fire(util)

'''
ubuntu@VM-64-245-ubuntu:~/cikuu/pypi/sbert$ nohup python __main__.py vec_source dic.snt & 
[1] 364344

	def vec(self, infile, outfile=None): 
		if not outfile : outfile = infile + ".vec"
		print ("started:", infile, flush=True)
		with open(outfile, 'w') as fw: 
			for line in readline(infile): 
				vec = model.encode(line.strip())
				fw.write(f"{line.strip()}\t{json.dumps(vec.tolist())}\n")
		print ("finished:", infile)

'''