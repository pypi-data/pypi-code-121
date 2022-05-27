import pickle
from pathlib import Path
from typing import List, Optional, Union

import numpy as np
import torch
import torch.nn.functional as F
from jina import DocumentArray, Executor, requests
from torch.nn import Linear, Module


def get_bi_modal_embedding(doc) -> Union[np.ndarray, torch.Tensor]:
    attributes = [doc.text, doc.blob]
    if not any(attributes) or all(attributes):
        raise ValueError(
            f'Received doc (id={doc.id}) with either no text and blob or both.'
        )
    zeros = np.zeros(doc.embedding.shape)
    if doc.text:
        order = (zeros, doc.embedding)
    else:
        order = (doc.embedding, zeros)
    return np.concatenate(order)


class LinearHead(Module):
    def __init__(self, final_layer_output_dim, embedding_size):
        super(LinearHead, self).__init__()
        self.linear1 = Linear(final_layer_output_dim, embedding_size, bias=False)

    def forward(self, x):
        x = x.float()
        x = self.linear1(x)
        normalized_embedding = F.normalize(x, p=2, dim=1)  # L2 normalize
        return normalized_embedding


def load_mean(mean_path):
    with open(mean_path, 'rb') as f:
        return pickle.load(f)


class FineTunedLinearHeadEncoder(Executor):
    def __init__(
        self,
        pre_trained_embedding_size,
        finetune_layer_size,
        bi_modal=True,
        model_path=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if not model_path:
            model_path = Path(__file__).parent / 'best_model_ndcg'
        self.bi_model = bi_modal
        self.pre_trained_embedding_size = pre_trained_embedding_size
        self.model = LinearHead(pre_trained_embedding_size, finetune_layer_size)
        self.model.load_state_dict(torch.load(model_path, map_location='cpu'))

    @requests
    def encode(self, docs: Optional[DocumentArray], **kwargs):
        content_attr = FineTunedLinearHeadEncoder._preserve_content_attribute(docs)
        for d in docs:
            if (
                self.bi_model
                and d.embedding.shape[0] != self.pre_trained_embedding_size
            ):
                d.tensor = get_bi_modal_embedding(d)
            else:
                assert (
                    d.embedding is not None
                ), f'Expected embedding but doc (id={d.id}) has None.'
                d.tensor = d.embedding
            d.embedding = None

        docs.embed(self.model)
        for d, text, blob in zip(docs, *content_attr):
            if type(d.embedding) != np.ndarray:
                d.embedding = d.embedding.numpy()
            if text:
                d.text = text
            if blob:
                d.blob = blob

        return docs

    @staticmethod
    def _preserve_content_attribute(
        docs: DocumentArray,
    ) -> List[Union[List[Optional[str]], List[Optional[bytes]]]]:
        return [[d.text for d in docs], [d.blob for d in docs]]
