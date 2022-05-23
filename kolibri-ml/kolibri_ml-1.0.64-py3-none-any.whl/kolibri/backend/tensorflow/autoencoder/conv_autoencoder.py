import numpy as np
from tensorflow.keras.layers import Input, Conv1D, GlobalMaxPool1D, Dense, MaxPooling1D, Flatten, Reshape, UpSampling1D
from tensorflow.keras.models import Sequential, Model

from kolibri.backend.tensorflow.autoencoder.base_autoencoder import BaseAutoEncoder


class Conv1DAutoencoder(BaseAutoEncoder):

    @classmethod
    def get_default_hyper_parameters(cls):
        return {
            'conv1d_layer': {
                'filters': 128,
                'kernel_size': [5],
                'activation': 'relu'
            },
            'max_pool_layer': {},
            'dense_layer': {
                'units': 64,
                'activation': 'relu'
            },
            'activation_layer': {
                'activation': 'softmax'
            },
            'multipooling': False
        }

    def build_model_arc(self):
        NUM_WORDS = 3
        pool_size = 2
        x = Input(shape=(32, 100), name="input")
        h = x
        h = Conv1D(filters=100, kernel_size=NUM_WORDS,
                   activation="relu", padding='same', name='Conv1')(h)
        h = MaxPooling1D(pool_size=pool_size, name='Maxpool1')(h)
        h = Conv1D(filters=50, kernel_size=NUM_WORDS,
                   activation="relu", padding='same', name='Conv2')(h)
        h = MaxPooling1D(pool_size=pool_size, name="Maxpool2")(h)
        h = Flatten()(h)
        h = Dense(8, name='embedding')(h)
        y = h
        y = Dense(1050, activation="relu")(y)
        y = Reshape((8, 150))(y)
        y = Conv1D(filters=50, kernel_size=NUM_WORDS,
                   activation="relu", padding='same', name='conv-decode1')(y)
        y = UpSampling1D(size=pool_size, name='upsampling1')(y)
        y = Conv1D(filters=100, kernel_size=NUM_WORDS,
                   activation="relu", padding='same', name='conv-decode2')(y)
        y = UpSampling1D(size=pool_size, name='upsampling2')(y)

        autoencoderM = Model(x, y)
        myLoss = 'mean_squared_error'
        autoencoderM.compile(optimizer='adadelta', loss=myLoss)

        autoencoderM.summary()  # will print





        self.autoencoder = Sequential()
        self.autoencoder.add(Conv1D(filters=256, kernel_size=5, padding='same', activation='relu',
                         input_shape=(self.input_dim, 1)))
        self.autoencoder.add(GlobalMaxPool1D())

        self.autoencoder.add(Dense(units=self.input_dim, activation='linear'))

    def fit(self, x_train, x_validate=None,batch_size=32, epochs=10,callbacks=None, fit_kwargs=None, shuffle= True):
        """

        """
        self.build_model(x_train)

        return self.autoencoder.fit(np.expand_dims(x_train, axis=2), x_train,
                                        epochs=epochs,
                                        validation_data=(x_validate, x_validate),
#                                        callbacks=callbacks
                                        )


    def predict(self,
               x_data,
               batch_size=32,
               debug_info=False,
               predict_kwargs= None):
        """
        Generates output predictions for the encoder.
        """
        if predict_kwargs is None:
            predict_kwargs = {}
        pred = self.autoencoder.predict(np.expand_dims(x_data,axis=2), batch_size=batch_size, **predict_kwargs)

        return pred