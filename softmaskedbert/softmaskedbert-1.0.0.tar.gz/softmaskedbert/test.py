from inference import Corrector
from softmaskedbert3 import SmbModel


corrector = Corrector()
sentence = '她回国以后，男朋友就把他拍的像片寄给她。'
csentence = corrector.correct(sentence)
print(sentence)
print(csentence)