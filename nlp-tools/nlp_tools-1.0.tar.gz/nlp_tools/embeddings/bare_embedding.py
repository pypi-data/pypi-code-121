from typing import Dict, Any, Optional
from tensorflow import keras

from nlp_tools.embeddings.abc_embedding import ABCEmbedding
L = keras.layers


class BareEmbedding(ABCEmbedding):
    """
    BareEmbedding is a random init `tf.keras.layers.Embedding` layer for text sequence embedding,
    which is the defualt embedding class for kashgari models.
    """

    def __init__(self,
                 embedding_size: int = 100,
                 vocab_size: int = 100,
                 **kwargs: Any):
        """

        Args:
            embedding_size: Dimension of the dense embedding.
            kwargs: additional params
        """
        self.embedding_size: int = embedding_size
        self.vocab_size = vocab_size
        super(BareEmbedding, self).__init__(embedding_size=embedding_size,
                                            **kwargs)

    def load_embed_vocab(self) -> Optional[Dict[str, int]]:
        return None

    def build_embedding_model(self) -> None:
        if self.embed_model is None :
            input_tensor = L.Input(shape=(None,),
                                   name=f'input')
            #segement_tensor = L.Input(shape=(None,))
            layer_embedding = L.Embedding(self.vocab_size,
                                          self.embedding_size,
                                          mask_zero=True,
                                          name=f'layer_embedding')

            embedded_tensor = layer_embedding(input_tensor)
            self.embed_model = keras.Model(input_tensor, embedded_tensor)



