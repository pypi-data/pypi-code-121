
from tqdm import tqdm

from .Loader import Loader

class ConllLoader(Loader):

    def __init__(self) -> None:
        super().__init__()
        self.texts = []
        self.labels = []

    def load(self, file_name: str) -> None:
        texts = []
        labels = []
        with open(file_name, 'r', encoding='utf8') as f:
            simple_text = []
            simple_label = []
            for line in tqdm(f.readlines()):
                if line.strip() == "":
                    if simple_label != [] and simple_text != []:
                        assert len(simple_text) == len(simple_label)
                        texts.append(simple_text)
                        labels.append(simple_label)
                        simple_text = []
                        simple_label = []
                else:
                    token, tag = line.strip().split("\t")
                    simple_text.append(token)
                    simple_label.append(tag)
            assert len(texts) == len(labels)
        
        self.texts += texts
        self.labels += labels

