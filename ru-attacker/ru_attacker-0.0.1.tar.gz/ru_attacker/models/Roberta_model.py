from transformers import RobertaTokenizer, RobertaForSequenceClassification
from .basic_model import BasicModel
from torch.utils.data import Dataset, DataLoader
from .set_dataset import get_data
import torch
import tqdm

__all__ = ["RobertaModel"]


class DatasetTERRa(Dataset):
    def __init__(self, dataframe, tokenizer, max_len):
        self.len = len(dataframe)
        self.data = dataframe
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __getitem__(self, index):
        premise = self.data.iloc[index]['premise']
        hypothesis = self.data.iloc[index]['hypothesis']
        label = self.data.iloc[index]['label']
        pair_token_ids_padded = torch.zeros(self.max_len, dtype=torch.long)
        attention_mask_ids_padded = torch.zeros(self.max_len, dtype=torch.long)
        premise_id = self.tokenizer.encode(premise, add_special_tokens=False)
        hypothesis_id = self.tokenizer.encode(hypothesis, add_special_tokens=False)
        pair_token_ids = [self.tokenizer.cls_token_id] + premise_id + [self.tokenizer.sep_token_id] + hypothesis_id + [
            self.tokenizer.sep_token_id]
        if len(pair_token_ids) < self.max_len:
            pair_token_ids_padded[:len(pair_token_ids)] = torch.tensor(pair_token_ids)
        else:
            pair_token_ids_padded = torch.tensor(pair_token_ids[:self.max_len])

        premise_len = len(premise_id)
        hypothesis_len = len(hypothesis_id)
        attention_mask_ids = torch.tensor([1] * (premise_len + hypothesis_len + 3))
        if len(attention_mask_ids) < self.max_len:
            attention_mask_ids_padded[:len(attention_mask_ids)] = attention_mask_ids
        else:
            attention_mask_ids_padded = attention_mask_ids[:self.max_len]

        return {
            'input_ids': pair_token_ids_padded,
            'attention_mask': attention_mask_ids_padded,
            'labels': torch.tensor(label, dtype=torch.long)
        }

    def __len__(self):
        return self.len


class RobertaModel(BasicModel):
    def __init__(self, model_dir):
        super().__init__()
        # self.model = torch.load(model_dir, map_location=torch.device(self.device))
        self.model = RobertaForSequenceClassification.from_pretrained(model_dir)
        self.model.to(self.device).eval()
        self.tokenizer = RobertaTokenizer.from_pretrained(model_dir)
        self.max_len = 512

    def prepare_data(self, premise, hypothesis):
        pair_token_ids_padded = torch.zeros(self.max_len, dtype=torch.long)
        attention_mask_ids_padded = torch.zeros(self.max_len, dtype=torch.long)
        premise_id = self.tokenizer.encode(premise, add_special_tokens=False)
        hypothesis_id = self.tokenizer.encode(hypothesis, add_special_tokens=False)
        pair_token_ids = [self.tokenizer.cls_token_id] + premise_id + [self.tokenizer.sep_token_id] + hypothesis_id + [
            self.tokenizer.sep_token_id]
        if len(pair_token_ids) < self.max_len:
            pair_token_ids_padded[:len(pair_token_ids)] = torch.tensor(pair_token_ids)
        else:
            pair_token_ids_padded = torch.tensor(pair_token_ids[:self.max_len])

        premise_len = len(premise_id)
        hypothesis_len = len(hypothesis_id)
        attention_mask_ids = torch.tensor([1] * (premise_len + hypothesis_len + 3))
        if len(attention_mask_ids) < self.max_len:
            attention_mask_ids_padded[:len(attention_mask_ids)] = attention_mask_ids
        else:
            attention_mask_ids_padded = attention_mask_ids[:self.max_len]
        return {"input_ids": pair_token_ids_padded, "attention_mask": attention_mask_ids_padded}

    def predict(self, inputs):
        with torch.no_grad():
            input_ids = inputs["input_ids"].reshape((1, -1)).to(self.device)
            attention_mask = inputs["attention_mask"].reshape((1, -1)).to(self.device)

            prediction = self.model(input_ids=input_ids, attention_mask=attention_mask).logits
            prediction = torch.argmax(prediction, dim=1)
            return int(prediction[0])

    def validate(self, filename):
        data = get_data(filename)
        dataset = DatasetTERRa(data, self.tokenizer, self.max_len)
        loader = DataLoader(dataset, batch_size=16)
        targets = data["label"].tolist()
        preds = []
        with torch.no_grad():
            for batch in tqdm.tqdm(loader):
                x = self.model(
                    input_ids=batch["input_ids"].to(self.device),
                    attention_mask=batch["attention_mask"].to(self.device)
                ).logits.argmax(-1).tolist()
                preds.extend(x)
        return sum([p == t for p, t in zip(preds, targets)]) / len(targets)
