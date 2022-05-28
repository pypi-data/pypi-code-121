# 2022.2.7
import streamlit as st
import spacy
import pandas as pd

nlp			= spacy.load('en_core_web_sm')
merge_nps	= nlp.create_pipe("merge_noun_chunks")
postag		= lambda snt: pd.DataFrame([ (t.text, t.tag_) for t in nlp(snt)], columns=['word','pos'])
tokenize	= lambda snt: " ".join([t.text for t in nlp(snt) if len(t.text.strip())]).strip()

def parse(snt, merge_np= False):
	doc = nlp(snt)
	if merge_np : merge_nps(doc)
	return pd.DataFrame({'word': [t.text for t in doc], 'tag': [t.tag_ for t in doc],'pos': [t.pos_ for t in doc],'head': [t.head.orth_ for t in doc],'dep': [t.dep_ for t in doc], 'lemma': [t.text.lower() if t.lemma_ == '-PRON-' else t.lemma_ for t in doc],
	'n_lefts': [ t.n_lefts for t in doc], 'left_edge': [ t.left_edge.text for t in doc], 
	'n_rights': [ t.n_rights for t in doc], 'right_edge': [ t.right_edge.text for t in doc],
	}) #'subtree': str([ list(t.subtree) for t in doc]),'children': str([ list(t.children) for t in doc]),

st.title("Sentence parsing")
snt = st.text_input("Input a sentence", "The quick fox jumped over the lazy dog.")
merge_np = st.checkbox('merge NP', value=False)
if st.button("submit"):
	df = parse(snt, merge_np)
	st.write(df)
