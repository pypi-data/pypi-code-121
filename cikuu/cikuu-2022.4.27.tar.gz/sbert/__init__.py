# https://www.sbert.net/
import json 
from sentence_transformers import SentenceTransformer

if not hasattr(json, 'vecmodel'):
	json.vecmodel		= SentenceTransformer('all-MiniLM-L6-v2') # 384 dims
	json.vec_encode		= lambda snt : json.vecmodel.encode(snt)
