import torch
from config import Config
from transformers import BertTokenizer


class Corrector(object):
    def __init__(self):
        super(Corrector, self).__init__()
        self.config = Config()
        self.tokenizer = BertTokenizer.from_pretrained(self.config.vocab_file)
        self.model = torch.load('model/checkpoints/skpt_epoch5.pt', map_location = self.config.device)
        self.model.eval()
        self.vocabs = []
        with open('model/chinese-bert-wwm-ext/vocab.txt', 'r', encoding='utf-8') as f:
            for char in f.readlines():
                self.vocabs.append(char.strip())

    def correct(self, sentence):
        input_id = self.tokenizer.convert_tokens_to_ids(['[CLS]'] + list(sentence) + ['[SEP]'])
        mask = [1] * len(input_id)
        input_id = torch.tensor(input_id).view(1,-1)
        mask = torch.tensor(mask).float().view(1,-1)
        detect_prob, correct_prob = self.model.forward(input_id.to(self.config.device), mask.to(self.config.device))
        detect_prob = detect_prob.flatten()
        detect_prob = detect_prob[1:-1]
        correct_text = sentence
        details = {}
        for idx in range(len(detect_prob)):
            if detect_prob[idx] > 0.1:
                #这里是idx+1的原因是correct的返回结果包括增加的首尾（不同于detect）
                t = correct_prob[0][idx+1].argmax()
                word = self.vocabs[t]
                correct_text = list(correct_text)
                correct_text[idx] = word
                correct_text = ''.join(correct_text)
                if sentence[idx] != word:
                    details[sentence[idx]] = word
        return correct_text, details
