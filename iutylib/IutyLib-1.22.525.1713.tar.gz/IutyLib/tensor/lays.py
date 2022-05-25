import tensorflow as tf

def getConv(name,ahead,channels):
    rtn = None
    dim = ahead.get_shape()[-1].value
    with tf.variable_scope(name) as scope:
        weights = tf.Variable(tf.truncated_normal(shape=[3, 3, dim, channels], stddev=1.0, dtype=tf.float32),name='weights', dtype=tf.float32)

        biases = tf.Variable(tf.constant(value=0.1, dtype=tf.float32, shape=[channels]),name='biases', dtype=tf.float32)

        conv = tf.nn.conv2d(ahead, weights, strides=[1, 1, 1, 1], padding='SAME')
        pre_activation = tf.nn.bias_add(conv, biases)
        conv1 = tf.nn.relu(pre_activation, name=scope.name)
        rtn = conv1
    return rtn

def getPool(name,ahead,output):
    rtn = None
    with tf.variable_scope(name) as scope:
        pool1 = tf.nn.max_pool(ahead, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1], padding='SAME', name='pooling1')
        norm1 = tf.nn.lrn(pool1, depth_radius=4, bias=1.0, alpha=0.001 / 9.0, beta=0.75, name=scope.name)
        rtn = norm1
    return rtn

def getLocal(name,ahead,output):
    rtn = None
    with tf.variable_scope(name) as scope:
        batch_size = ahead.get_shape()[0].value
        reshape = tf.reshape(ahead, shape=[batch_size, -1])
        dim = reshape.get_shape()[-1].value
        
        weights = tf.Variable(tf.truncated_normal(shape=[dim, output], stddev=0.005, dtype=tf.float32),name='weights', dtype=tf.float32)

        biases = tf.Variable(tf.constant(value=0.1, dtype=tf.float32, shape=[output]),name='biases', dtype=tf.float32)
        local = tf.nn.relu(tf.matmul(reshape, weights) + biases, name=scope.name)
        rtn = local
    return rtn

def getLinear(name,ahead,output):
    rtn = None
    with tf.variable_scope(name) as scope:
        dim = ahead.get_shape()[-1].value
        weights = tf.Variable(tf.truncated_normal(shape=[dim, output], stddev=0.005, dtype=tf.float32),name='softmax_linear', dtype=tf.float32)

        biases = tf.Variable(tf.constant(value=0.1, dtype=tf.float32, shape=[output]),name='biases', dtype=tf.float32)

        softmax_linear = tf.add(tf.matmul(ahead, weights), biases, name=scope.name)
        rtn = softmax_linear
    return rtn

