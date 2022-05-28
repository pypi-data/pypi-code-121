# https://segmentfault.com/a/1190000017825534
from flair.models import TextClassifier
from flair.data import Sentence

classifier = TextClassifier.load('./best-model.pt')
sentence = Sentence('Hi. Yes mum, I will...')
classifier.predict(sentence)
print(sentence.labels)
#[ham (0.9937)]
