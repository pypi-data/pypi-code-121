# 2022.2.18
import json, sys, time, fire, os, spacy

if not hasattr(spacy, 'snts'): 
	from spacy.lang import en
	spacy.sntbr		= (inst := en.English(), inst.add_pipe("sentencizer"))[0]
	spacy.snts		= lambda essay: [ snt.text.strip() for snt in  spacy.sntbr(essay).sents]
	spacy.sntpid	= lambda essay: (pid:=0, [ ( pid := pid + 1 if "\n" in snt.text else pid,  (snt.text.strip(), pid))[-1] for snt in  spacy.sntbr(essay).sents] )[-1]

def postag_nlp():
	nlp = spacy.load('en_core_web_sm')  # 3.1.1
	#t = nlp.get_pipe('tagger')
	#>>> nlp.pipe_names #['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer', 'ner']
	#[nlp.remove_pipe(n) for n in ['tok2vec','parser', 'attribute_ruler','lemmatizer', 'ner'] ]
	[nlp.remove_pipe(n) for n in ['parser',  'ner'] ]
	return nlp 

def readline(infile, sepa=None):
	with open(infile, 'r') as fp:
		while True:
			line = fp.readline()
			if not line: break
			yield line.strip().split(sepa) if sepa else line.strip()

class util(object):
	def __init__(self): pass 

	def down(self, ibeg,iend):
		for i in range(ibeg, iend):  
			j = str(10000 + i)
			os.system(f"wget https://huggingface.co/datasets/allenai/c4/resolve/main/en/c4-train.0{j[1:]}-of-01024.json.gz")

	def compress(self):
		''' 0..1023 '''
		for i in range(1024):  # 0..1023
			j = str(10000 + i)
			os.system(f"gzip c4-train.0{j[1:]}-of-01024.json")

	def sntbr(self, infile, outfile=None):
		'''  'text' -> 'snts' 2022.2.19	'''
		print("started:", infile , flush=True)
		if not outfile: outfile = infile + ".snts"
		with open(outfile, 'w') as fw : 
			for line in readline(infile): 
				try:
					arr =json.loads(line) 
					arr['snts'] = spacy.snts(arr.get('text','').strip())
					del arr['text']
					fw.write( json.dumps(arr) + "\n")
				except Exception as e:
					print("ex:", e, line)
		print("finished:", infile , flush=True)

	def sntbr_all(self):
		''' 0..1023 '''
		for i in range(1024):  # 0..1023
			j = str(10000 + i)
			filename = f"c4-train.0{j[1:]}-of-01024.json"
			print( i,  filename, flush=True)
			self.sntbr(filename) 

	def postag(self, infile, outfile=None):
		''' c0.snts0 => c0.snts.postag '''
		if not outfile: outfile = infile + ".postag"
		if os.path.exists(outfile): 
			print ("already exists:", outfile, flush=True)
			return 
		nlp = postag_nlp()
		with open(outfile, 'w') as fw:
			for line in readline(infile):
				try:
					arr = json.loads(line.strip())
					for snt in arr.get('snts',[]):
						doc = nlp(snt)
						poslist = [(t.text, t.pos_, t.tag_) for t in doc]
						fw.write(json.dumps(poslist) + "\n") # prepared for n-gram counting 
				except Exception as e:
					print("ex:", e, line)
		print ("finished:", infile, outfile)

if __name__ == '__main__':
	fire.Fire(util)

'''
ubuntu@dsk-162-10-ubuntu:/ftp/c4data$ nohup python c4data.py sntbr_all &
[1] 45656

'''