from docarray import Document
import numpy as np
import yaml


def load_config(filename):
    with open(filename, "r") as file:
        config = yaml.safe_load(file)

    return config


def preproc(doc: Document, dims=(64, 64)):
    doc.load_uri_to_image_tensor()
    doc.tensor = doc.tensor.astype(np.uint8)

    doc.set_image_tensor_normalization().set_image_tensor_shape(dims)


class Formats:
    table = ["csv"]
    image = ["jpg", "jpg", "png"]

default_config = {
    "host": "http://0.0.0.0:45678",
    "indexing": {
        "data": "./data",
        "num_docs": 1_000_000,
    },
    "searching": {
        "image_size": [64, 64]
    }
}
