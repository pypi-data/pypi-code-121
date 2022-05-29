#2022.2.17
import en
from en import terms, verbnet 

doc = spacy.getdoc("The quick fox jumped over the lazy dog.")
terms.attach(doc) 
verbnet.attach(doc)
print(doc.user_data)