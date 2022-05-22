import numpy as np
import pandas as pd
import plotly.express as px


class Neuron:
    """A single neuron with an activation function.
       Attributes:
          bias:     The bias term. By defaul it's 1.0.
          weights:  List of weights incl. bias
          activ:    The activation function: linear (default), relu, mrelu (modified relu), sigmoid.
          param:    parameter of mrelu activ function -- slope of negatives. 0.01 by default."""

    def __init__(self, inputs, bias = 1.0, activ = 'linear'):
        """Return a new Perceptron object with the specified number of inputs (+1 for the bias) and random initial weights.
        inputs:   The number of inputs in the perceptron, not counting the bias.""" 
        self.weights = (np.random.rand(inputs+1) * 2) - 1 
        self.bias = bias
        self.activ = activ

    def run(self, x):
        """Run the perceptron according the activ function. x is a list with a single row of the input data."""
        sum = np.dot(np.append(x,self.bias),self.weights)
        if self.activ == 'linear':
          return sum
        if self.activ == 'sigmoid':
          return self.sigmoid(sum)
        if self.activ == 'relu':
          return self.relu(sum)
        if self.activ == 'mrelu':
          return self.mrelu(sum)

    def set_weights(self, w_init):
        """Overrides the np.random.rand() weights and the bias weight.
           w_init is a list of numbers. Turns to a numpy array of doubles."""
        self.weights=np.array(w_init, dtype='double')

    def set_activ(self, activ, param=0):
        """Overrides the 'linear' activation function."""
        self.activ = activ
        self.param = param

    def sigmoid(self, x):
        """Returns the sigmoid of the input"""
        # return the output of the sigmoid function applied to x
        return 1/(1+np.exp(-x))
    
    def relu(self, x):
        """Returns the RELU of the input"""
        # return the output of the relu function applied to x
        if x >= 0:
          return x
        return 0

    def mrelu(self, x):
        """Returns the modified RELU of the input. The parameter is a slope for negatives"""
        # return the output of the modified relu function applied to x
        if x >= 0:
          return x
        return self.param*x
    
class MultiLayerNeuron:     
    """A multilayer neuron class that uses the Neuron class.
       Builds a list of neurons with the specific activation function.
       The activation function may be modified later using the set_activ method.
       For example: self.network[layer][neuron].set_activ('linear'). Layer 0 is an input.
       Attributes:
          layers:  A list with the number of neurons per layer. Including the input (0) and the output (last) layers.
          bias:    The bias term. The same bias is used for all neurons.
          network: self.network[layer][neuron] -- list of lists of Neurons. Layer 0 is an inputs.
          param:   Parameter of mrelu activ function -- slope of negatives. 0.01 by default.
          eta:     Learning rate."""

    def __init__(self, layers, bias = 1.0, activ='linear'):
        """Return a new MLP object with the specified parameters.
           layers -- a list of layers. [0] is a number of the model's features.
           Activation function is linear by default.""" 
        self.layers = np.array(layers,dtype=object)
        self.bias = bias
        self.network = [] # The list of lists of neurons (perceptrons).
        self.values = []  # The list of lists of neurons' (perceptrons') output values.
        self.d = []       # The list of lists of error terms (lowercase deltas)
        self.activ = activ

        # 2 nested loops to create neurons layer by layer
        for i in range(len(self.layers)): # outer loop iterates on each layer
            self.values.append([]) #The new list of values will be filled with zeros, for every neuron in the layer. 
            self.values[i] = [0.0 for j in range(self.layers[i])]
            self.d.append([])
            self.d[i] = [0.0 for j in range(self.layers[i])]                        
            self.network.append([])
            if i > 0:      #network[0] is the input layer, so it has no neurons
                for j in range(self.layers[i]): # inner loop iterates on each neuron in a layer
                    neur=Neuron(inputs = self.layers[i-1], bias = self.bias, activ = self.activ) # 
                    self.network[i].append(neur) # adding j perceptrons
        self.network = np.array([np.array(x) for x in self.network],dtype=object) #transforms list of lists to numpy array
        self.values = np.array([np.array(x) for x in self.values],dtype=object)
        self.d = np.array([np.array(x) for x in self.d],dtype=object)

    def set_weights(self, w_init): # set_weights of the MultiLayer class
        """Set the weights. 
           Overrides the np.random.rand() weights and the bias weight.
           w_init -- a list of lists with the weights for all but the input layer. Incl. the bias. """
        for i in range(len(w_init)):
            for j in range(len(w_init[i])):
                self.network[i+1][j].set_weights(w_init[i][j]) # set_weights for each perceptron i

    def set_activ(self, activ, param=0):
        """Set the activation function to every neurons.
           activ -- a string of 'linear' (default), 'relu', 'mrelu' (modified relu), 'sigmoid'.
           param -- parameter for mrelu."""
        for i in range(1,len(self.network)):
            for j in range(self.layers[i]):
                self.network[i][j].set_activ(activ, param) # set_activ for each neuron
        self.param=param
    
    def set_output_activ(self, activ, param=0):
        """Set the activation function to the last (output) neurons.
           activ -- a string of 'linear' (default), 'relu', 'mrelu' (modified relu), 'sigmoid'.
           param -- parameter for mrelu."""
        i = len(self.network)-1
        for j in range(self.layers[i]):
            self.network[i][j].set_activ(activ, param) 

    def printWeights(self):
        """Displays a summary of weights and activation functions per layer and neuron."""
        print()
        print('Layer 0 is the Input Layer')
        for i in range(1,len(self.network)):
            for j in range(self.layers[i]):
                print("Layer",i,"Neuron",j,":",self.network[i][j].weights,self.network[i][j].activ)
        print()

    def run(self, x):
        """Feed a single row of x into the MultiLayer Neuron.
           Returns the output of the last neuron."""
        x = np.array(x,dtype=object)
        self.values[0] = x
        for i in range(1,len(self.network)):
            for j in range(self.layers[i]):  
                self.values[i][j] = self.network[i][j].run(self.values[i-1]) #runs preceptrons with the previous outputs
        return self.values[-1]

    def bp_classif(self, x, y, eta=0.2):
        """Run a single (x,y) pair with the backpropagation algorithm - Gradient Descent.
           Uses the derivative of the SIGMOID function."""
        x = np.array(x,dtype=object)
        y = np.array(y,dtype=object)
        self.eta=eta
        # STEP 1: Feed a sample to the network 
        outputs = self.run(x)
        # STEP 2: Calculate the MSE
        error = 2*(y - outputs) # A list of outputs
        MSE = sum( error ** 2) / self.layers[-1] 
        # ∂MSE/∂weight=∂MSE/∂output*∂output/∂weight
        # STEP 3: Calculate the OUTPUT error terms
        # ∂MSE/∂output -- depends on neuron's activation function
        self.d[-1] = outputs * (1 - outputs) * (error) # derivative of the SIGMOID function 
        # STEP 4: Calculate the error term of EACH UNIT on each layer
        for i in reversed(range(1,len(self.network)-1)):
            for h in range(len(self.network[i])):
                fwd_error = 0.0
                for k in range(self.layers[i+1]): 
                    fwd_error += self.network[i+1][k].weights[h] * self.d[i+1][k]               
                self.d[i][h] = self.values[i][h] * (1-self.values[i][h]) * fwd_error # derivative of the SIGMOID function
        # STEPS 5 & 6: Calculate the deltas and update the weights
        for i in range(1,len(self.network)): # runs on layers
            for j in range(self.layers[i]): # runs on neurons
                for k in range(self.layers[i-1]+1): # runs on inputs. +1 for bias
                    if k==self.layers[i-1]:
                        delta = self.eta * self.d[i][j] * self.bias
                    else:
                        delta = self.eta * self.d[i][j] * self.values[i-1][k] # applying the delta rule
                    self.network[i][j].weights[k] += delta
        return MSE

    def sigmoid(self, x):
        """Return the output of the sigmoid function applied to x"""
        return 1/(1+np.exp(-x))

    def deriv(self, value, i, j=0):
        '''Calculates the derivative of the activ function for the back propagation'''
        if self.network[i][j].activ == 'linear':
          # print ('lin')
          return 1
        if self.network[i][j].activ == 'sigmoid':
          # print ('sig')
          return self.sigmoid(value)*(1-self.sigmoid(value))
        if self.network[i][j].activ == 'relu':
          if value > 0:
            # print ('re>')
            return 1
          else:
            # print ('re<')
            return 0
        if self.network[i][j].activ == 'mrelu':
          if value > 0:
            return 1
          else:
            return self.param

    def bp_regres(self, x, y, eta=0.01):
        """Run a single (x,y) pair with the backpropagation algorithm - Gradient Descent.
           Uses the derivative according each neuron's activation function.
           Modifies the weights of the neurons, calculates and returns updated MSE.
           eta -- learning rate."""
        x = np.array(x,dtype=object)
        y = np.array(y,dtype=object)
        self.eta=eta
        # STEP 1: Feed a sample to the network 
        outputs = self.run(x)
        # STEP 2: Calculate the MSE
        error = 2*(y - outputs) # A list of outputs
        MSE = sum( error ** 2) / self.layers[-1] 
        # ∂MSE/∂weight=∂MSE/∂output*∂output/∂weight
        # STEP 3: Calculate the OUTPUT error terms
        # ∂MSE/∂output -- depends on neuron's activation function
        for j in range (len(outputs)):
            self.d[-1][j] = self.deriv(outputs[j], len(self.network)-1) * error
        # STEP 4: Calculate the error term of EACH UNIT on each layer
        for i in reversed(range(1,len(self.network)-1)):
            for h in range(len(self.network[i])):
                fwd_error = 0.0
                for k in range(self.layers[i+1]): 
                    fwd_error += self.network[i+1][k].weights[h] * self.d[i+1][k] 
                self.d[i][h] = self.deriv(self.values[i][h], i, h) * fwd_error
        # STEPS 5 & 6: Calculate the deltas and update the weights
        for i in range(1,len(self.network)): # runs on layers
            for j in range(self.layers[i]): # runs on neurons
                for k in range(self.layers[i-1]+1): # runs on inputs. +1 for bias
                    # output=sum(weight*value)+bias*bias_weight
                    if k==self.layers[i-1]:
                        # ∂output/∂bias_weight=bias
                        delta = self.eta * self.d[i][j] * self.bias
                    else:
                        # ∂output/∂weight=value
                        delta = self.eta * self.d[i][j] * self.values[i-1][k] 
                    self.network[i][j].weights[k] += delta # applying the delta rule
        return MSE

class Regres:
    """Creates a multilayer neuron network.
       Used for regression. Fits the model by running the MultiLayer Neuron Network in a 
       loop for each row of X and calculating the error. Each running modifies the weights of the objects. 
       Attributes:
          layers:               A list with the number of neurons per layer. Including the input (first) and the output (last) layers.
          regres_network:       MultiLayerNeuron Class. self.regres_network.network[layer][neuron] -- Neuron Class (layer 0 is an input).
          epochs:               Number of iterations
          eta:                  Learning rate
          weight_history:       List of lists of weights propagation
          weight_history_table: Pandas table of weights propagation
          MSE_history:          List of MSEs propagation"""
      
    def __init__(self, layers, bias=1.0):
        """Return a new MLP object with the specified parameters.
           layers -- a list of layers. [0] is a number of the model's features.
           Activation function is linear by default.""" 
        self.layers = layers
        self.bias = bias
        self.regres_network = MultiLayerNeuron(layers=layers, bias=bias)

    def set_weights(self, w_init):
        """Set the weights. 
           Overrides the np.random.rand() weights and the bias weight.
           w_init -- a list of lists with the weights for all but the input layer. Incl. the bias. """
        self.regres_network.set_weights(w_init)

    def set_hidden_activ(self, activ, param=0):
        """Sets the activ function of the hidden layers.
           activ -- a string of 'linear' (default), 'relu', 'mrelu' (modified relu), 'sigmoid'.
           param -- parameter for mrelu."""
        self.regres_network.set_activ(activ, param=0)
        self.regres_network.set_output_activ('linear')

    def fit(self, X, y, epochs, eta=0.01):
        """Runs the MLNs epochs times. Each time the weights are being modified and the error is being calculated.
           MSEs and weights are stored.
           X,y -- an array and a list of data."""
        self.epochs=epochs
        self.eta=eta
        self.weight_history=[]
        self.weight_history_table=[]
        self.MSE_history=[]
        for i in range(self.epochs):
            weight_epoch=[]
            weight_epoch_table=[]
            MSE = 0.0
            for j in range (len(X)):
                MSE +=  self.regres_network.bp_regres(X[j],[y[j]], self.eta)
            MSE = MSE / len(X)
            self.MSE_history.append(MSE)
            for m in range(1,len(self.layers)):
                weight_layer=[]
                for n in range(self.layers[m]):
                    neuron_w=self.regres_network.network[m][n].weights
                    neuron_w_list=[x for x in neuron_w]
                    weight_layer.append(neuron_w_list)
                    weight_epoch_table+=neuron_w_list
                weight_epoch.append(weight_layer)
            self.weight_history.append(weight_epoch)
            self.weight_history_table.append(weight_epoch_table)
        self.weight_history_table=pd.DataFrame(data=self.weight_history_table, columns=self.get_cols())
        print ("""Model fitted.
self.weight_history - list of lists of weights propagation
self.weight_history_table - Pandas table of weights propagation
self.MSE_history - list of MSEs propagation""")

    def get_cols(self): 
        """Gets a list of names for weights. Used for pandas table of weights propagation as column names."""
        cols=[]
        for i in range(1,len(self.layers)):
            for h in range(self.layers[i]):
                for k in range(self.layers[i-1]+1): 
                    col="{}_{}_{}".format(i,h,k) 
                    cols.append(col)
        return cols 
    
    def printWeights(self):
        """Displays a summary of weights and activation functions per layer and neuron."""
        self.regres_network.printWeights()

    def run(self, x):
        """Calculates the output of a single row of X with the weights set"""
        return self.regres_network.run(x)

    def predict(self, x):
        """Returns the list of output. Runs every row of the data."""
        y=[]
        for i in range(len(x)):
            y.append(self.run(x[i])[0])
        return y

class VectorBackProp:
    """Creates a two layer neuron network: the hidden layer and the output layer.
       The output layer may be multiple.
       The activation functions of the layers may be set.

       X and T are numpy column vectors or set of column vectors as numpy matrices.
       If the data is pandas dataframe, it should be turned to numpy:
          X=np.array(DataFrame[[x0,x1,...]])
          T=np.array(DataFrame[[t0,...]])
      
       Attributes:
          layers: A list of layers. [2,3,1] -- 2 inputs, 3 neurons in hidden layer, 1 neuron in output layer
          hidden_activation: Activation function of the hidden layer. 'linear' (by default), 'sigmoid', 'prelu'.
          output_activation: Activation function of the output layer. 'linear' (by default) for regression, 'softmax' for classification.
          Wh, bh, Wo, bo: Matrices of weights.
          JWh, Jbh, JWo, Jbo: Matrices of weight Jacobian.
          Wh_history, bh_history, Wo_history, bo_history: 3D numpy arrays with histories of weights."""
      
    def __init__(self, layers, hidden_activation = 'linear', output_activation = 'linear'):
        """Return a new MLP object with the specified parameters.
           layers: A list of layers. [2,3,1] -- 2 inputs, 3 neurons in hidden layer, 1 neuron in output layer
           hidden_activation: Activation function of the hidden layer. 'linear' (by default), 'sigmoid', 'prelu'.
           output_activation: Activation function of the output layer. 'linear' (by default) for regression, 'softmax' for classification.""" 
        self.layers = layers
        self.hidden_activation = hidden_activation
        self.output_activation = output_activation

    def sigmoid(self, x):
        """Sigmoid activation function."""
        return 1. / (1. + np.exp(-x))

    def sigmoid_deriv(self, x):
        """Sigmoid derivative function."""
        return np.multiply(x,(1 - x))

    def PReLU(self, x):
        """Parametric ReLU activation function.
           Parameter = 0.001"""
        x[x<0] *= 0.001
        return x

    def PReLU_deriv(self, x):
        """Parametric ReLU derivative function:
           Matrix with ones for positives and 0.001s for negatives."""
        y=np.ones(x.shape)
        y[x<0]=0.001
        return y

    def softmax(self, x):
        """Softmax activation function"""
        return np.exp(x) / np.sum(np.exp(x), axis=1, keepdims=True)

    def hidden_activations(self, X):
        """Compute the hidden activations H.
           self.hidden_activation may be 'linear' (default), 'sigmoid' or 'prelu'."""
        if self.hidden_activation == 'sigmoid':
            return self.sigmoid((X @ self.Wh) + self.bh)
        if self.hidden_activation == 'prelu':
            return self.PReLU((X @ self.Wh) + self.bh)
        if self.hidden_activation == 'linear':
            return (X @ self.Wh) + self.bh
        return (X @ self.Wh) + self.bh # default

    def output_activations(self, H):
        """Compute the output Y.
           self.output_activation may be 'linear' (default) or 'softmax'."""
        if self.output_activation == 'softmax': # softmax for classification
            return self.softmax((H @ self.Wo) + self.bo)
        if self.output_activation == 'linear': #linear for regression
            return (H @ self.Wo) + self.bo
        return (H @ self.Wo) + self.bo # default
    
    def run(self, X):
        """Runs the input X vectors of input layer, returns the Y vectors of output layer."""
        return self.output_activations(self.hidden_activations(X))

    def nn_predict(self, X):
        """Neural network prediction function that only returns
        1 or 0 depending on the predicted class"""
        return np.around(self.run(X))

    def loss(self, Y, T):
        """Loss function.
           Regression: MSE (output_activation -- 'linear').
           Classification: cross-entropy (output_activation -- 'softmax')."""
        SE=(Y-T)**2 # MSE 
        abs_err=np.abs(Y-T) # ABS
        MSE=SE.sum()/Y.shape[0]
        if self.output_activation == 'linear':      
            return MSE
        if self.output_activation == 'softmax':
            return - (T * np.log(Y)).sum() # softmax layer with corresponding cross-entropy loss function
        return MSE # default

    def error_output(self, Y, T):
        """Error function at the output"""
        return Y - T # same for softmax and MSE

    def gradient_weight_out(self, H, Eo):
        """Gradients for the weight parameters at the output layer"""
        return  H.T @ Eo

    def gradient_bias_out(self, Eo):
        """Gradients for the bias parameters at the output layer"""
        return  np.sum(Eo, axis=0, keepdims=True)

    def error_hidden(self, H, Eo):
        """Error at the hidden layer.
        H * (1-H) * (E . Wo^T) for sigmoid
        [1 for pos, 0.001 for neg] * (E . Wo^T) for PReLU
        (E . Wo^T) for linear (default)."""
        if self.hidden_activation == 'sigmoid':
            return np.multiply(self.sigmoid_deriv(H), (Eo @ self.Wo.T))
        if self.hidden_activation == 'prelu':
            return np.multiply(self.PReLU_deriv(H), (Eo @ self.Wo.T))
        if self.hidden_activation == 'linear':
            return (Eo @ self.Wo.T)
        return (Eo @ self.Wo.T) # default

    def gradient_weight_hidden(self, X, Eh):
        """Gradient for the weight parameters at the hidden layer"""
        return X.T @ Eh

    def gradient_bias_hidden(self, Eh):
        """Gradient for the bias parameters at the output layer"""
        return  np.sum(Eh, axis=0, keepdims=True)  

    def generate_weights(self, init_var=0.1):
        # Initialize hidden layer parameters
        bh = np.random.randn(1, self.layers[1]) * init_var
        Wh = np.random.randn(self.layers[0], self.layers[1]) * init_var
        # Initialize output layer parameters
        bo = np.random.randn(1, self.layers[2]) * init_var
        Wo = np.random.randn(self.layers[1], self.layers[2]) * init_var
        return Wh, bh, Wo, bo
 
    def get_gradients(self, X, T):
        """Update the network parameters over 1 iteration."""
        # Compute the output of the network
        # Compute the activations of the layers
        H = self.hidden_activations(X)
        Y = self.output_activations(H)
        # Compute the gradients of the output layer
        Eo = self.error_output(Y, T)
        self.JWo = self.gradient_weight_out(H, Eo)
        self.Jbo = self.gradient_bias_out(Eo)
        # Compute the gradients of the hidden layer
        Eh = self.error_hidden(H, Eo)
        self.JWh = self.gradient_weight_hidden(X, Eh)
        self.Jbh = self.gradient_bias_hidden(Eh)

    def update_momentum(self, X, T, Ms, lr_decay, momentum_term):
        """Update the momentum term."""
        # list_of_weights = [Wh, bh, Wo, bo]
        self.get_gradients(X, T)
        Js = [self.JWh, self.Jbh, self.JWo, self.Jbo]
        return [momentum_term * M - lr_decay * J 
                for M,J in zip(Ms, Js)]

    def update_weights(self, Ms):
        """Update the weights."""
        Ws = [self.Wh, self.bh, self.Wo, self.bo]
        # Ms = [MWh, Mbh, MWo, Mbo]
        return [P + M for P,M in zip(Ws, Ms)]

    def fit(self, X, T, epochs, learning_rate = 0.01, learning_rate_decay = 0, momentum_term = 0.9, init_var=0.1, repeat=False):
        """Run backpropagation:
              1. Initilizes weights matrices (if repeat is False)
              2. Creates list of losses and calculates initial loss by rinning self.loss()
              3. Creates lists of weight matrices and puts initial matrices
              4. Starts epoch iterations for weights and loss update
                a. Calculates learning rate decay:
                   lr_decay = learning_rate / (1 + learning_rate_decay * epoch)
                   learning_rate_decay = 0 in case of constant learning rate
                b. Runs update_momentum() function, which calls get_gradients() function.
                   get_gradients() calculates H, Y, Eo, Eh and returns weights' Jacobians: self.JWh, self.Jbh, self.JWo, self.Jbo
                   update_momentum() returns list of momentums and replaces the previous ones
                c. Runs update_weights() which returns new weight matrices and replaces the previous ones
                d. Calculates loss and addes to the list of losses
                e. New weight matrices are added to their lists
              5. Lists of weight matrices are turned to .self numpy arrays for better slicing option 

           X and T are numpy column vectors or set of column vectors as numpy matrices.
           If the data is pandas dataframe, it should be turned to numpy:
              X=np.array(DataFrame[[x0,x1,...]])
              T=np.array(DataFrame[[t0,...]])
           epochs: int number of epochs
           learning_rate: learning rate, 0.01 by default
           learning_rate_decay: learning rate decay, 0 by default, integer or float
           momentum_term: momentum term, 0.9 by default, 0 for simple gradiend descent
           init_var: initial variance of generated weights, multiplies np.random.randn(), 0.1 by default
           repeat: False -- new weights are generated, 
                   True -- old weights are used from previous fit() or import_weights()

           The results are:
           self.loss_list -- list of floats
           self.Wh_history -- 3D numpy array of weights [epochs, starting neuron, target neuron]
           self.bh_history
           self.Wo_history
           self.bo_history

           self.JWh_history -- 3D numpy array of weights' Jacobians 
           self.Jbh_history
           self.JWo_history
           self.Jbo_history           
           """        
        # Run backpropagation
        # Initialize weights and biases
        if repeat:
            self.Wh, self.bh, self.Wo, self.bo = self.Wh, self.bh, self.Wo, self.bo
        else:
            self.Wh, self.bh, self.Wo, self.bo = self.generate_weights(init_var)
        # Moments Ms = [MWh, Mbh, MWo, Mbo]
        Ms = [np.zeros_like(M) for M in [self.Wh, self.bh, self.Wo, self.bo]]
        # Start the gradient descent updates
        # list of loss over the iterations
        self.loss_list = [self.loss(self.run(X), T)]
        Wh_hist, bh_hist, Wo_hist, bo_hist = [self.Wh], [self.bh], [self.Wo], [self.bo]
        JWh_hist, Jbh_hist, JWo_hist, Jbo_hist = [],[],[],[]
        for i in range(epochs):
            # learning rate decay
            lr_decay = learning_rate / (1 + learning_rate_decay * 1.0 * i)
            # Update the moments and the parameters
            Ms = self.update_momentum(X, T, Ms, lr_decay, momentum_term)
            self.Wh, self.bh, self.Wo, self.bo = self.update_weights(Ms)
            self.loss_list.append(self.loss(self.run(X), T))
            Wh_hist.append(self.Wh)
            bh_hist.append(self.bh)
            Wo_hist.append(self.Wo)
            bo_hist.append(self.bo)

            JWh_hist.append(self.JWh)
            Jbh_hist.append(self.Jbh)
            JWo_hist.append(self.JWo)
            Jbo_hist.append(self.Jbo)

        self.Wh_history=np.array(Wh_hist)
        self.bh_history=np.array(bh_hist)
        self.Wo_history=np.array(Wo_hist)
        self.bo_history=np.array(bo_hist)

        self.JWh_history=np.array(JWh_hist)
        self.Jbh_history=np.array(Jbh_hist)
        self.JWo_history=np.array(JWo_hist)
        self.Jbo_history=np.array(Jbo_hist)

    def export_weights(self):
        """
        return [self.Wh.tolist(), self.bh.tolist(), self.Wo.tolist(), self.bo.tolist()]
        Arranges weights without word "array", in a way that makes possible copy/paste and import as self.import_weights().
        """
        return [self.Wh.tolist(), self.bh.tolist(), self.Wo.tolist(), self.bo.tolist()]

    def export_weights_as_numpy(self):
        """
        return [self.Wh, self.bh, self.Wo, self.bo]"""
        return [self.Wh, self.bh, self.Wo, self.bo]

    def print_weights(self):
        """
        Prints the layers and weights.
        """
        print ('Layers (input, hidden, output): ', self.layers, self.hidden_activation, self.output_activation)
        print ('Hidden layer weights: ', self.Wh.tolist())
        print ('Hidden layer biases: ', self.bh.tolist())
        print ('Outlet layer weights: ', self.Wo.tolist())
        print ('Outlet layer biases: ', self.bo.tolist())

    def import_weights(self, weights):
        """
        Puts values to Wh, bh, Wo and bo from the list of lists as it is from self.export_weights().
        """
        self.Wh, self.bh, self.Wo, self.bo = np.array(weights[0]), np.array(weights[1]), np.array(weights[2]), np.array(weights[3])
