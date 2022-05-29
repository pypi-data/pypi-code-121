
import textdistance
from nltk.tokenize import TreebankWordTokenizer
tokenizer = TreebankWordTokenizer()
hamming = textdistance.Hamming(external=False)
edits = lambda snt0="I like it.", snt1="I love it.": hamming(tokenizer.tokenize(snt0), tokenizer.tokenize(snt1))

def sent_diff(snt:str="I like it.", refsnt:str="I love it."):
	src_toks = tokenizer.tokenize(snt)
	ref_toks = tokenizer.tokenize(refsnt)
	edits = hamming(src_toks, ref_toks)
	return 1 - round(edits / len(ref_toks), 2) 

print (sent_diff())