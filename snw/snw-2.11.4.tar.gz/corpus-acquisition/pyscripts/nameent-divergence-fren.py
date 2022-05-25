import spacy
import re
import argparse
import unicodedata
import re
from tqdm import tqdm

argparser = argparse.ArgumentParser()
argparser.add_argument('-f', '--file', required=True, type=str, help='Prefix of file to process')

args = argparser.parse_args()

f_fr = open(args.file+".fr")
f_en = open(args.file+".en")

print("#Loading entity models")
from spacy.lang.en import English
from spacy.lang.fr import French
nlp_fr = spacy.load("fr_core_news_sm")
nlp_en = spacy.load("en_core_web_sm")

f_mismatch = open(args.file+".fren-mismatch.txt", "w")
f_fr_keep = open(args.file+"-entkeep.fr", "w")
f_en_keep = open(args.file+"-entkeep.en", "w")

def norm_unicode(l):
    l = unicodedata.normalize('NFKD', l)
    l = u"".join([c for c in l if not unicodedata.combining(c)])
    l = l.lower().replace("ou", "u").replace("q","k")
    l = re.sub(r"([bcdfghjklmnpqrstvwxz])e(\b)", "\\1\\2", l.lower())
    return l

counter = 0
counter_with_person_entity = 0
mismatches = 0

count = 0
print("#Estimate file size")
for l_fr in f_fr:
    count = count + 1
f_fr.seek(0)

print("#Parse file %s,%s" % (args.file+".fr", args.file+".en"))
for (l_fr, l_en) in tqdm(zip(f_fr, f_en), total=count):
    doc_fr = nlp_fr(l_fr.strip())
    doc_en = nlp_en(l_en.strip())

    #print([e.text+"/"+e.label_ for e in doc_fr.ents]
    #	  , "--",
    #	  [e.text+"/"+e.label_ for e in doc_en.ents])

    ents_person_fr = [e.text for e in doc_fr.ents if e.label_=="PER"]
    ents_person_en = [e.text for e in doc_en.ents if e.label_=="PERSON"]

    if len(ents_person_en) > len(ents_person_fr):
        ok = True
        for e in ents_person_en:
            ok = ok and norm_unicode(l_fr).find(norm_unicode(e)) != -1
        if not ok:
            f_mismatch.write("\t".join([l_fr.strip(), ", ".join([a for a in ents_person_fr]),
                             			l_en.strip(), ", ".join([a for a in ents_person_en])])+"\n")
            mismatches += 1
        else:
            f_fr_keep.write(l_fr)
            f_en_keep.write(l_en)

    if len(ents_person_fr):
    	counter_with_person_entity += 1
    counter += 1
    if counter == 10000:
        break

print("#sentences", counter, "#withentity", counter_with_person_entity, "#mismatches", mismatches)
