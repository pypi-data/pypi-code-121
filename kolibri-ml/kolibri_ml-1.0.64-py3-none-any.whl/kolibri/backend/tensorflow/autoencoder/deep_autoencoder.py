from tensorflow.keras import regularizers
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.models import Model

from kolibri.backend.tensorflow.autoencoder.base_autoencoder import BaseAutoEncoder


class SequenceAutoencoder(BaseAutoEncoder):

    @classmethod
    def get_default_hyper_parameters(cls):
        return {
            'nb-layers': 2,
            'sparsity': 0.01,
            'hidden': {
                'units': 100,
                'activation': 'relu'
            },
            'latent': {
                'units': 10,
                'activation': 'relu'
            },
            'output': {
                'activation': 'tanh'
            }
        }

    def build_model_arc(self):
        dim_in = self.input_dim


        #dim_out=self.hyper_parameters['latent']['units']
        dims_encoder = self.hyper_parameters['nb-layers']
        dims_decoding = dims_encoder
        input_img: object = Input(shape=(dim_in,), name='EncoderIn')

        encoded = input_img

        # Construct encoder layers
        out_dim = self.input_dim
        for i in range(dims_encoder):
            name = 'Encoder{0}'.format(i)
            out_dim = int(out_dim / 2)
            encoded = Dense(out_dim, activation='relu', name=name, activity_regularizer=regularizers.l2(self.hyper_parameters['sparsity']))(encoded)

        # Construct decoder layers
        # The decoded is connected to the encoders, whereas the decoder is not
        decoded = encoded
        decoder_input = Input(shape=(out_dim,), name='DecoderIn')

        decoder = decoder_input
        for i in range(dims_decoding):
            name = 'Decoder{0}'.format(i)

            activation = 'relu'
            out_dim = out_dim * 2
            decoder = Dense(out_dim, activation=activation, name=name, activity_regularizer=regularizers.l2(self.hyper_parameters['sparsity']))(decoder)

        decoder = Dense(self.input_dim, activation=activation, name='output')(decoder)

        self.encoder = Model(inputs=input_img, outputs=encoded)

        # instantiate decoder model

        self.decoder = Model(decoder_input, decoder, name='decoder')

        # autoencoder = encoder + decoder
        # instantiate autoencoder model
        self.autoencoder = Model(input_img,
                                 self.decoder(self.encoder(input_img)),
                                 name='autoencoder')

#		self.encoder = Model(input=input_img, output=encoded)
#		self.decoder = Model(input=decoder_input, output=decoder)

#		self.autoencoder.compile(optimizer='adadelta', loss='binary_crossentropy')
