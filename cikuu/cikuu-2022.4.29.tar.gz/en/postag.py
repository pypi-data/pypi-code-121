# 2022.2.18
import json, sys, time, fire, os, en

def readline(infile, sepa=None):
	with open(infile, 'r') as fp:
		while True:
			line = fp.readline()
			if not line: break
			yield line.strip().split(sepa) if sepa else line.strip()

class util(object):
	def __init__(self): pass 

	def es_postag(self, infile, outfile=None, snt='snt'):
		''' clec.njson -> clec.njson.postag 
		{"snt":..., } => {"snt":, ... ,"postag": }
		2022.2.18
		'''
		print("started:", infile , flush=True)
		if not outfile: outfile = infile + ".postag"
		with open(outfile, 'w') as fw : 
			for line in readline(infile): 
				try:
					arr =json.loads(line) 
					doc = en.nlp(arr.get(snt,'').strip())
					arr['postag'] = "^ " + ' '.join([f"{t.text}_{t.text.lower()}_{t.lemma_}_{t.pos_}_{t.tag_}" if t.text != t.text.lower() else f"{t.text}_{t.lemma_}_{t.pos_}_{t.tag_}" for t in doc])  + ' $'
					fw.write( json.dumps(arr) + "\n")
				except Exception as e:
					print("ex:", e, line)
		print("finished:", infile , flush=True)

	def gram(self, infile, outfile=None):
		''' gram.txt => gram.txt.postag '''
		if not hasattr(gram, 'nlp'):
			gram.nlp = spacy.load('en_core_web_sm')  # 3.1.1
			#t = nlp.get_pipe('tagger')
			#>>> nlp.pipe_names #['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer', 'ner']
			#[nlp.remove_pipe(n) for n in ['tok2vec','parser', 'attribute_ruler','lemmatizer', 'ner'] ]
			[gram.nlp.remove_pipe(n) for n in ['parser',  'ner'] ]
		if not outfile: outfile = infile + ".postag"
		with open(outfile, 'w') as fw:
			for line in readline(infile):
				try:
					arr = line.strip().split("\t")[0:2]
					if len(arr) != 2: continue
					doc = gram.nlp(arr[0])
					poslist = " ".join([t.pos_ for t in doc])
					fw.write(f"{line.strip()}\t{poslist}\n")
				except Exception as e:
					print("ex:", e, line)
		print ("finished:", infile, outfile)

if __name__ == '__main__':
	fire.Fire(util)
