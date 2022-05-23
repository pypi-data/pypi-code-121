import tensorflow as tf  # Only used for various tensor operations
from keras.layers import Layer, Dense


# A more general and complete version of the layer defined in the linked keras example

class MultiHeadSelfAttention(Layer):
    """ This uses Bahadanau attention """

    def __init__(self, num_heads=8, weights_dim=64):
        """ Constructor: Initializes parameters of the Attention layer """

        # Initialize base class:
        super(MultiHeadSelfAttention, self).__init__()

        # Initialize parameters of the layer:
        self.num_heads = num_heads
        self.weights_dim = weights_dim

        if self.weights_dim % self.num_heads != 0:
            raise ValueError(
                f"Weights dimension = {weights_dim} should be divisible by number of heads = {num_heads} to ensure proper division into sub-matrices")

        # We use this to divide the Q,K,V matrices into num_heads submatrices, to compute multi-headed attention
        self.sub_matrix_dim = self.weights_dim // self.num_heads

        """
            Note that all K,Q,V matrices and their respective weight matrices are initialized and computed as a whole
            This ensures somewhat of a parallel processing/vectorization
            After computing K,Q,V, we split these into num_heads submatrices for computing the different attentions
        """

        # Weight matrices for computing query, key and value (Note that we haven't defined an activation function anywhere)
        # Important: In keras units contain the shape of the output
        self.W_q = Dense(units=weights_dim)
        self.W_k = Dense(units=weights_dim)
        self.W_v = Dense(units=weights_dim)

    def get_config(self):
        """ Required for saving/loading the model """
        config = super().get_config().copy()
        config.update({
            "num_heads": self.num_heads,
            "weights_dim": self.weights_dim
            # All args of __init__() must be included here
        })
        return config

    def build(self, input_shape):
        """ Initializes various weights dynamically based on input_shape """
        input_dim = input_shape[-1]
        self.input_dim = input_dim
        # Weight matrix for combining the output from multiple heads:
        # Takes in input of shape (batch_size, seq_len, weights_dim) returns output of shape (batch_size, seq_len, input_dim)
        self.W_h = Dense(units=input_dim)

    def attention(self, query, key, value):
        """ The main logic """
        # Compute the raw score = QK^T
        score = tf.matmul(query, key, transpose_b=True)

        # Scale by dimension of K
        dim_key = tf.cast(tf.shape(key)[-1], tf.float32)  # == DIM_KEY
        scaled_score = score / tf.math.sqrt(dim_key)

        # Weights are the softmax of scaled scores
        weights = tf.nn.softmax(scaled_score, axis=-1)

        # The final output of the attention layer (weighted sum of hidden states)
        output = tf.matmul(weights, value)

        return output, weights

    def separate_heads(self, x, batch_size):
        """
            Splits the given x into num_heads submatrices and returns the result as a concatenation of these sub-matrices
        """
        x = tf.reshape(x, (batch_size, -1, self.num_heads, self.sub_matrix_dim))
        return tf.transpose(x, perm=[0, 2, 1, 3])

    def call(self, inputs):
        """ All computations take place here """

        batch_size = tf.shape(inputs)[0]

        # Compute Q = W_q*X
        query = self.W_q(inputs)  # (batch_size, seq_len, weights_dim)

        # Compute K = W_k*X
        key = self.W_k(inputs)  # (batch_size, seq_len, weights_dim)

        # Compute V = W_v*X
        value = self.W_v(inputs)  # (batch_size, seq_len, weights_dim)

        # Split into n_heads submatrices
        query = self.separate_heads(query, batch_size)  # (batch_size, num_heads, seq_len, sub_matrix_dim)
        key = self.separate_heads(key, batch_size)  # (batch_size, num_heads, seq_len, sub_matrix_dim)
        value = self.separate_heads(value, batch_size)  # (batch_size, num_heads, seq_len, sub_matrix_dim)

        # Compute attention (contains weights and attentions for all heads):
        attention, weights = self.attention(query, key, value)
        attention = tf.transpose(attention, perm=[0, 2, 1, 3])  # (batch_size, seq_len, num_heads, sub_matrix_dim)

        # Concatenate all attentions from different heads (squeeze the last dimension):
        concat_attention = tf.reshape(attention,
                                      (batch_size, -1, self.weights_dim))  # (batch_size, seq_len, weights_dim)

        # Use a weighted average of the attentions from different heads:
        output = self.W_h(concat_attention)  # (batch_size, seq_len, input_dim)

        return output

    def compute_output_shape(self, input_shape):
        print(input_shape)
        """ Specifies the output shape of the custom layer, without this, the model doesn't work """
        return input_shape