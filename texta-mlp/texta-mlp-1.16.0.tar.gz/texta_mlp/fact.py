import json
import uuid
from typing import List


class Fact:

    def __init__(self, source: str, fact_type: str, fact_value: str, doc_path: str = None, fact_lemma: str = None, spans: list = [[0, 0]], sent_index: int = 0):
        self.id = str(uuid.uuid4())
        self.source = source
        self.fact_type = fact_type
        self.fact_value = fact_value
        self.spans = spans
        self.sent_index = sent_index
        self.doc_path = doc_path
        self.fact_lemma = fact_lemma


    @staticmethod
    def from_json(list_of_facts: List[dict]):
        container = []
        for fact_json in list_of_facts:
            fact_type = fact_json.get("fact")
            spans = json.loads(fact_json.get("spans"))
            sent_index = fact_json.get("sent_index")
            value = fact_json.get("str_val")
            field_path = fact_json.get("doc_path")
            fact = Fact(source="mlp", fact_type=fact_type, fact_value=value, doc_path=field_path, spans=spans)
            container.append(fact)
        return container


    def to_json(self):
        container = {
            "id": self.id,
            "source": "mlp",
            "str_val": self.fact_value,
            "spans": json.dumps(self.spans),
            "sent_index": self.sent_index,
            "fact": self.fact_type,
            "doc_path": self.doc_path,
        }
        if self.fact_lemma:
            container["lemma"] = self.fact_lemma
        return container
