# -*- coding: utf-8 -*-
"""


https://colab.research.google.com/drive/1f2oonnG_-NlXoY_EXhUwAXkuYJwLDqIu?usp=sharing

"""
# from fastai.callback.hook import Hooks
import torch
from torch import nn
import torch.nn.functional as F




def check_lstm():
    """function check_lstm.
    Doc::
            
            Args:
            Returns:
                
    """

    #############################################################################
    #### Internal LSTM parameters
    bs, seq_len, d_in = 4, 10, 8
    x = torch.randn(bs, seq_len, d_in)

    d_h = 16
    rnn = nn.LSTM(d_in, d_h, batch_first=True)

    for n, p in rnn.named_parameters():
        print(f"{n:<12} {p.shape}")


    ##### LSTM forward output
    out , (h, c) = rnn(x)
    print(out.shape, h.shape, c.shape)
    # the last element of out is equal to final hidden state `h`
    assert (out[:, -1, :] == h.squeeze()).all()


    # h is fed recursively to the next timestep
    # seme with c
    # the returned value are the final ones
    # so out is basically history of `h`s

    out2, _ = rnn(x, (h, c))
    ### this one I know, but did not rememebr aht last element  == hiddne shape
    ### Sure, no pb. 
    assert not torch.allclose(out.data, out2.data)



    ##########################################################################
    ####### 2 layers versions
    rnn2 = nn.LSTM(d_in, d_h, num_layers=2, batch_first=True)

    for n, p in rnn2.named_parameters():
        print(f"{n:<12} {p.shape}")

    out , (h, c) = rnn2(x)
    print(out.shape, h.shape, c.shape)
    assert (out[:, -1, :] == h[-1]).all()
    """ 2 layers stacked
    weight_ih_l0 torch.Size([64, 8])   8 = 1 * 8
    weight_hh_l0 torch.Size([64, 16])
    bias_ih_l0   torch.Size([64])
    bias_hh_l0   torch.Size([64])

    weight_ih_l1 torch.Size([64, 16])  16 = 2 * 8
    weight_hh_l1 torch.Size([64, 16])
    bias_ih_l1   torch.Size([64])
    bias_hh_l1   torch.Size([64])

    out,   h,     c
    torch.Size([4, 10, 16]) torch.Size([2, 4, 16]) torch.Size([2, 4, 16]) 


    """






    rnn_b = nn.LSTM(d_in, d_h, num_layers=1, bidirectional=True, batch_first=True)
    for n, p in rnn_b.named_parameters():
        print(f"{n:<20} {p.shape}")

    out , (h, c) = rnn_b(x)
    print(out.shape, h.shape, c.shape)
    assert (out[:, -1, :16] == h[0]).all()
    assert (out[:, 0, 16:] == h[1]).all()
    """
    weight_ih_l0         torch.Size([64, 8])
    weight_hh_l0         torch.Size([64, 16])
    bias_ih_l0           torch.Size([64])
    bias_hh_l0           torch.Size([64])

    weight_ih_l0_reverse torch.Size([64, 8])
    weight_hh_l0_reverse torch.Size([64, 16])
    bias_ih_l0_reverse   torch.Size([64])
    bias_hh_l0_reverse   torch.Size([64])


    szie is 32= bi-directionnal part ??  (I know less the bi-rectioonal formulae..., but thats ok)
    out,   h, c
    torch.Size([4, 10, 32]) torch.Size([2, 4, 16]) torch.Size([2, 4, 16])    


    yes, you can check the correspondence with h below
    it's :16 for forward and 16: for backward along feature dimention

    along feature dimension !!???  (will cehck bi-rectionnal formulae)
    thought it was both on the sequence dimension...
    thats oksu,re no pob,

    that's how it is returned in pytorch [bs, seq_len, 2*d_hidden]

    """

    # need to apt install graphviz



    #### TensoboardX  does it too ??/ but more heavier...ok, thanks.

    rnn_b2 = nn.LSTM(d_in, d_h, num_layers=2, bidirectional=True, batch_first=True)
    for n, p in rnn_b.named_parameters():
        print(f"{n:<20} {p.shape}")

    out, (h, c) = rnn_b2(x)
    print(out.shape, h.shape, c.shape)
    assert (out[:, -1, :16] == h[2]).all()
    assert (out[:, 0, 16:] == h[3]).all()
    """
    weight_ih_l0         torch.Size([64, 8])
    weight_hh_l0         torch.Size([64, 16])
    bias_ih_l0           torch.Size([64])
    bias_hh_l0           torch.Size([64])
    weight_ih_l0_reverse torch.Size([64, 8])
    weight_hh_l0_reverse torch.Size([64, 16])
    bias_ih_l0_reverse   torch.Size([64])
    bias_hh_l0_reverse   torch.Size([64])
    torch.Size([4, 10, 32]) torch.Size([4, 4, 16]) torch.Size([4, 4, 16])


    """
    x.requires_grad_()
    out, (h, c) = rnn(x)

    loss = out.sum()
    grad_x, = torch.autograd.grad(loss, x, create_graph=True)


    #### Dsiplay the compute graph.
    import torchviz
    torchviz.make_dot((grad_x, x, out), {"grad_x": grad_x, "x": x, "loss": loss})

    hook_ih = rnn.weight_ih_l0.register_hook(lambda x: print(f"comuted ih grad shape {x.shape}"))
    hook_hh = rnn.weight_hh_l0.register_hook(lambda x: print(f"comuted hh grad shape {x.shape}"))

    out, (h, c)  = rnn(x)
    out.mean().backward()

    hook_ih.remove()
    hook_hh.remove()


    #### Padding check ???
    """
    tensor(False)
    What do you mean by PackedSequence ??
    you mean a small sequence, and pad by empty token ?
    AttributeError: 'PackedSequence' object has no attribute 'shape'

    padd: in understand  (ie small seuqnce paaded to match input size)
    pack : what does it mean ?? I see
        I see, it's ckind of compression/compaction... of the input to save the zeros...
        ok No pb

    Will copy paste the training loop below, we cna discuss a bit


    that's alternative way to represent inpu sequence, can be more compute efficient if you got a lot of padding (sequences with length variation)
    the shape[0] is some of non-zero (non-padding) enties in input
    that is a type of input
    torch RNN can accept either Tensor or PackedSequence
    you can print out x_pack, out_pack to see

    when you deal with PackedSequence h will correspond to output at last index of the sequence, 
    out[torch.arange(4), length-1, :]

    """
    length = torch.randint(5, 10, (x.size(0), ))
    from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence, pad_sequence
    x = [torch.randn(l, d_in) for l in length]
    x = pad_sequence(x, batch_first=True)
    print( x.shape )   ##### tensor(False)


    x_pack = pack_padded_sequence(x, length, enforce_sorted=False, batch_first=True)
    out_pack, (h, c) = rnn(x_pack)
    out, length_out = pad_packed_sequence(out_pack, batch_first=True)
    assert (length_out == length).all()

    (out[:, -1, :] == h[0]).all()


    ### x = [torch.randn(l, d_in) for l in length]
    print(x_pack.data.shape, out_pack.data.shape)
    #### torch.Size([28, 8]) torch.Size([28, 16])





    """
    Training loop seems standard
    Good question,  the model I picked up somewhere...
    but got some issues with trainin accuracy... (dont know)

    tehcnically, the dataloader batch_size =16  
        code wont change ???
        Yes, true, need to change the harcoding...

        batch_size =  1
        x = x.reshape((batch_size, self.seq_len, self.n_features))

        assert x.shape == (batch_size, self.seq_len, self.n_features)   #



    next sesison, we can disuss how to use this layer into the exisint model.
    instead of LSTM layer...
    https://pytorch.org/docs/stable/generated/torch.nn.TransformerEncoderLayer.html#torch.nn.TransformerEncoderLayer      

    Suppose, we need to match the dimensions...
    It';s good practice 


    yes
    once input is fed in batches you don't need dto reshape

        
    I so inputing extra batch dim hardcoded in the model
    that will need to be removed

    """



