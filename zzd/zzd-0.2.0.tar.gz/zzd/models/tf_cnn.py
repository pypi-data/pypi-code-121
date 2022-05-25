import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.models import  Model

def cnn(length=2000,chanels=20,dropout_rate=0.5,lr=0.001):
    In = layers.Input(shape=(length,chanels))
    x = layers.Conv1D(filters=32, kernel_size=3, padding='same', input_shape=(length,chanels))(In)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    x = layers.AvgPool1D(pool_size=4, padding='same')(x)

    x = layers.Conv1D(filters=64, kernel_size=3, strides=1, padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    x = layers.AvgPool1D(pool_size=4, padding='same')(x)

    x = layers.Conv1D(filters=128, kernel_size=3,padding='same')(x)
    x = layers.ReLU()(x)
    x = layers.AvgPool1D(pool_size=4, padding='same')(x)

    x = layers.Conv1D(filters=256, kernel_size=3, padding='same')(x)
    x = layers.ReLU()(x)
    x = layers.MaxPool1D(pool_size=4, strides=4, padding='same')(x)

    x = layers.Conv1D(filters=512, kernel_size=3, padding='same')(x)
    x = layers.ReLU()(x)
    x = layers.MaxPool1D(pool_size=4, strides=4, padding='same')(x)
    x = layers.Flatten()(x)
    convs = Model(In,x)
    In1 = layers.Input(shape=(length, chanels))
    In2 = layers.Input(shape=(length, chanels))
    x1 = convs(In1)
    x2 = convs(In2)
    x_merge = layers.Concatenate()([x1,x2])
    fc1 = layers.Dense(512, activation='relu')(x_merge)
    fc1 = layers.Dropout(dropout_rate)(fc1)
    fc2 = layers.Dense(1, activation='sigmoid')(fc1)
    model = Model([In1,In2],[fc2])

    model.compile(loss = tf.keras.losses.BinaryCrossentropy(),
                optimizer=tf.keras.optimizers.Adam(learning_rate=lr),metrics=['accuracy'])

    return model

