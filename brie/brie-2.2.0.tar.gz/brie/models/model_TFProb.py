## BRIE model

import time
import numpy as np
from scipy.sparse import issparse

import tensorflow as tf
import tensorflow_probability as tfp
from tensorflow_probability import distributions as tfd


class Model_init():
    """Random initialize parameters for BRIE2 model
    """
    def __init__(self, Nc, Ng, Kc, Kg, intercept_shape, sigma_shape, 
                 intercept=None, sigma=None):
        if intercept is None:
            self.intercept = tf.random.normal(intercept_shape)
        else:
            self.intercept = tf.ones(intercept_shape) * intercept
            
        if sigma is None:
            self.sigma = tf.ones(sigma_shape)
        else:
            self.sigma = tf.ones(sigma_shape) * sigma
            
        self.Z_loc = tf.random.normal([Nc, Ng])
        self.Z_std = tf.math.exp(tf.random.normal([Nc, Ng]))
        
        self.Wc_loc = tf.random.normal([Kc, Ng])
        self.Wg_loc = tf.random.normal([Nc, Kg])



class BRIE2():
    """
    Ng : number of genes
    Nc : number of cells
    Kg : number of gene features
    Kc : number of cell features
    """
    def __init__(self, Nc, Ng, Kc=0, Kg=0, effLen=None,
                 intercept=None, intercept_mode='gene',
                 sigma=None, tau_prior=[3, 27], 
                 name=None, init_obj=None):
        self.Nc = Nc
        self.Ng = Ng
        self.Kc = Kc
        self.Kg = Kg
        self.effLen = effLen # (Ng, 3 * 2)
        self.intercept_mode = intercept_mode
        
        if intercept_mode.upper() == 'CELL':
            _intercept_shape = (Nc, 1)
            _sigma_shape = (Nc, 1)
        else:
            # for intercept_mode.upper() == 'GENE' and others
            # print("[BIRE2] Error: intercept_mode only supports gene or cell")
            _intercept_shape = (1, Ng)
            _sigma_shape = (1, Ng)
            
        if init_obj is None:
            # print("new init")
            init_obj = Model_init(Nc, Ng, Kc, Kg, _intercept_shape, 
                                  _sigma_shape, intercept, sigma)
            
        if intercept is None:
            self.intercept = tf.Variable(init_obj.intercept, name='bias', 
                constraint=lambda t: tf.clip_by_value(t, -9, 9))
        else:
            self.intercept = tf.constant(init_obj.intercept, name='bias')
            
        if sigma is None:
            self.sigma_log = tf.Variable(tf.math.log(init_obj.sigma), 
                                         name='sigma_log')
        else:
            self.sigma_log = tf.constant(tf.math.log(init_obj.sigma), 
                                         name='sigma_log')
            
        self.Z_loc = tf.Variable(init_obj.Z_loc, name='Z_loc',
            constraint=lambda t: tf.clip_by_value(t, -9, 9))
        self.Z_std_log = tf.Variable(tf.math.log(init_obj.Z_std), name='Z_var')
        
        self.Wc_loc = tf.Variable(init_obj.Wc_loc, name='Wc_loc')
        self.Wg_loc = tf.Variable(init_obj.Wg_loc, name='Wg_loc')
    

    @property
    def Z_std(self):
        return tf.math.exp(self.Z_std_log)
    
    @property
    def Psi(self):
        """Mean value of Psi in variational posterior"""
        return tf.sigmoid(self.Z_loc)
    
    @property
    def PsiDist(self):
        """Variational logitNormal distribution of Psi"""
        return tfd.LogitNormal(self.Z_loc, self.Z_std)
    
    @property
    def Psi95CI(self):
        """95% confidence interval around mean"""
        return (self.PsiDist.quantile(0.975).numpy() - 
                self.PsiDist.quantile(0.025).numpy())

    @property
    def sigma(self):
        """Standard deviation of predicted Z"""
        return tf.exp(self.sigma_log)

    @property
    def Z(self):
        """Variational posterior for the logit Psi"""
        return tfd.Normal(self.Z_loc, self.Z_std)
    
    @property
    def Z_prior(self):
        """Predicted informative prior for Z"""
        _zz_loc = tf.zeros((self.Nc, self.Ng))
        if self.Kc > 0 and self.Xc is not None:
            _zz_loc = tf.matmul(self.Xc, self.Wc_loc) 
        if self.Kg > 0 and self.Xg is not None:
            _zz_loc += tf.matmul(self.Wg_loc, self.Xg.T)
        _zz_loc += self.intercept
        return tfd.Normal(_zz_loc, self.sigma)
    
        
    def logLik_MC(self, count_layers, target="ELBO", MC_size=1):
        """Get marginal logLikelihood on variational or prior distribution
        with Monte Carlo sampling
        """
        # TODO: introduce sparse tensor in new development
        for i in range(len(count_layers)):
            if issparse(count_layers[i]):
                count_layers[i] = count_layers[i].toarray()
        
        # Reshape the tensors
        def _re1(x):
            return tf.expand_dims(x, 0)      #(1, Nc, Ng)
        def _re2(x): 
            return tf.expand_dims(x, (0, 1)) #(1, 1, Ng)
        
        
        ## Manual re-parametrization (VAE) - works similarly well as build-in
        ## https://gregorygundersen.com/blog/2018/04/29/reparameterization/
        # _zzz = tfd.Normal(0, 1).sample((size, self.Ng, self.Nc)) #(size, 1, 1)
        # if mode == "prior":
        #     _Z = _re1(self.sigma) * _zzz + _re1(self.Z_prior.parameters['loc'])
        # else:
        #     _Z = _re1(self.Z_std) * _zzz + _re1(self.Z_loc)
        
        
        ## Build-in re-parametrized: Gaussian is FULLY_REPARAMETERIZED
        if target == "marginLik":
            _Z = self.Z_prior.sample(MC_size)      # (size, Nc, Ng)
        else:
            _Z = self.Z.sample(MC_size)            # (size, Nc, Ng)
        
        ## Calculate element wise logLikelihood
        if self.effLen is None:
            Psi1_log = tf.math.log_sigmoid(_Z)
            Psi2_log = tf.math.log_sigmoid(0 - _Z)
            _logLik_S = (
                _re1(count_layers[0]) * Psi1_log + 
                _re1(count_layers[1]) * Psi2_log)
        else:
            _Z = tf.expand_dims(_Z, 3)
            Psi_logs = tf.concat(
                (tf.math.log_sigmoid(_Z), 
                 tf.math.log_sigmoid(0 - _Z), 
                 tf.zeros(_Z.shape)), axis=3)
    
            effLen = np.expand_dims(self.effLen, (0, 1)) # (1, 1, Ng, 3 * 2)
            phi_log = Psi_logs + tf.math.log(effLen[:, :, :, [0, 4, 5]])
            phi_log = phi_log - tf.math.reduce_logsumexp(phi_log, axis=3, 
                                                         keepdims=True)
            
            _logLik_S = (
                _re1(count_layers[0]) * phi_log[:, :, :, 0] + 
                _re1(count_layers[1]) * phi_log[:, :, :, 1])
            
            if len(count_layers) > 2:
                _logLik_S += _re1(count_layers[2]) * phi_log[:, :, :, 2]
                
        ## return the mean over the sampling
        if target == "marginLik":
            return tfp.math.reduce_logmeanexp(_logLik_S, axis=0)
        else:
            return tf.reduce_mean(_logLik_S, axis=0)
    

    def get_loss(self, count_layers, target="ELBO", axis=None, **kwargs):
        """Loss function per gene (axis=0) or all genes
        
        Please be careful: for loss function, you should reduce_sum of each 
        module first then add them up!!! Otherwise, it doesn't work propertly
        by adding modules first and then reduce_sum.
        """
        ## target function
        if target == "marginLik":
            return -tf.reduce_sum(
                self.logLik_MC(count_layers, target="marginLik", **kwargs), 
                axis=axis)
        else:
            return (
                tf.reduce_sum(tfd.kl_divergence(self.Z, self.Z_prior), 
                              axis=axis) -
                tf.reduce_sum(self.logLik_MC(count_layers, target="ELBO", 
                                             **kwargs), axis=axis))

    
    def fit(self, count_layers, Xc=None, Xg=None, target="ELBO", optimizer=None, 
            learn_rate=0.05, min_iter=1000, max_iter=5000, add_iter=500, 
            epsilon_conv=1e-2, verbose=True, **kwargs):
        """Fit the model's parameters"""
        start_time = time.time()
        
        self.Xc = Xc  #(Nc, Kc)
        self.Xg = Xg  #(Ng, Kg)
        self.target = target
        
        ## target function
        loss_fn = lambda: self.get_loss(count_layers, target, **kwargs)
            
        ## optimization
        if optimizer is None:
            learn_rate = 0.01
            optimizer = tf.optimizers.Adam(learning_rate=learn_rate)
            #optimizer = tf.optimizers.Adagrad(learning_rate=learn_rate)
                
        # learning_rates = [0.001, 0.003, 0.005, 0.01, 0.005]
        learning_rates = [0.001, 0.005, 0.01, 0.02, 0.01, 0.005]
        # learning_rates = [0.001, 0.005, 0.015, 0.03, 0.015, 0.005, 0.003]
        for i in range(6):
            optimizer = tf.optimizers.Adam(learning_rate=learning_rates[i])
            
            losses = tfp.math.minimize(loss_fn, 
                                       num_steps=int(min_iter/6), 
                                       optimizer=optimizer)
        
#         losses = tfp.math.minimize(loss_fn, 
#                                    num_steps=min_iter, 
#                                    optimizer=optimizer)
        
        n_iter = min_iter + 0
        d1 = min(50, add_iter / 2)
        d2 = d1 * 2
        while ((losses[-d2:-d1].numpy().mean() - losses[-d1:].numpy().mean() > 
                epsilon_conv) and  n_iter < max_iter):
            n_iter += add_iter
            losses = tf.concat([
                losses,
                tfp.math.minimize(loss_fn, 
                                  num_steps=add_iter, 
                                  optimizer=optimizer)
            ], axis=0)
            
        
        self.loss_gene = self.get_loss(count_layers, target, axis=0).numpy()
        for it in range(499):
            self.loss_gene += self.get_loss(count_layers, target, axis=0).numpy()
        self.loss_gene = tf.constant(self.loss_gene / 500)
        
        self.losses = losses
        
        if verbose:
            print("[BRIE2] model fit with %d steps in %.2f min, loss: %.2f" %(
                n_iter, (time.time() - start_time) / 60, 
                tf.reduce_sum(self.loss_gene)))
            
        return losses
