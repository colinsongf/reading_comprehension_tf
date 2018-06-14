import numpy as np
import tensorflow as tf

from util.default_util import *
from util.reading_comprehension_util import *

__all__ = ["Attention", "MaxAttention", "HeadAttention"]

def _create_attention_matrix(src_unit_dim,
                             trg_unit_dim,
                             attention_unit_dim,
                             attention_score_type,
                             trainable):
    """create attetnion matrix"""
    if attention_score_type == "dot":
        attention_matrix = []
    elif attention_score_type == "scaled_dot":
        attention_matrix = []
    elif attention_score_type == "linear":
        attention_matrix = _create_linear_attention_matrix(src_unit_dim, trg_unit_dim, trainable)
    elif attention_score_type == "bilinear":
        attention_matrix = _create_bilinear_attention_matrix(src_unit_dim, trg_unit_dim, trainable)
    elif attention_score_type == "nonlinear":
        attention_matrix = _create_nonlinear_attention_matrix(src_unit_dim, trg_unit_dim, attention_unit_dim, trainable)
    elif attention_score_type == "linear_plus":
        attention_matrix = _create_linear_plus_attention_matrix(src_unit_dim, trg_unit_dim, trainable)
    elif attention_score_type == "nonlinear_plus":
        attention_matrix = _create_nonlinear_plus_attention_matrix(src_unit_dim, trg_unit_dim, attention_unit_dim, trainable)
    else:
        raise ValueError("unsupported attention score type {0}".format(attention_score_type))
    
    return attention_matrix

def _create_linear_attention_matrix(src_unit_dim,
                                    trg_unit_dim,
                                    trainable):
    """create linear attetnion matrix"""
    weight_initializer = create_variable_initializer("glorot_uniform")
    
    linear_src_weight = tf.get_variable("linear_src_weight", shape=[1, src_unit_dim],
        initializer=weight_initializer, trainable=trainable, dtype=tf.float32)
    linear_trg_weight = tf.get_variable("linear_trg_weight", shape=[1, trg_unit_dim],
        initializer=weight_initializer, trainable=trainable, dtype=tf.float32)
    attention_matrix = [linear_src_weight, linear_trg_weight]
    
    return attention_matrix

def _create_bilinear_attention_matrix(src_unit_dim,
                                      trg_unit_dim,
                                      trainable):
    """create bilinear attetnion matrix"""
    weight_initializer = create_variable_initializer("glorot_uniform")
    
    bilinear_weight = tf.get_variable("bilinear_weight", shape=[src_unit_dim, trg_unit_dim],
        initializer=weight_initializer, trainable=trainable, dtype=tf.float32)
    attention_matrix = [bilinear_weight]
    
    return attention_matrix

def _create_nonlinear_attention_matrix(src_unit_dim,
                                       trg_unit_dim,
                                       attention_unit_dim,
                                       trainable):
    """create nonlinear attetnion matrix"""
    weight_initializer = create_variable_initializer("glorot_uniform")
    bias_initializer = create_variable_initializer("glorot_uniform")
    
    pre_nonlinear_src_weight = tf.get_variable("pre_nonlinear_src_weight", shape=[attention_unit_dim, src_unit_dim],
        initializer=weight_initializer, trainable=trainable, dtype=tf.float32)
    pre_nonlinear_trg_weight = tf.get_variable("pre_nonlinear_trg_weight", shape=[attention_unit_dim, trg_unit_dim],
        initializer=weight_initializer, trainable=trainable, dtype=tf.float32)
    pre_nonlinear_bias = tf.get_variable("pre_nonlinear_bias", shape=[attention_unit_dim],
        initializer=bias_initializer, trainable=trainable, dtype=tf.float32)
    post_nonlinear_weight = tf.get_variable("post_nonlinear_weight", shape=[1, attention_unit_dim],
        initializer=weight_initializer, trainable=trainable, dtype=tf.float32)
    attention_matrix = [pre_nonlinear_src_weight, pre_nonlinear_trg_weight,
        pre_nonlinear_bias, post_nonlinear_weight]
    
    return attention_matrix

def _create_linear_plus_attention_matrix(src_unit_dim,
                                         trg_unit_dim,
                                         trainable):
    """create linear plus attetnion matrix"""
    weight_initializer = create_variable_initializer("glorot_uniform")
    
    if src_unit_dim != trg_unit_dim:
        raise ValueError("src dim {0} and trg dim must be the same for linear plus attention".format(src_unit_dim, trg_unit_dim))
    else:
        mul_unit_dim = src_unit_dim
    
    linear_plus_src_weight = tf.get_variable("linear_plus_src_weight", shape=[1, src_unit_dim],
        initializer=weight_initializer, trainable=trainable, dtype=tf.float32)
    linear_plus_trg_weight = tf.get_variable("linear_plus_trg_weight", shape=[1, trg_unit_dim],
        initializer=weight_initializer, trainable=trainable, dtype=tf.float32)
    linear_plus_mul_weight = tf.get_variable("linear_plus_mul_weight", shape=[1, mul_unit_dim],
        initializer=weight_initializer, trainable=trainable, dtype=tf.float32)
    attention_matrix = [linear_plus_src_weight, linear_plus_trg_weight, linear_plus_mul_weight]
    
    return attention_matrix

def _create_nonlinear_plus_attention_matrix(src_unit_dim,
                                            trg_unit_dim,
                                            attention_unit_dim,
                                            trainable):
    """create nonlinear plus attetnion matrix"""
    weight_initializer = create_variable_initializer("glorot_uniform")
    bias_initializer = create_variable_initializer("glorot_uniform")
    
    if src_unit_dim != trg_unit_dim:
        raise ValueError("src dim {0} and trg dim must be the same for nonlinear plus attention".format(src_unit_dim, trg_unit_dim))
    else:
        mul_unit_dim = src_unit_dim
    
    pre_nonlinear_plus_src_weight = tf.get_variable("pre_nonlinear_plus_src_weight", shape=[attention_unit_dim, src_unit_dim],
        initializer=weight_initializer, trainable=trainable, dtype=tf.float32)
    pre_nonlinear_plus_trg_weight = tf.get_variable("pre_nonlinear_plus_trg_weight", shape=[attention_unit_dim, trg_unit_dim],
        initializer=weight_initializer, trainable=trainable, dtype=tf.float32)
    pre_nonlinear_plus_mul_weight = tf.get_variable("pre_nonlinear_plus_mul_weight", shape=[attention_unit_dim, mul_unit_dim],
        initializer=weight_initializer, trainable=trainable, dtype=tf.float32)
    pre_nonlinear_plus_bias = tf.get_variable("pre_nonlinear_plus_bias", shape=[attention_unit_dim],
        initializer=bias_initializer, trainable=trainable, dtype=tf.float32)
    post_nonlinear_plus_weight = tf.get_variable("post_nonlinear_plus_weight", shape=[1, attention_unit_dim],
        initializer=weight_initializer, trainable=trainable, dtype=tf.float32)
    attention_matrix = [pre_nonlinear_plus_src_weight, pre_nonlinear_plus_trg_weight,
        pre_nonlinear_plus_mul_weight, pre_nonlinear_plus_bias, post_nonlinear_plus_weight]
    
    return attention_matrix

def _create_projection_matrix(input_unit_dim,
                              projection_unit_dim,
                              trainable):
    """create projection matrix"""
    weight_initializer = create_variable_initializer("glorot_uniform")
    projection_weight = tf.get_variable("projection_weight", shape=[input_unit_dim, projection_unit_dim],
        initializer=weight_initializer, trainable=trainable, dtype=tf.float32)
    
    return projection_weight

def _generate_attention_score(input_src_data,
                              input_trg_data,
                              attention_matrix,
                              attention_score_type):
    """generate attention score"""
    if attention_score_type == "dot":
        input_attention_score = _generate_dot_attention_score(input_src_data, input_trg_data)
    elif attention_score_type == "scaled_dot":
        input_attention_score = _generate_scaled_dot_attention_score(input_src_data, input_trg_data)
    elif attention_score_type == "linear":
        input_attention_score = _generate_linear_attention_score(input_src_data,
            input_trg_data, attention_matrix)
    elif attention_score_type == "bilinear":
        input_attention_score = _generate_bilinear_attention_score(input_src_data,
            input_trg_data, attention_matrix)
    elif attention_score_type == "nonlinear":
        input_attention_score = _generate_nonlinear_attention_score(input_src_data,
            input_trg_data, attention_matrix)
    elif attention_score_type == "linear_plus":
        input_attention_score = _generate_linear_plus_attention_score(input_src_data,
            input_trg_data, attention_matrix)
    elif attention_score_type == "nonlinear_plus":
        input_attention_score = _generate_nonlinear_plus_attention_score(input_src_data,
            input_trg_data, attention_matrix)
    else:
        raise ValueError("unsupported attention score type {0}".format(attention_score_type))
    
    return input_attention_score

def _generate_dot_attention_score(input_src_data,
                                  input_trg_data):
    """generate dot-product attention score"""
    input_src_shape = tf.shape(input_src_data)
    input_trg_shape = tf.shape(input_trg_data)
    batch_size = input_src_shape[0]
    src_max_length = input_src_shape[1]
    src_unit_dim = input_src_shape[2]
    input_trg_data = tf.transpose(input_trg_data, perm=[0, 2, 1])
    input_attention = tf.matmul(input_src_data, input_trg_data)
    
    return input_attention

def _generate_scaled_dot_attention_score(input_src_data,
                                         input_trg_data):
    """generate scaled dot-product attention score"""
    input_src_shape = tf.shape(input_src_data)
    input_trg_shape = tf.shape(input_trg_data)
    batch_size = input_src_shape[0]
    src_max_length = input_src_shape[1]
    src_unit_dim = input_src_shape[2]
    input_trg_data = tf.transpose(input_trg_data, perm=[0, 2, 1])
    input_attention = tf.matmul(input_src_data, input_trg_data)
    input_attention = input_attention / tf.sqrt(tf.cast(src_unit_dim, dtype=tf.float32))
    
    return input_attention

def _generate_linear_attention_score(input_src_data,
                                     input_trg_data,
                                     attention_matrix):
    """generate linear attention score"""
    input_src_shape = tf.shape(input_src_data)
    input_trg_shape = tf.shape(input_trg_data)
    batch_size = input_src_shape[0]
    src_max_length = input_src_shape[1]
    trg_max_length = input_trg_shape[1]
    src_unit_dim = input_src_shape[2]
    trg_unit_dim = input_trg_shape[2]
    linear_src_weight = tf.transpose(attention_matrix[0], perm=[1, 0])
    linear_trg_weight = tf.transpose(attention_matrix[1], perm=[1, 0])
    input_src_data = tf.reshape(input_src_data, shape=[-1, src_unit_dim])
    input_src_data = tf.matmul(input_src_data, linear_src_weight)
    input_src_data = tf.reshape(input_src_data, shape=[batch_size, src_max_length, 1, -1])
    input_trg_data = tf.reshape(input_trg_data, shape=[-1, trg_unit_dim])
    input_trg_data = tf.matmul(input_trg_data, linear_trg_weight)
    input_trg_data = tf.reshape(input_trg_data, shape=[batch_size, 1, trg_max_length, -1])
    input_src_data = tf.tile(input_src_data, multiples=[1, 1, trg_max_length, 1])
    input_trg_data = tf.tile(input_trg_data, multiples=[1, src_max_length, 1, 1])
    input_attention = input_src_data + input_trg_data
    input_attention = tf.reshape(input_attention, shape=[batch_size, src_max_length, trg_max_length])
    
    return input_attention

def _generate_bilinear_attention_score(input_src_data,
                                       input_trg_data,
                                       attention_matrix):
    """generate bilinear attention score"""
    input_src_shape = tf.shape(input_src_data)
    input_trg_shape = tf.shape(input_trg_data)
    batch_size = input_src_shape[0]
    src_max_length = input_src_shape[1]
    src_unit_dim = input_src_shape[2]
    bilinear_weight = attention_matrix[0]
    input_src_data = tf.reshape(input_src_data, shape=[-1, src_unit_dim])
    input_src_data = tf.matmul(input_src_data, bilinear_weight)
    input_src_data = tf.reshape(input_src_data, shape=[batch_size, src_max_length, -1])
    input_trg_data = tf.transpose(input_trg_data, perm=[0, 2, 1])
    input_attention = tf.matmul(input_src_data, input_trg_data)
    
    return input_attention

def _generate_nonlinear_attention_score(input_src_data,
                                        input_trg_data,
                                        attention_matrix):
    """generate linear attention score"""
    input_src_shape = tf.shape(input_src_data)
    input_trg_shape = tf.shape(input_trg_data)
    batch_size = input_src_shape[0]
    src_max_length = input_src_shape[1]
    trg_max_length = input_trg_shape[1]
    src_unit_dim = input_src_shape[2]
    trg_unit_dim = input_trg_shape[2]
    pre_nonlinear_src_weight = tf.transpose(attention_matrix[0], perm=[1, 0])
    pre_nonlinear_trg_weight = tf.transpose(attention_matrix[1], perm=[1, 0])
    pre_nonlinear_bias = tf.reshape(attention_matrix[2], shape=[1, 1, 1, -1])
    post_nonlinear_weight = tf.transpose(attention_matrix[3], perm=[1, 0])
    input_src_data = tf.reshape(input_src_data, shape=[-1, src_unit_dim])
    input_src_data = tf.matmul(input_src_data, pre_nonlinear_src_weight)
    input_src_data = tf.reshape(input_src_data, shape=[batch_size, src_max_length, 1, -1])
    input_trg_data = tf.reshape(input_trg_data, shape=[-1, trg_unit_dim])
    input_trg_data = tf.matmul(input_trg_data, pre_nonlinear_trg_weight)
    input_trg_data = tf.reshape(input_trg_data, shape=[batch_size, 1, trg_max_length, -1])
    input_src_data = tf.tile(input_src_data, multiples=[1, 1, trg_max_length, 1])
    input_trg_data = tf.tile(input_trg_data, multiples=[1, src_max_length, 1, 1])
    input_attention = input_src_data + input_trg_data
    input_attention = tf.nn.tanh(input_attention + pre_nonlinear_bias)
    attention_dim = tf.shape(input_attention)[-1]
    input_attention = tf.reshape(input_attention, shape=[-1, attention_dim])
    input_attention = tf.matmul(input_attention, post_nonlinear_weight)
    input_attention = tf.reshape(input_attention, shape=[batch_size, src_max_length, trg_max_length])
    
    return input_attention

def _generate_linear_plus_attention_score(input_src_data,
                                          input_trg_data,
                                          attention_matrix):
    """generate linear plus attention score"""
    input_src_shape = tf.shape(input_src_data)
    input_trg_shape = tf.shape(input_trg_data)
    batch_size = input_src_shape[0]
    src_max_length = input_src_shape[1]
    trg_max_length = input_trg_shape[1]
    src_unit_dim = input_src_shape[2]
    trg_unit_dim = input_trg_shape[2]
    mul_unit_dim = src_unit_dim
    linear_plus_src_weight = tf.transpose(attention_matrix[0], perm=[1, 0])
    linear_plus_trg_weight = tf.transpose(attention_matrix[1], perm=[1, 0])
    linear_plus_mul_weight = tf.transpose(attention_matrix[2], perm=[1, 0])
    input_src_data = tf.expand_dims(input_src_data, axis=2)
    input_trg_data = tf.expand_dims(input_trg_data, axis=1)
    input_src_data = tf.tile(input_src_data, multiples=[1, 1, trg_max_length, 1])
    input_trg_data = tf.tile(input_trg_data, multiples=[1, src_max_length, 1, 1])
    input_mul_data = input_src_data * input_trg_data
    input_src_data = tf.reshape(input_src_data, shape=[-1, src_unit_dim])
    input_src_data = tf.matmul(input_src_data, linear_plus_src_weight)
    input_src_data = tf.reshape(input_src_data, shape=[batch_size, src_max_length, trg_max_length, -1])
    input_trg_data = tf.reshape(input_trg_data, shape=[-1, trg_unit_dim])
    input_trg_data = tf.matmul(input_trg_data, linear_plus_trg_weight)
    input_trg_data = tf.reshape(input_trg_data, shape=[batch_size, src_max_length, trg_max_length, -1])
    input_mul_data = tf.reshape(input_mul_data, shape=[-1, mul_unit_dim])
    input_mul_data = tf.matmul(input_mul_data, linear_plus_mul_weight)
    input_mul_data = tf.reshape(input_mul_data, shape=[batch_size, src_max_length, trg_max_length, -1])
    input_attention = input_src_data + input_trg_data + input_mul_data
    input_attention = tf.reshape(input_attention, shape=[batch_size, src_max_length, trg_max_length])
    
    return input_attention

def _generate_nonlinear_plus_attention_score(input_src_data,
                                             input_trg_data,
                                             attention_matrix):
    """generate nonlinear plus attention score"""
    input_src_shape = tf.shape(input_src_data)
    input_trg_shape = tf.shape(input_trg_data)
    batch_size = input_src_shape[0]
    src_max_length = input_src_shape[1]
    trg_max_length = input_trg_shape[1]
    src_unit_dim = input_src_shape[2]
    trg_unit_dim = input_trg_shape[2]
    mul_unit_dim = src_unit_dim
    pre_nonlinear_plus_src_weight = tf.transpose(attention_matrix[0], perm=[1, 0])
    pre_nonlinear_plus_trg_weight = tf.transpose(attention_matrix[1], perm=[1, 0])
    pre_nonlinear_plus_mul_weight = tf.transpose(attention_matrix[2], perm=[1, 0])
    pre_nonlinear_plus_bias = tf.reshape(attention_matrix[3], shape=[1, 1, 1, -1])
    post_nonlinear_plus_weight = tf.transpose(attention_matrix[4], perm=[1, 0])
    input_src_data = tf.reshape(input_src_data, shape=[batch_size, src_max_length, 1, -1])
    input_trg_data = tf.reshape(input_trg_data, shape=[batch_size, 1, trg_max_length, -1])
    input_src_data = tf.tile(input_src_data, multiples=[1, 1, trg_max_length, 1])
    input_trg_data = tf.tile(input_trg_data, multiples=[1, src_max_length, 1, 1])
    input_mul_data = input_src_data * input_trg_data
    input_src_data = tf.reshape(input_src_data, shape=[-1, src_unit_dim])
    input_src_data = tf.matmul(input_src_data, pre_nonlinear_plus_src_weight)
    input_src_data = tf.reshape(input_src_data, shape=[batch_size, src_max_length, trg_max_length, -1])
    input_trg_data = tf.reshape(input_trg_data, shape=[-1, trg_unit_dim])
    input_trg_data = tf.matmul(input_trg_data, pre_nonlinear_plus_trg_weight)
    input_trg_data = tf.reshape(input_trg_data, shape=[batch_size, src_max_length, trg_max_length, -1])
    input_mul_data = tf.reshape(input_mul_data, shape=[-1, mul_unit_dim])
    input_mul_data = tf.matmul(input_mul_data, pre_nonlinear_plus_mul_weight)
    input_mul_data = tf.reshape(input_mul_data, shape=[batch_size, src_max_length, trg_max_length, -1])
    input_attention = input_src_data + input_trg_data + input_mul_data
    input_attention = tf.nn.tanh(input_attention + pre_nonlinear_plus_bias)
    attention_dim = tf.shape(input_attention)[-1]
    input_attention = tf.reshape(input_attention, shape=[-1, attention_dim])
    input_attention = tf.matmul(input_attention, post_nonlinear_plus_weight)
    input_attention = tf.reshape(input_attention, shape=[batch_size, src_max_length, trg_max_length])
    
    return input_attention

def _generate_attention_mask(input_src_mask,
                             input_trg_mask,
                             remove_diag=False):
    """generate attention mask"""
    input_src_shape = tf.shape(input_src_mask)
    input_trg_shape = tf.shape(input_trg_mask)
    batch_size = input_src_shape[0]
    src_max_length = input_src_shape[1]
    trg_max_length = input_trg_shape[1]
    input_src_mask = tf.reshape(input_src_mask, shape=[batch_size, src_max_length, 1, -1])
    input_trg_mask = tf.reshape(input_trg_mask, shape=[batch_size, 1, trg_max_length, -1])
    input_src_mask = tf.tile(input_src_mask, multiples=[1, 1, trg_max_length, 1])
    input_trg_mask = tf.tile(input_trg_mask, multiples=[1, src_max_length, 1, 1])
    input_mask = input_src_mask * input_trg_mask
    input_mask = tf.reshape(input_mask, shape=[batch_size, src_max_length, trg_max_length])
    if remove_diag == True:
        input_mask = input_mask * (1 - tf.eye(src_max_length, trg_max_length))
    
    return input_mask

def _generate_projection_data(input_data,
                              projection_matrix):
    """generate projection data"""
    input_shape = tf.shape(input_data)
    batch_size = input_shape[0]
    max_length = input_shape[1]
    unit_dim = input_shape[2]
    input_projection = tf.reshape(input_data, shape=[-1, unit_dim])
    input_projection = tf.matmul(input_projection, projection_matrix)
    input_projection = tf.reshape(input_projection, shape=[batch_size, max_length, -1])
    
    return input_projection

class Attention(object):
    """attention layer"""
    def __init__(self,
                 src_dim,
                 trg_dim,
                 att_dim,
                 score_type,
                 is_self,
                 external_matrix=None,
                 num_gpus=1,
                 default_gpu_id=0,
                 trainable=True,
                 scope="attention"):
        """initialize attention layer"""
        self.src_dim = src_dim
        self.trg_dim = trg_dim
        self.att_dim = att_dim
        self.score_type = score_type
        self.is_self = is_self
        self.trainable = trainable
        self.scope = scope
        self.device_spec = get_device_spec(default_gpu_id, num_gpus)
        
        with tf.variable_scope(self.scope, reuse=tf.AUTO_REUSE), tf.device(self.device_spec):
            if external_matrix == None:
                self.attention_matrix = _create_attention_matrix(self.src_dim,
                    self.trg_dim, self.att_dim, self.score_type, self.trainable)
            else:
                self.attention_matrix = external_matrix
    
    def __call__(self,
                 input_src_data,
                 input_trg_data,
                 input_src_mask,
                 input_trg_mask):
        """call attention layer"""
        with tf.variable_scope(self.scope, reuse=tf.AUTO_REUSE), tf.device(self.device_spec):
            input_src_data = input_src_data * input_src_mask
            input_trg_data = input_trg_data * input_trg_mask
            input_attention_score = _generate_attention_score(input_src_data,
                input_trg_data, self.attention_matrix, self.score_type)
            input_attention_mask = _generate_attention_mask(input_src_mask, input_trg_mask, self.is_self)
            input_attention_weight = softmax_with_mask(input_attention_score,
                input_attention_mask, axis=-1, keepdims=True)
            output_attention = tf.matmul(input_attention_weight, input_trg_data)
            output_mask = input_src_mask
            output_attention = output_attention * output_mask
        
        return output_attention, output_mask
    
    def get_attention_matrix(self):
        return self.attention_matrix

class MaxAttention(object):
    """max-attention layer"""
    def __init__(self,
                 src_dim,
                 trg_dim,
                 att_dim,
                 score_type,
                 is_self,
                 external_matrix=None,
                 num_gpus=1,
                 default_gpu_id=0,
                 trainable=True,
                 scope="max_att"):
        """initialize max-attention layer"""       
        self.src_dim = src_dim
        self.trg_dim = trg_dim
        self.att_dim = att_dim
        self.score_type = score_type
        self.is_self = is_self
        self.trainable = trainable
        self.scope = scope
        self.device_spec = get_device_spec(default_gpu_id, num_gpus)
        
        with tf.variable_scope(self.scope, reuse=tf.AUTO_REUSE), tf.device(self.device_spec):
            if external_matrix == None:
                self.attention_matrix = _create_attention_matrix(self.src_dim,
                    self.trg_dim, self.att_dim, self.score_type, self.trainable)
            else:
                self.attention_matrix = external_matrix
    
    def __call__(self,
                 input_src_data,
                 input_trg_data,
                 input_src_mask,
                 input_trg_mask):
        """call max-attention layer"""
        with tf.variable_scope(self.scope, reuse=tf.AUTO_REUSE), tf.device(self.device_spec):
            input_src_data = input_src_data * input_src_mask
            input_trg_data = input_trg_data * input_trg_mask
            input_attention_score = _generate_attention_score(input_src_data,
                input_trg_data, self.attention_matrix, self.score_type)
            input_attention_mask = _generate_attention_mask(input_src_mask, input_trg_mask, self.is_self)
            input_attention_score = tf.reduce_max(input_attention_score, axis=-1, keep_dims=True)
            input_attention_mask = tf.reduce_max(input_attention_mask, axis=-1, keep_dims=True)
            input_attention_weight = softmax_with_mask(input_attention_score,
                input_attention_mask, axis=-2, keepdims=True)
            input_attention_weight = tf.transpose(input_attention_weight, perm=[0, 2, 1])
            output_attention = tf.matmul(input_attention_weight, input_src_data)
            src_max_length = tf.shape(input_src_data)[1]
            output_attention = tf.tile(output_attention, multiples=[1, src_max_length, 1])
            output_mask = input_src_mask
            output_attention = output_attention * output_mask
        
        return output_attention, output_mask
    
    def get_attention_matrix(self):
        return self.attention_matrix

class HeadAttention(object):
    """head-attention layer"""
    def __init__(self,
                 src_dim,
                 trg_dim,
                 att_dim,
                 score_type,
                 is_self,
                 external_matrix=None,
                 num_gpus=1,
                 default_gpu_id=0,
                 trainable=True,
                 scope="head_att"):
        """initialize head-attention layer"""
        self.src_dim = src_dim
        self.trg_dim = trg_dim
        self.att_dim = att_dim
        self.score_type = score_type
        self.is_self = is_self
        self.trainable = trainable
        self.scope = scope
        self.device_spec = get_device_spec(default_gpu_id, num_gpus)
        
        with tf.variable_scope(self.scope, reuse=tf.AUTO_REUSE), tf.device(self.device_spec):
            if external_matrix == None:
                (q_att_dim, k_att_dim, v_att_dim) = tuple(self.att_dim)
                self.projection_matrix = [
                    _create_projection_matrix(self.src_dim, q_att_dim, self.trainable),
                    _create_projection_matrix(self.trg_dim, k_att_dim, self.trainable),
                    _create_projection_matrix(self.trg_dim, v_att_dim, self.trainable)
                ]
                self.attention_matrix = _create_attention_matrix(q_att_dim,
                    k_att_dim, k_att_dim, self.score_type, self.trainable)
            else:
                self.projection_matrix = external_matrix["projection"]
                self.attention_matrix = external_matrix["attention"]
    
    def __call__(self,
                 input_src_data,
                 input_trg_data,
                 input_src_mask,
                 input_trg_mask):
        """call head-attention layer"""
        with tf.variable_scope(self.scope, reuse=tf.AUTO_REUSE), tf.device(self.device_spec):
            input_src_data = input_src_data * input_src_mask
            input_trg_data = input_trg_data * input_trg_mask
            input_query_data = _generate_projection_data(input_src_data, self.projection_matrix[0])
            input_key_data = _generate_projection_data(input_trg_data, self.projection_matrix[1])
            input_value_data = _generate_projection_data(input_trg_data, self.projection_matrix[2])
            input_attention_score = _generate_attention_score(input_query_data,
                input_key_data, self.attention_matrix, self.score_type)
            input_attention_mask = _generate_attention_mask(input_src_mask, input_trg_mask, self.is_self)
            input_attention_weight = softmax_with_mask(input_attention_score,
                input_attention_mask, axis=-1, keepdims=True)
            output_attention = tf.matmul(input_attention_weight, input_value_data)
            output_mask = input_src_mask
            output_attention = output_attention * output_mask
        
        return output_attention, output_mask
    
    def get_projection_matrix(self):
        return self.projection_matrix
    
    def get_attention_matrix(self):
        return self.attention_matrix
