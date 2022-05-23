from tensorflow.keras import backend as K
from tensorflow.keras.layers import Lambda, Input, Dense
from tensorflow.keras.losses import mse, binary_crossentropy
from tensorflow.keras.models import Model

from kolibri.backend.tensorflow.autoencoder.base_autoencoder import BaseAutoEncoder


class VariationalAutoencoder(BaseAutoEncoder):

    def sampling(self, args):
        """Reparameterization trick by sampling
            fr an isotropic unit Gaussian.

        # Arguments:
            args (tensor): mean and log of variance of Q(z|X)

        # Returns:
            z (tensor): sampled latent vector
        """

        z_mean, z_log_var = args
        # K is the keras backend
        batch = K.shape(z_mean)[0]
        dim = K.int_shape(z_mean)[1]
        # by default, random_normal has mean=0 and std=1.0
        epsilon = K.random_normal(shape=(batch, dim))
        return z_mean + K.exp(0.5 * z_log_var) * epsilon

    @classmethod
    def get_default_hyper_parameters(cls):
        return {
            'layer_multiplyer': 2,
            'input_distribution': 'gaussian',
            'hidden': {
                'units': 100,
                'activation': 'relu'
            },
            'latent':{
                'units': 10,
                'activation': 'relu'
                       },
            'output': {
                'activation': 'tanh'
                }
                }

    def build_model_arc(self):
        # network parameters
        input_shape = (self.input_dim,)
        latent_dim = self.hyper_parameters['latent']['units']

        # VAE model = encoder + decoder
        # build encoder model
        inputs = Input(shape=input_shape, name='encoder_input')
        x = Dense(**self.hyper_parameters['hidden'])(inputs)
        z_mean = Dense(**self.hyper_parameters['latent'], name='z_mean')(x)
        z_log_var = Dense(**self.hyper_parameters['latent'], name='z_log_var')(x)

        # use reparameterization trick to push the sampling out as input
        # note that "output_shape" isn't necessary
        # with the TensorFlow backend
        z = Lambda(self.sampling,
                   output_shape=(latent_dim,),
                   name='z')([z_mean, z_log_var])

        # instantiate encoder model
        self.encoder = Model(inputs, [z_mean, z_log_var, z], name='encoder')


        # decoder model
        latent_inputs = Input(shape=(latent_dim,), name='z_sampling')
        x = Dense(**self.hyper_parameters['hidden'])(latent_inputs)
        outputs = Dense(self.input_dim, activation='sigmoid')(x)

        # instantiate decoder model
        self.decoder = Model(latent_inputs, outputs, name='decoder')

        # instantiate VAE model
        outputs = self.decoder(self.encoder(inputs)[2])
        self.autoencoder = Model(inputs, outputs, name='vae_mlp')

        # VAE loss = mse_loss or xent_loss + kl_loss
        if self.hyper_parameters['input_distribution']=='bernoulli':
            reconstruction_loss = binary_crossentropy(inputs,
                                                      outputs)
        else:
            reconstruction_loss = mse(inputs, outputs)

        reconstruction_loss *= self.input_dim
        kl_loss = 1 + z_log_var - K.square(z_mean) - K.exp(z_log_var)
        kl_loss = K.sum(kl_loss, axis=-1)
        kl_loss *= -0.5
        vae_loss = K.mean(reconstruction_loss + kl_loss)
        self.autoencoder.add_loss(vae_loss)

if __name__ == "__main__":
    from kolibri.data.text.corpus import CreditCardFraud



    corpus = CreditCardFraud()
    train_x=corpus.X

    model = Autoencoder()
    model.build_model(train_x[:100])



    epochs = 4
    history = None
    model.fit(train_x[0:20000], epochs=epochs)

    model.evaluate(train_x[0:10000])

