from transformers import T5Tokenizer, T5ForConditionalGeneration
from typing import List, Dict
from .basic_model import BasicModel
import torch
from torch.utils.data import Dataset, DataLoader
import re
import jsonlines
import tqdm

__all__ = ["T5Model"]


class T5Dataset(Dataset):
    def __init__(self, items):
        super().__init__()
        self.items = items

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        return self.items[index]


class T5Collator:
    def __init__(self, pad_token_id):
        self.pad_token_id = pad_token_id

    def __call__(self, batch: List[Dict[str, List[int]]]) -> Dict[str, torch.Tensor]:
        m = max(len(x["input_ids"]) for x in batch)
        d = {
            "input_ids": torch.stack(
                [torch.tensor(x["input_ids"] + [self.pad_token_id] * (m - len(x["input_ids"]))) for x in batch]),
            "attention_mask": torch.stack(
                [torch.tensor(x["attention_mask"] + [0] * (m - len(x["attention_mask"]))) for x in batch])
        }
        return d


class T5Model(BasicModel):
    def __init__(self, model_dir):
        super().__init__()
        self.model = T5ForConditionalGeneration.from_pretrained(model_dir)
        self.model.to(self.device).eval()
        self.tokenizer = T5Tokenizer.from_pretrained(model_dir)
        self.max_len = 200

    def prepare_data(self, premise, hypothesis):
        inputs = ["terra посылка: " + premise + " гипотеза: " + hypothesis]
        res = self.tokenizer.batch_encode_plus(
            inputs,
            return_attention_mask=False,
            max_length=self.max_len,
            truncation=True
        )
        return {
            "input_ids": torch.tensor(
                res["input_ids"][0] + [self.tokenizer.pad_token_id] * (self.max_len - len(res["input_ids"][0]))),
            "attention_mask": torch.tensor(
                [1] * len(res["input_ids"][0]) + [0] * (self.max_len - len(res["input_ids"][0]))),
        }

    @staticmethod
    def postprocess(s):
        s = s.replace("<pad>", "")
        s = s.replace("</s>", "")
        s = re.sub("\s+", " ", s)
        s = s.strip()
        return s

    def predict(self, inputs):
        di = {"следует": 1, "не следует": 0}
        with torch.no_grad():
            x = self.model.generate(
                input_ids=inputs["input_ids"].reshape((1, -1)).to(self.device),
                attention_mask=inputs["attention_mask"].reshape((1, -1)).to(self.device),
                max_length=16,
                do_sample=False,
                num_beams=1
            )
            preds_i = self.tokenizer.batch_decode(x.to("cpu"))
            for p in preds_i:
                p = self.postprocess(p)
                if p in di:
                    return di[p]
                else:
                    return False

    def validate(self, filename):
        data = self._get_data(filename)
        data_ids = self._tokenize(data)
        collator = T5Collator(pad_token_id=self.tokenizer.pad_token_id)
        ds_test = T5Dataset(self._get_items(data_ids))
        loader = DataLoader(ds_test, batch_size=8, collate_fn=collator)
        targets = [i["targets"] for i in data]
        preds = []
        with torch.no_grad():
            for batch in tqdm.tqdm(loader):
                x = self.model.generate(
                    input_ids=batch["input_ids"].to(self.device),
                    attention_mask=batch["attention_mask"].to(self.device),
                    max_length=16,
                    do_sample=False,
                    num_beams=1
                )
                preds_i = self.tokenizer.batch_decode(x.to("cpu"))
                for p in preds_i:
                    p = self.postprocess(p)
                    preds.append(p)
        return sum([p == t for p, t in zip(preds, targets)])/len(targets)

    @staticmethod
    def _get_data(filename):
        data = []
        di = {"entailment": "следует", "not_entailment": "не следует"}
        with jsonlines.open(filename) as reader:
            for obj in reader:
                idx = obj["idx"]
                inputs = "terra посылка: " + obj["premise"] + " гипотеза: " + obj["hypothesis"]
                output = di[obj["label"]]
                data.append({"idx": idx, "inputs": inputs, "targets": output})
        return data

    def _tokenize(self, data):
        inputs = []
        targets = []
        for x in data:
            inputs.append(x["inputs"])
            if "targets" in x:
                targets.append(x["targets"])
        res = self.tokenizer.batch_encode_plus(
            inputs,
            return_attention_mask=False,
            max_length=self.max_len,
            truncation=True
        )
        if len(targets) != 0:
            assert len(targets) == len(inputs)
            res["target_ids"] = self.tokenizer.batch_encode_plus(
                targets,
                return_attention_mask=False,
                max_length=self.max_len,
                truncation=True
            )["input_ids"]
        return res

    @staticmethod
    def _get_items(ids):
        items = []
        for i in range(len(ids["input_ids"])):
            item = {
                "input_ids": ids["input_ids"][i],
                "attention_mask": [1] * len(ids["input_ids"][i]),
            }
            items.append(item)
        return items
