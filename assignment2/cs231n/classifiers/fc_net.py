from builtins import range
from builtins import object
import numpy as np

from cs231n.layers import *
from cs231n.layer_utils import *


class TwoLayerNet(object):
    """
    A two-layer fully-connected neural network with ReLU nonlinearity and
    softmax loss that uses a modular layer design. We assume an input dimension
    of D, a hidden dimension of H, and perform classification over C classes.

    The architecure should be affine - relu - affine - softmax.

    Note that this class does not implement gradient descent; instead, it
    will interact with a separate Solver object that is responsible for running
    optimization.

    The learnable parameters of the model are stored in the dictionary
    self.params that maps parameter names to numpy arrays.
    """

    def __init__(self, input_dim=3*32*32, hidden_dim=100, num_classes=10,
                 weight_scale=1e-3, reg=0.0):
        """
        Initialize a new network.

        Inputs:
        - input_dim: An integer giving the size of the input
        - hidden_dim: An integer giving the size of the hidden layer
        - num_classes: An integer giving the number of classes to classify
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - reg: Scalar giving L2 regularization strength.
        """
        self.params = {}
        self.reg = reg

        ############################################################################
        # TODO: Initialize the weights and biases of the two-layer net. Weights    #
        # should be initialized from a Gaussian centered at 0.0 with               #
        # standard deviation equal to weight_scale, and biases should be           #
        # initialized to zero. All weights and biases should be stored in the      #
        # dictionary self.params, with first layer weights                         #
        # and biases using the keys 'W1' and 'b1' and second layer                 #
        # weights and biases using the keys 'W2' and 'b2'.                         #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

        self.params['W1'] = weight_scale * np.random.randn(input_dim,hidden_dim)
        self.params['b1'] = np.zeros((1,hidden_dim))
        self.params['W2'] = weight_scale * np.random.randn(hidden_dim,num_classes)
        self.params['b2'] = np.zeros((1,num_classes))

        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################


    def loss(self, X, y=None):
        """
        Compute loss and gradient for a minibatch of data.

        Inputs:
        - X: Array of input data of shape (N, d_1, ..., d_k)
        - y: Array of labels, of shape (N,). y[i] gives the label for X[i].

        Returns:
        If y is None, then run a test-time forward pass of the model and return:
        - scores: Array of shape (N, C) giving classification scores, where
          scores[i, c] is the classification score for X[i] and class c.

        If y is not None, then run a training-time forward and backward pass and
        return a tuple of:
        - loss: Scalar value giving the loss
        - grads: Dictionary with the same keys as self.params, mapping parameter
          names to gradients of the loss with respect to those parameters.
        """
        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the two-layer net, computing the    #
        # class scores for X and storing them in the scores variable.              #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

        out1, cache1 = affine_relu_forward(X, self.params['W1'], self.params['b1'])
        out2, cache2 = affine_forward(out1, self.params['W2'], self.params['b2'])
        scores = out2

        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If y is None then we are in test mode so just return scores
        if y is None:
            return scores

        loss, grads = 0, {}
        ############################################################################
        # TODO: Implement the backward pass for the two-layer net. Store the loss  #
        # in the loss variable and gradients in the grads dictionary. Compute data #
        # loss using softmax, and make sure that grads[k] holds the gradients for  #
        # self.params[k]. Don't forget to add L2 regularization!                   #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

        data_loss, dscores = softmax_loss(scores, y)
        
        dout2, dW2, db2 = affine_backward(dscores, cache2)
        dout1, dW1, db1 = affine_relu_backward(dout2, cache1)
        
        
        W1 = self.params['W1']
        W2 = self.params['W2']
        
        reg_loss = 0.5*self.reg*np.sum(W1*W1) + 0.5*self.reg*np.sum(W2*W2)
        loss = data_loss + reg_loss
        
        
        dW2 += self.reg * W2
        dW1 += self.reg * W1

        # grads
        grads['W1'] = dW1
        grads['b1'] = db1
        grads['W2'] = dW2
        grads['b2'] = db2

        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads


class FullyConnectedNet(object):
    """
    A fully-connected neural network with an arbitrary number of hidden layers,
    ReLU nonlinearities, and a softmax loss function. This will also implement
    dropout and batch/layer normalization as options. For a network with L layers,
    the architecture will be

    {affine - [batch/layer norm] - relu - [dropout]} x (L - 1) - affine - softmax

    where batch/layer normalization and dropout are optional, and the {...} block is
    repeated L - 1 times.

    Similar to the TwoLayerNet above, learnable parameters are stored in the
    self.params dictionary and will be learned using the Solver class.
    """

    def __init__(self, hidden_dims, input_dim=3*32*32, num_classes=10,
                 dropout=1, normalization=None, reg=0.0,
                 weight_scale=1e-2, dtype=np.float32, seed=None):
        """
        Initialize a new FullyConnectedNet.

        Inputs:
        - hidden_dims: A list of integers giving the size of each hidden layer.
        - input_dim: An integer giving the size of the input.
        - num_classes: An integer giving the number of classes to classify.
        - dropout: Scalar between 0 and 1 giving dropout strength. If dropout=1 then
          the network should not use dropout at all.
        - normalization: What type of normalization the network should use. Valid values
          are "batchnorm", "layernorm", or None for no normalization (the default).
        - reg: Scalar giving L2 regularization strength.
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - dtype: A numpy datatype object; all computations will be performed using
          this datatype. float32 is faster but less accurate, so you should use
          float64 for numeric gradient checking.
        - seed: If not None, then pass this random seed to the dropout layers. This
          will make the dropout layers deteriminstic so we can gradient check the
          model.
        """
        self.normalization = normalization
        self.use_dropout = dropout != 1
        self.reg = reg
        self.num_layers = 1 + len(hidden_dims)
        self.dtype = dtype
        self.params = {}

        ############################################################################
        # TODO: Initialize the parameters of the network, storing all values in    #
        # the self.params dictionary. Store weights and biases for the first layer #
        # in W1 and b1; for the second layer use W2 and b2, etc. Weights should be #
        # initialized from a normal distribution centered at 0 with standard       #
        # deviation equal to weight_scale. Biases should be initialized to zero.   #
        #                                                                          #
        # When using batch normalization, store scale and shift parameters for the #
        # first layer in gamma1 and beta1; for the second layer use gamma2 and     #
        # beta2, etc. Scale parameters should be initialized to ones and shift     #
        # parameters should be initialized to zeros.                               #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        
        # {affine - [batch/layer norm] - relu - [dropout]} x (L - 1) - affine - softmax
        
        #hidden_dims.append(num_classes)
        in_dim = input_dim
        index = 0
        for hidden_dim in hidden_dims:
            
            out_dim = hidden_dim
            index += 1
            
#             if index == 6:
#                 print('--------------6------------')
#                 print(hidden_dims)
            
            self.params['W%s' % index] = weight_scale * np.random.randn(in_dim,out_dim)
            self.params['b%s' % index] = np.zeros((1,out_dim))
            if self.normalization == 'batchnorm' or self.normalization == 'layernorm':
                self.params['gamma%s' % index] = np.ones((1,out_dim))
                self.params['beta%s' % index] = np.zeros((1,out_dim))
            
            in_dim = out_dim
        # Last layer
        index += 1
        self.params['W%s' % index] = weight_scale * np.random.randn(in_dim,num_classes)
        self.params['b%s' % index] = np.zeros((1,num_classes))
        # print(hidden_dims)
        # print(self.params)

        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # When using dropout we need to pass a dropout_param dictionary to each
        # dropout layer so that the layer knows the dropout probability and the mode
        # (train / test). You can pass the same dropout_param to each dropout layer.
        self.dropout_param = {}
        if self.use_dropout:
            self.dropout_param = {'mode': 'train', 'p': dropout}
            if seed is not None:
                self.dropout_param['seed'] = seed

        # With batch normalization we need to keep track of running means and
        # variances, so we need to pass a special bn_param object to each batch
        # normalization layer. You should pass self.bn_params[0] to the forward pass
        # of the first batch normalization layer, self.bn_params[1] to the forward
        # pass of the second batch normalization layer, etc.
        self.bn_params = []
        if self.normalization=='batchnorm':
            self.bn_params = [{'mode': 'train'} for i in range(self.num_layers - 1)]
        if self.normalization=='layernorm':
            self.bn_params = [{} for i in range(self.num_layers - 1)]

        # Cast all parameters to the correct datatype
        for k, v in self.params.items():
            self.params[k] = v.astype(dtype)
        
        #for key, value in self.params.items():
        #    print('%s: %s' % (key, value.shape))


    def loss(self, X, y=None):
        """
        Compute loss and gradient for the fully-connected net.

        Input / output: Same as TwoLayerNet above.
        
        Inputs:
        - X: Array of input data of shape (N, d_1, ..., d_k)
        - y: Array of labels, of shape (N,). y[i] gives the label for X[i].

        Returns:
        If y is None, then run a test-time forward pass of the model and return:
        - scores: Array of shape (N, C) giving classification scores, where
          scores[i, c] is the classification score for X[i] and class c.

        If y is not None, then run a training-time forward and backward pass and
        return a tuple of:
        - loss: Scalar value giving the loss
        - grads: Dictionary with the same keys as self.params, mapping parameter
          names to gradients of the loss with respect to those parameters.
        """
        X = X.astype(self.dtype)
        mode = 'test' if y is None else 'train'

        # Set train/test mode for batchnorm params and dropout param since they
        # behave differently during training and testing.
        if self.use_dropout:
            self.dropout_param['mode'] = mode
        if self.normalization=='batchnorm':
            for bn_param in self.bn_params:
                bn_param['mode'] = mode
        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the fully-connected net, computing  #
        # the class scores for X and storing them in the scores variable.          #
        #                                                                          #
        # When using dropout, you'll need to pass self.dropout_param to each       #
        # dropout forward pass.                                                    #
        #                                                                          #
        # When using batch normalization, you'll need to pass self.bn_params[0] to #
        # the forward pass for the first batch normalization layer, pass           #
        # self.bn_params[1] to the forward pass for the second batch normalization #
        # layer, etc.                                                              #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        
        # self.normalization = normalization
        # self.use_dropout = dropout != 1
        # self.reg = reg
        # self.num_layers = 1 + len(hidden_dims)
        # self.dtype = dtype
        # self.params = {}
        # self.dropout_param = {'mode': 'train', 'p': dropout}
        # self.bn_params = [{'mode': 'train'} for i in range(self.num_layers - 1)]

        # {affine - [batch/layer norm] - relu - [dropout]} x (L - 1) - affine - softmax

        # out, cache = affine_forward(x, w, b) 
        # out, cache = batchnorm_forward(x, gamma, beta, bn_param) 
        # out, cache = relu_forward(x) 
        # out, cache = dropout_forward(x, dropout_param) 
        # loss, dx = softmax_loss(x, y) 

        outs_and_caches = []
        input_matrix = X
        for i in range(self.num_layers - 1):
            index = i + 1
            
            #affine
            out, cache = affine_forward(input_matrix, self.params['W%s' % index], self.params['b%s' % index])
            outs_and_caches.append(('affine', index, cache))
            
            # batch
            if self.normalization == 'batchnorm':
                out, cache = batchnorm_forward(out,self.params['gamma%s' % index],self.params['beta%s' % index], 
                                               self.bn_params[i])
                outs_and_caches.append(('batch', index, cache))
            
            # layernorm
            if self.normalization == 'layernorm':
                out, cache = layernorm_forward(out,self.params['gamma%s' % index],self.params['beta%s' % index], 
                                               self.bn_params[i])
                outs_and_caches.append(('layernorm', index, cache))
                
            #relu
            out, cache = relu_forward(out)
            outs_and_caches.append(('relu', index, cache))
            
            #dropout
            if self.use_dropout:
                out, cache = dropout_forward(out, self.dropout_param)
                outs_and_caches.append(('dropout', index, cache))
                
            input_matrix = out
            
        index = self.num_layers 
        out, cache = affine_forward(input_matrix, self.params['W%s' % index], self.params['b%s' % index])
        outs_and_caches.append(('affine',index, cache))
        scores = out
        
        

        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If test mode return early
        if mode == 'test':
            return scores

        loss, grads = 0.0, {}
        ############################################################################
        # TODO: Implement the backward pass for the fully-connected net. Store the #
        # loss in the loss variable and gradients in the grads dictionary. Compute #
        # data loss using softmax, and make sure that grads[k] holds the gradients #
        # for self.params[k]. Don't forget to add L2 regularization!               #
        #                                                                          #
        # When using batch/layer normalization, you don't need to regularize the scale   #
        # and shift parameters.                                                    #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

    
        data_loss, dout = softmax_loss(scores, y)
        reg_loss = 0.0
        for i in range(self.num_layers):
            index = i + 1
            reg_loss += 0.5*self.reg*np.sum(self.params['W%s' % index]*self.params['W%s' % index])
        
        loss = data_loss + reg_loss
        
        # {affine - [batch/layer norm] - relu - [dropout]} x (L - 1) - affine - softmax
        # dx, dw, db = affine_backward(dout, cache)
        # dx = relu_backward(dout, cache)
        # dx, dgamma, dbeta = batchnorm_backward(dout, cache)
        # dx = dropout_backward(dout, cache)
        
        # self.params['W%s' % index]
        # self.params['b%s' % index]
        # self.params['gamma%s' % index]
        # self.params['beta%s' % index]
        
        for i in reversed(range(len(outs_and_caches))):
            layer, index, cache = outs_and_caches[i]
            if layer == 'affine':
                dx, dw, db = affine_backward(dout, cache)
                dw += self.reg * self.params['W%s' % index] # add regularization gradient contribution
                grads['W%s' % index] = dw 
                grads['b%s' % index] = db
                dout = dx
            if layer == 'batch':
                dx, dgamma, dbeta = batchnorm_backward(dout, cache)
                grads['gamma%s' % index] = dgamma
                grads['beta%s' % index] = dbeta
                dout = dx
            if layer == 'layernorm':
                dx, dgamma, dbeta = layernorm_backward(dout, cache)
                grads['gamma%s' % index] = dgamma
                grads['beta%s' % index] = dbeta
                dout = dx
            if layer == 'relu':
                dx = relu_backward(dout, cache)
                dout = dx
            if layer == 'dropout':
                dx = dropout_backward(dout, cache)
                dout = dx
                

        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads
