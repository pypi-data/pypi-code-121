from .abstract_inference_store import AbstractInferenceStore
from .sqlalchemy_inference_store import SqlAlchemyInferenceStore


def get_inference_store(uri: str) -> AbstractInferenceStore:
    # For now we have only one repo
    return SqlAlchemyInferenceStore(db_uri=uri)
