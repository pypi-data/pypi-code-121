import tensorflow as tf
from tensorflow import keras


def dense_encoder(
        input_shape: tuple = (1024, 1024, 1),
        latent_dims: tuple = (200, 100)
) -> keras.models.Model:
    inputs = keras.layers.Input(shape=input_shape, name="encoder-input")
    x = keras.layers.Flatten()(inputs)
    for idx, dims in enumerate(latent_dims):
        x = keras.layers.Dense(dims, activation="relu", name=f"encoder-dense-{idx+1}")(x)
    encoder = keras.models.Model(inputs, x, name="dense-encoder")
    return encoder


def dense_decoder(
        output_shape: tuple = (1024, 1024, 1),
        latent_dims: tuple = (100, 200)
) -> keras.models.Model:
    inputs = keras.layers.Input(shape=(latent_dims[0],), name="decoder-input")
    x = keras.layers.Dense(latent_dims[0], activation="relu", name="decoder-dense-1")(inputs)
    for idx, dims in enumerate(latent_dims[1:]):
        x = keras.layers.Dense(dims, activation="relu", name=f"decoder-dense-{idx+2}")(x)
    if not tf.math.reduct_prod(output_shape) == latent_dims[-1]:
        x = keras.layers.Dense(tf.math.reduce_prod(output_shape), activation="relu", name="decoder-output")(x)
    output = keras.layers.Reshape(output_shape)(x)
    decoder = keras.models.Model(inputs, output, name="dense-decoder")
    return decoder


def dense_autoencoder(
        input_shape: tuple = (1024, 1024, 1),
        latent_dims: tuple = (200, 100)
) -> keras.models.Model:
    model = keras.Sequential(name="dense-autoencoder")
    model.add(keras.layers.Input(input_shape))
    model.add(dense_encoder(input_shape, latent_dims))
    model.add(dense_decoder(input_shape, tuple(reversed(latent_dims))))
    return model
