# Copyright 2018 The KaiJIN Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
r"""RNN"""

import math
import torch
from torch import nn
from torch.nn import functional as F


def _update_state(x, wx, bx, h, wh, bh):
  """ (W_x * x + b_x + W_h * h + bh) """
  return F.linear(x, wx, bx) + F.linear(h, wh, bh)


class RNN(nn.Module):
  def __init__(self,
               input_size,
               hidden_size,
               num_layers=1,
               bias=True,
               nonlinearity='tanh',
               batch_first=True):
    super(RNN, self).__init__()
    self._all_weights = []
    self._num_layers = num_layers
    self._bias = bias
    self._hidden_size = hidden_size
    self._input_size = input_size
    self._batch_first = batch_first
    if nonlinearity == 'tanh':
      self._activation_fn = torch.tanh
    elif nonlinearity == 'relu':
      self._activation_fn = torch.relu
    else:
      raise NotImplementedError(self._activation_fn)

    for layer in range(num_layers):
      input_size = input_size if layer == 0 else hidden_size
      w_ih = nn.Parameter(torch.Tensor(hidden_size, input_size))
      w_hh = nn.Parameter(torch.Tensor(hidden_size, hidden_size))
      b_ih = nn.Parameter(torch.Tensor(hidden_size)) if bias else None
      b_hh = nn.Parameter(torch.Tensor(hidden_size)) if bias else None
      layer_params = (w_ih, w_hh, b_ih, b_hh)
      # name
      param_names = ['weight_ih_l{}{}', 'weight_hh_l{}{}']
      if bias:
        param_names += ['bias_ih_l{}{}', 'bias_hh_l{}{}']
      param_names = [x.format(layer, '') for x in param_names]
      # add into
      for name, param in zip(param_names, layer_params):
        setattr(self, name, param)
      self._all_weights.append((w_ih, w_hh, b_ih, b_hh))
    self.reset_parameters()

  def reset_parameters(self):
    stdv = 1.0 / math.sqrt(self._hidden_size)
    for data in self.parameters():
      nn.init.uniform_(data, -stdv, stdv)

  def forward(self, x, hx=None):
    """ For each cell will execute:

    h_t = \text{tanh}(W_{ih} x_t + b_{ih} + W_{hh} h_{(t-1)} + b_{hh})

    where :math:`h_t` is the hidden state at time `t`, :math:`x_t` is
    the input at time `t`, and :math:`h_{(t-1)}` is the hidden state of the
    previous layer at time `t-1` or the initial hidden state at time `0`.
    If :attr:`nonlinearity` is ``'relu'``, then `ReLU` is used instead of `tanh`.

    Arguments:
      x: [bs, seq, input_size]
      hx: [num_layer, seq, hidden_size] initialize to zeros if hx is None
    """
    assert len(list(x.shape)) == 3
    bs, seq, _ = list(x.shape)

    # convert to [seq, bs, input_size]
    if self._batch_first:
      x = x.transpose(1, 0)

    # hx should be [n_layers, seq+1, bs, hidden_size]
    if hx is None:
      hx = torch.zeros(self._num_layers, seq + 1, bs, self._hidden_size,
                       dtype=x.dtype, device=x.device)
    else:
      raise NotImplementedError

    # batchsize-rnn
    for layer in range(self._num_layers):
      w_ih, w_hh, b_ih, b_hh = self._all_weights[layer]
      for t in range(seq):
        # t_0 as initial input, t_1 as output
        # [bs, size]
        x_t = hx[layer - 1, t + 1].clone() if layer else x[t].clone()
        h_t = hx[layer, t].clone()
        fx_t = F.linear(x_t, w_ih, b_ih)
        fh_t = F.linear(h_t, w_hh, b_hh)
        nh_t = self._activation_fn(fx_t + fh_t)
        hx[layer, t + 1] = nh_t

    # where we just output the last state
    output = hx[self._num_layers - 1, 1:].transpose(1, 0)
    return output, hx[:, seq, :]


class GRU(nn.Module):
  def __init__(self,
               input_size,
               hidden_size,
               num_layers=1,
               bias=True,
               nonlinearity='tanh',
               batch_first=True):
    """
    Attributes:
      weight_ih_l[k] : the learnable input-hidden weights of the :math:`\text{k}^{th}` layer
          (W_ir|W_iz|W_in), of shape `(3*hidden_size, input_size)` for `k = 0`.
          Otherwise, the shape is `(3*hidden_size, num_directions * hidden_size)`
      weight_hh_l[k] : the learnable hidden-hidden weights of the :math:`\text{k}^{th}` layer
          (W_hr|W_hz|W_hn), of shape `(3*hidden_size, hidden_size)`
      bias_ih_l[k] : the learnable input-hidden bias of the :math:`\text{k}^{th}` layer
          (b_ir|b_iz|b_in), of shape `(3*hidden_size)`
      bias_hh_l[k] : the learnable hidden-hidden bias of the :math:`\text{k}^{th}` layer
          (b_hr|b_hz|b_hn), of shape `(3*hidden_size)`
    """
    super(GRU, self).__init__()
    self._all_weights = []
    self._num_layers = num_layers
    self._bias = bias
    self._hidden_size = hidden_size
    self._input_size = input_size
    self._batch_first = batch_first
    if nonlinearity == 'tanh':
      self._activation_fn = torch.tanh
    elif nonlinearity == 'relu':
      self._activation_fn = torch.relu
    else:
      raise NotImplementedError(self._activation_fn)
    self._s = torch.sigmoid

    for layer in range(num_layers):
      input_size = input_size if layer == 0 else hidden_size
      w_ih = nn.Parameter(torch.Tensor(hidden_size * 3, input_size))
      w_hh = nn.Parameter(torch.Tensor(hidden_size * 3, hidden_size))
      b_ih = nn.Parameter(torch.Tensor(hidden_size * 3)) if bias else None
      b_hh = nn.Parameter(torch.Tensor(hidden_size * 3)) if bias else None
      layer_params = (w_ih, w_hh, b_ih, b_hh)
      # name
      param_names = ['weight_ih_l{}{}', 'weight_hh_l{}{}']
      if bias:
        param_names += ['bias_ih_l{}{}', 'bias_hh_l{}{}']
      param_names = [x.format(layer, '') for x in param_names]
      # add into
      for name, param in zip(param_names, layer_params):
        setattr(self, name, param)
      self._all_weights.append((w_ih, w_hh, b_ih, b_hh))
    self.reset_parameters()

  def reset_parameters(self):
    stdv = 1.0 / math.sqrt(self._hidden_size)
    for data in self.parameters():
      nn.init.uniform_(data, -stdv, stdv)

  def forward(self, x, hx=None):
    """
    Applies a multi-layer gated recurrent unit (GRU) RNN to an input sequence.

    For each element in the input sequence, each layer computes the following
    function:

    .. math::
        \begin{array}{ll}
            r_t = \\sigma(W_{ir} x_t + b_{ir} + W_{hr} h_{(t-1)} + b_{hr}) \\
            z_t = \\sigma(W_{iz} x_t + b_{iz} + W_{hz} h_{(t-1)} + b_{hz}) \\
            n_t = \tanh(W_{in} x_t + b_{in} + r_t * (W_{hn} h_{(t-1)}+ b_{hn})) \\
            h_t = (1 - z_t) * n_t + z_t * h_{(t-1)}
        \\end{array}

    where :math:`h_t` is the hidden state at time `t`, :math:`x_t` is the input
    at time `t`, :math:`h_{(t-1)}` is the hidden state of the layer
    at time `t-1` or the initial hidden state at time `0`, and :math:`r_t`,
    :math:`z_t`, :math:`n_t` are the reset, update, and new gates, respectively.
    :math:`\\sigma` is the sigmoid function, and :math:`*` is the Hadamard product.

    In a multilayer GRU, the input :math:`x^{(l)}_t` of the :math:`l` -th layer
    (:math:`l >= 2`) is the hidden state :math:`h^{(l-1)}_t` of the previous layer multiplied by
    dropout :math:`\\delta^{(l-1)}_t` where each :math:`\\delta^{(l-1)}_t` is a Bernoulli random
    variable which is :math:`0` with probability :attr:`dropout`.

    Arguments:
      x: [bs, seq, input_size]
      hx: [num_layer, bs, hidden_size] initialize to zeros if hx is None
    """
    assert len(list(x.shape)) == 3
    bs, seq, _ = list(x.shape)

    # convert to [seq, bs, input_size]
    if self._batch_first:
      x = x.transpose(1, 0)

    # hx should be [n_layers, seq+1, bs, hidden_size]
    if hx is None:
      hx = torch.zeros(self._num_layers, seq + 1, bs, self._hidden_size,
                       dtype=x.dtype, device=x.device)
    else:
      raise NotImplementedError

    # batchsize-rnn
    for layer in range(self._num_layers):
      w_ih, w_hh, b_ih, b_hh = self._all_weights[layer]
      w_ir, w_iz, w_in = w_ih.chunk(3)
      w_hr, w_hz, w_hn = w_hh.chunk(3)
      b_ir, b_iz, b_in = b_ih.chunk(3) if self._bias else (None, None, None)
      b_hr, b_hz, b_hn = b_hh.chunk(3) if self._bias else (None, None, None)
      for t in range(seq):
        # t_0 as initial input, t_1 as output
        # [bs, size]
        x_t = hx[layer - 1, t + 1].clone() if layer else x[t].clone()
        h_t = hx[layer, t].clone()
        fr_t = self._s(F.linear(x_t, w_ir, b_ir) + F.linear(h_t, w_hr, b_hr))
        fz_t = self._s(F.linear(x_t, w_iz, b_iz) + F.linear(h_t, w_hz, b_hz))
        fn_t = self._activation_fn(F.linear(x_t, w_in, b_in) +
                                   fr_t * F.linear(h_t, w_hn, b_hn))
        fh_t = (1 - fz_t) * fn_t + fz_t * h_t
        hx[layer, t + 1] = fh_t

    # where we just output the last state
    output = hx[self._num_layers - 1, 1:].transpose(1, 0)
    return output, hx[:, seq, :]


class LSTM(nn.Module):
  def __init__(self,
               input_size,
               hidden_size,
               num_layers=1,
               bias=True,
               nonlinearity='tanh',
               batch_first=True):
    """
    Attributes:
      weight_ih_l[k] : the learnable input-hidden weights of the :math:`\text{k}^{th}` layer
          `(W_ii|W_if|W_ig|W_io)`, of shape `(4*hidden_size, input_size)` for `k = 0`.
          Otherwise, the shape is `(4*hidden_size, num_directions * hidden_size)`
      weight_hh_l[k] : the learnable hidden-hidden weights of the :math:`\text{k}^{th}` layer
          `(W_hi|W_hf|W_hg|W_ho)`, of shape `(4*hidden_size, hidden_size)`
      bias_ih_l[k] : the learnable input-hidden bias of the :math:`\text{k}^{th}` layer
          `(b_ii|b_if|b_ig|b_io)`, of shape `(4*hidden_size)`
      bias_hh_l[k] : the learnable hidden-hidden bias of the :math:`\text{k}^{th}` layer
          `(b_hi|b_hf|b_hg|b_ho)`, of shape `(4*hidden_size)`
    """
    super(LSTM, self).__init__()
    self._all_weights = []
    self._num_layers = num_layers
    self._bias = bias
    self._hidden_size = hidden_size
    self._input_size = input_size
    self._batch_first = batch_first
    if nonlinearity == 'tanh':
      self._a = torch.tanh
    elif nonlinearity == 'relu':
      self._a = torch.relu
    else:
      raise NotImplementedError(nonlinearity)
    self._s = torch.sigmoid

    for layer in range(num_layers):
      input_size = input_size if layer == 0 else hidden_size
      w_ih = nn.Parameter(torch.Tensor(hidden_size * 4, input_size))
      w_hh = nn.Parameter(torch.Tensor(hidden_size * 4, hidden_size))
      b_ih = nn.Parameter(torch.Tensor(hidden_size * 4)) if bias else None
      b_hh = nn.Parameter(torch.Tensor(hidden_size * 4)) if bias else None
      layer_params = (w_ih, w_hh, b_ih, b_hh)
      # name
      param_names = ['weight_ih_l{}{}', 'weight_hh_l{}{}']
      if bias:
        param_names += ['bias_ih_l{}{}', 'bias_hh_l{}{}']
      param_names = [x.format(layer, '') for x in param_names]
      # add into
      for name, param in zip(param_names, layer_params):
        setattr(self, name, param)
      self._all_weights.append((w_ih, w_hh, b_ih, b_hh))
    self.reset_parameters()

  def reset_parameters(self):
    stdv = 1.0 / math.sqrt(self._hidden_size)
    for data in self.parameters():
      nn.init.uniform_(data, -stdv, stdv)

  def forward(self, x, hx=None, cx=None):
    """ Applies a multi-layer long short-term memory (LSTM) RNN to an input
    sequence.

    For each element in the input sequence, each layer computes the following
    function:

    .. math::
        \begin{array}{ll} \\
            i_t = \\sigma(W_{ii} x_t + b_{ii} + W_{hi} h_{(t-1)} + b_{hi}) \\
            f_t = \\sigma(W_{if} x_t + b_{if} + W_{hf} h_{(t-1)} + b_{hf}) \\
            g_t = \tanh(W_{ig} x_t + b_{ig} + W_{hg} h_{(t-1)} + b_{hg}) \\
            o_t = \\sigma(W_{io} x_t + b_{io} + W_{ho} h_{(t-1)} + b_{ho}) \\
            c_t = f_t * c_{(t-1)} + i_t * g_t \\
            h_t = o_t * \tanh(c_t) \\
        \\end{array}

    where :math:`h_t` is the hidden state at time `t`, :math:`c_t` is the cell
    state at time `t`, :math:`x_t` is the input at time `t`, :math:`h_{(t-1)}`
    is the hidden state of the layer at time `t-1` or the initial hidden
    state at time `0`, and :math:`i_t`, :math:`f_t`, :math:`g_t`,
    :math:`o_t` are the input, forget, cell, and output gates, respectively.
    :math:`\\sigma` is the sigmoid function, and :math:`*` is the Hadamard product.

    In a multilayer LSTM, the input :math:`x^{(l)}_t` of the :math:`l` -th layer
    (:math:`l >= 2`) is the hidden state :math:`h^{(l-1)}_t` of the previous layer multiplied by
    dropout :math:`\\delta^{(l-1)}_t` where each :math:`\\delta^{(l-1)}_t` is a Bernoulli random
    variable which is :math:`0` with probability :attr:`dropout`.


    Arguments:
      x: [bs, seq, input_size]
      hx: [num_layer, bs, hidden_size] initialize to zeros if hx is None
      cx: [num_layer, bs, hidden_size] initialize to zeros if cx is None
    """
    assert len(list(x.shape)) == 3
    bs, seq, _ = list(x.shape)

    # convert to [seq, bs, input_size]
    if self._batch_first:
      x = x.transpose(1, 0)

    # hx should be [n_layers, seq+1, bs, hidden_size]
    if hx is None:
      hx = torch.zeros(self._num_layers, seq + 1, bs, self._hidden_size,
                       dtype=x.dtype, device=x.device)
    else:
      raise NotImplementedError

    # cx
    if cx is None:
      cx = torch.zeros(self._num_layers, seq + 1, bs, self._hidden_size,
                       dtype=x.dtype, device=x.device)
    else:
      raise NotImplementedError

    # batchsize-rnn
    for layer in range(self._num_layers):
      w_ih, w_hh, b_ih, b_hh = self._all_weights[layer]
      w_ii, w_if, w_ig, w_io = w_ih.chunk(4)
      w_hi, w_hf, w_hg, w_ho = w_hh.chunk(4)
      b_ii, b_if, b_ig, b_io = b_ih.chunk(4) if self._bias else (None, None, None, None)
      b_hi, b_hf, b_hg, b_ho = b_hh.chunk(4) if self._bias else (None, None, None, None)
      for t in range(seq):
        # t_0 as initial input, t_1 as output
        # [bs, size]
        x_t = hx[layer - 1, t + 1].clone() if layer else x[t].clone()
        h_t = hx[layer, t].clone()
        c_t = cx[layer, t].clone()
        fi_t = self._s(_update_state(x_t, w_ii, b_ii, h_t, w_hi, b_hi))
        ff_t = self._s(_update_state(x_t, w_if, b_if, h_t, w_hf, b_hf))
        fo_t = self._s(_update_state(x_t, w_io, b_io, h_t, w_ho, b_ho))
        fg_t = self._a(_update_state(x_t, w_ig, b_ig, h_t, w_hg, b_hg))
        nc_t = ff_t * c_t + fi_t * fg_t
        nh_t = fo_t * self._a(nc_t)
        hx[layer, t + 1] = nh_t
        cx[layer, t + 1] = nc_t

    # where we just output the last state
    output = hx[self._num_layers - 1, 1:].transpose(1, 0)
    return output, (hx[:, seq, :], cx[:, seq, :])
