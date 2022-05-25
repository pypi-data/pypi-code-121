import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from dl2050nn.etc import get_cnn_szs

def model_stats(model, bottle=None, szs=None, show_szs=False):
    p = sum([p.numel() for p in model.parameters()])
    s = f'{str(model.__class__.__name__)}: params {p/1e6:,.1f}m'
    if bottle: s+=f', bottles {bottle}' 
    if szs: s+=f', input_sz: {szs[0]}, last_conv_sz {szs[-1]}'
    if szs and show_szs: s+=f'\n\tszs: {szs}'
    print(s)

def init_layer(l):
    if getattr(l, 'bias', None) is not None: nn.init.constant_(l.bias, 0) # l.bias.data.zero_()
    if isinstance(l, (nn.BatchNorm1d, nn.BatchNorm2d)): l.weight.data.fill_(1)
    if isinstance(l, (nn.Linear,)): nn.init.kaiming_normal_(l.weight)
    if isinstance(l, (nn.Embedding,)): l.weight.data.normal_(0., 2./math.sqrt(l.weight.data.size(1)))
        #sc = 2/(w.size(1)+1)
        #w.uniform_(-sc, sc)
    if isinstance(l, (nn.Conv1d, nn.Conv2d)): nn.init.kaiming_normal_(l.weight)

def init_net(m):
    init_layer(m)
    for l in m.children(): init_net(l)

def noop(x): return x
    
# def ReLU_Sim(x): return x.clamp_min(0.) - 0.5
class ReLU_Sim(nn.Module):
    def forward(self, x): return x.clamp_min(0.) - 0.5

class Mish(nn.Module):
    def __init__(self): super().__init__()
    def forward(self, x): return x *( torch.tanh(F.softplus(x)))

default_act =  Mish() # nn.ReLU(inplace=True), Mish()

class Sigmoid(nn.Module):
    def __init__(self, yrange=None):
        super().__init__()
        self.yrange = yrange
    def forward(self, x):
        return torch.sigmoid(x) if self.yrange is None else self.y_range[0]+(self.yrange[1]-self.yrange[0])*torch.sigmoid(x)

# def sigmoid(input, eps=1e-7):
#     "Same as `torch.sigmoid`, plus clamping to `(eps,1-eps)"
#     return input.sigmoid().clamp(eps,1-eps)

class Flatten(nn.Module):
    def forward(self, x): return x.view(x.size(0), -1)

def Linear(n1, n2, p=None, bn=True, act=default_act):
    net = []
    if bn:
        batch = nn.BatchNorm1d(num_features=n1)
        init_layer(batch)
        net += [batch]
    if p is not None: net += [nn.Dropout(p=p)]
    linear = nn.Linear(in_features=n1, out_features=n2)
    init_layer(linear)
    net += [linear]
    if act: net+=[act]
    return nn.Sequential(*net)

def LinearFinal(n1, n2, p=None, act=nn.LogSoftmax(dim=1)): return Linear(n1, n2, p=p, bn=False, act=act)

def Conv2D(n1, n2, ks=3, stride=1, zero_bn=False, act=True):
    bn = nn.BatchNorm2d(n1)
    nn.init.constant_(bn.weight, 0. if zero_bn else 1.)
    conv = nn.Conv2d(n1, n2, kernel_size=ks, stride=stride, padding=ks//2, bias=False)
    layers = [bn, conv]
    if act: layers.append(default_act)
    return nn.Sequential(*layers)
    # PREVIOUS: return F.relu(self.batch(self.conv(x)))

def Conv1D(n1, n2, ks=3, stride=1, zero_bn=False, act=True):
    bn = nn.BatchNorm1d(n1)
    nn.init.constant_(bn.weight, 0. if zero_bn else 1.)
    conv = nn.Conv1d(n1, n2, kernel_size=ks, stride=stride, padding=ks//2, bias=False)
    layers = [bn, conv]
    if act: layers.append(default_act)
    return nn.Sequential(*layers)

class ResBlock2D(nn.Module):
    def __init__(self, ni, nf, stride=1):
        super().__init__()
        layers  = [Conv2D(ni, nf, stride=stride),
                   Conv2D(nf, nf, zero_bn=True, act=False)]
        self.convs = nn.Sequential(*layers)
        self.idconv = noop if ni==nf else Conv2D(ni, nf, ks=1, act=False)
        self.pool = noop if stride==1 else nn.AvgPool2d(2, ceil_mode=True)
    def forward(self, x): return default_act(self.convs(x) + self.idconv(self.pool(x)))

class ResBlock1D(nn.Module):
    def __init__(self, n1, n2, ks=3, stride=1):
        super().__init__()
        layers  = [Conv1D(n1, n2, ks=ks, stride=stride),
                   Conv1D(n2, n2, ks=ks, zero_bn=True, act=False)]
        self.convs = nn.Sequential(*layers)
        self.idconv = noop if n1==n2 else Conv1D(n1, n2, ks=1, act=False)
        self.pool = noop if stride==1 else nn.AvgPool1d(2, ceil_mode=True)
    def forward(self, x): return default_act(self.convs(x) + self.idconv(self.pool(x)))

class Resnet(nn.Module):
    def __init__(self, data, layers=[64, 64, 64], p=None):
        super(Resnet, self).__init__()
        sz = [int(e) for e in data.ds1[0][0].shape]
        n1, n2 = sz[0], 32
        net = [ResBlock2D(n1, n2, stride=2)]
        n1 = n2
        for n2 in layers:
            net += [ResBlock2D(n1, n2, stride=2)]
            n1 = n2
        net += [nn.AdaptiveMaxPool2d(1)]
        net += [Flatten()]
        net += [Linear(layers[-1], 1024, p=p)]
        net += [LinearFinal(1024, data.c, p=None)]
        self.net = nn.Sequential(*net)
        p = sum([p.numel() for p in self.parameters()])
        self.szs = get_cnn_szs(self, sz)
        print(f'\nResnet: params: {p:,.0f}, img_sz: {sz}, last_conv {self.szs[-1]}: ')

    def forward(self, x):
        return self.net(x)

# ####################################################################################################
# UNet 1D
# ####################################################################################################

class Encoder(nn.Module):
    def __init__(self, chs):
        super().__init__()
        self.enc_blocks = nn.ModuleList([ResBlock1D(chs[i], chs[i+1], ks=7) for i in range(len(chs)-1)])
        self.pool = nn.MaxPool1d(2)
    
    def forward(self, x):
        encs = []
        for block in self.enc_blocks:
            x = block(x)
            encs.append(x)
            x = self.pool(x)
        return encs

class Decoder(nn.Module):
    def __init__(self, chs):
        super().__init__()
        chs = chs[1::][::-1]
        self.chs = chs
        self.upconvs = nn.ModuleList([nn.ConvTranspose1d(chs[i], chs[i+1], 2, stride=2, padding=0) for i in range(len(chs)-1)])
        self.dec_blocks = nn.ModuleList([Conv1D(chs[i], chs[i+1], ks=5) for i in range(len(chs)-1)]) 
        
    def forward(self, x, encs):
        for i in range(len(self.chs)-1):
            x = self.upconvs[i](x)
            x2 = self.crop(encs[i], x)
            x = torch.cat([x, x2], dim=1)
            x = self.dec_blocks[i](x)
        return x
    
    def crop(self, encs, x):
        k = x.shape[2]
        return encs[:,:,:k]

class UNet1D(nn.Module):
    def __init__(self, chs, c, retain_dim=True, show=False):
        super().__init__()
        self.encoder = Encoder(chs)
        self.decoder = Decoder(chs)
        self.head = nn.Sequential(*[Conv1D(chs[1], c, ks=1), Conv1D(c, c, ks=1, zero_bn=True, act=False)])
        self.retain_dim  = retain_dim
        self.softmax = nn.LogSoftmax(dim=1)
        if show: model_stats(self)

    def forward(self, x):
        out_sz = x.shape[2]
        encs = self.encoder(x)
        x = self.decoder(encs[::-1][0], encs[::-1][1:])
        x = self.head(x)
        if self.retain_dim: x = torch.nn.functional.interpolate(x,out_sz)
        x = self.softmax(x)
        return x

################################################################################################################################
#  SignalNet
################################################################################################################################

class SignalNet(nn.Module):
    def __init__(self, ch, n, c, p=0., show=False):
        # super(SignalNet, self).__init__()
        super().__init__()
        n1,sz = ch,n
        n2 = min((n1+1)*8,64)
        net = []
        szs = [(n1,sz)]
        for _ in range(3):
            net += [Conv1D(n1, n2, stride=2)]
            n1, sz = n2, int(sz/2)
            szs += [(n1,sz)]
        bottle = int((int(math.log2(sz)))/2)
        for _ in range(bottle):
            net += [ResBlock1D(n1, n1*2, ks=3, stride=2)]
            n1, sz = n1*2, int(sz/2)
            szs += [(n1,sz)]
            net += [nn.MaxPool1d(2)]  # AvgPool1d, MaxPool1d
            sz = int(sz/2)
            szs += [(n1,sz)]
        net += [nn.AdaptiveMaxPool1d(1)]
        net += [Flatten()]
        net += [Linear(1*n1, 1024, p=p)]
        net += [LinearFinal(1024, c, p=None)]
        self.net = nn.Sequential(*net)
        if show: model_stats(self, bottle=bottle, szs=szs, show_szs=True)

    def forward(self, x): return self.net(x)

################################################################################################################################
#  TabularNet
################################################################################################################################

class TabularNet(nn.Module):
    def __init__(self, data, szs, emb_p, ps):
        super().__init__()
        self.ncats, self.nconts = data.ncats, data.nconts
        self.embs = nn.ModuleList([nn.Embedding(c, s) for c,s in data.emb_szs])
        self.nemb = sum(e.embedding_dim for e in self.embs)
        self.emb_drop = nn.Dropout(emb_p)
        self.bn_cont = nn.BatchNorm1d(data.nconts)
        szs = [self.nemb+data.nconts] + szs
        fcs = [Linear(szs[i], szs[i+1], p=ps[i]) for i in range(len(szs)-1)]
        out_sz = data.c if data.clsf else 1
        act_out = nn.LogSoftmax(dim=1) if data.clsf else Sigmoid()
        fcs += [LinearFinal(szs[-1], out_sz, act=act_out)]
        self.fcs = nn.Sequential(*fcs)
        init_net(self)
        np = sum([p.numel() for p in self.parameters()])
        i,c,e = data.ncats+data.nconts, len(data.emb_szs), self.nemb
        print(f'\nTabNet: {np:,d} params; {i:,d}->{i-c+e:,d} inputs; {c:,d}->{e:,d} embeds'.replace(',', '.'))

    def forward(self, x):
        x_cat, x_cont = x[:,:self.ncats].long(), x[:,self.ncats:].contiguous()
        if self.nemb!=0:
            x = [e(x_cat[:,i]) for i,e in enumerate(self.embs)]
            x = torch.cat(x, 1)
            x = self.emb_drop(x)
        if self.nconts!=0:
            # x_cont = self.bn_cont(x_cont)
            x = torch.cat([x, x_cont], 1) if self.nemb!=0 else x_cont
        x = self.fcs(x)
        return x

################################################################################################################################
#  Etc
################################################################################################################################

# x = torch.randn(1, 1, 250)
# l = ResBlock1D(1, 64)
# l(x).shape

# class ResBlock(nn.Module):
#     def __init__(self, expansion, ni, nh, stride=1):
#         super().__init__()
#         nf,ni = nh*expansion,ni*expansion
#         layers  = [conv_layer(ni, nh, 3, stride=stride),
#                    conv_layer(nh, nf, 3, zero_bn=True, act=False)
#         ] if expansion == 1 else [
#                    conv_layer(ni, nh, 1),
#                    conv_layer(nh, nh, 3, stride=stride),
#                    conv_layer(nh, nf, 1, zero_bn=True, act=False)
#         ]
#         self.convs = nn.Sequential(*layers)
#         self.idconv = noop if ni==nf else conv_layer(ni, nf, 1, act=False)
#         self.pool = noop if stride==1 else nn.AvgPool2d(2, ceil_mode=True)

#     def forward(self, x): return act_fn(self.convs(x) + self.idconv(self.pool(x)))


# class XResNet(nn.Sequential):
#     @classmethod
#     def create(cls, expansion, layers, c_in=3, c_out=1000):
#         nfs = [c_in, (c_in+1)*8, 64, 64]
#         stem = [conv_layer(nfs[i], nfs[i+1], stride=2 if i==0 else 1)
#             for i in range(3)]

#         nfs = [64//expansion,64,128,256,512]
#         res_layers = [cls._make_layer(expansion, nfs[i], nfs[i+1], n_blocks=l, stride=1 if i==0 else 2)
#                   for i,l in enumerate(layers)]
#         res = cls(
#             *stem,
#             nn.MaxPool2d(kernel_size=3, stride=2, padding=1),
#             *res_layers,
#             nn.AdaptiveAvgPool2d(1), Flatten(),
#             nn.Linear(nfs[-1]*expansion, c_out),
#         )
#         init_net(res)
#         return res

#     @staticmethod
#     def _make_layer(expansion, ni, nf, n_blocks, stride):
#         return nn.Sequential(
#             *[ResBlock(expansion, ni if i==0 else nf, nf, stride if i==0 else 1)
#               for i in range(n_blocks)])


# def xresnet18 (**kwargs): return XResNet.create(1, [2, 2,  2, 2], **kwargs)
# def xresnet34 (**kwargs): return XResNet.create(1, [3, 4,  6, 3], **kwargs)
# def xresnet50 (**kwargs): return XResNet.create(4, [3, 4,  6, 3], **kwargs)
# def xresnet101(**kwargs): return XResNet.create(4, [3, 4, 23, 3], **kwargs)
# def xresnet152(**kwargs): return XResNet.create(4, [3, 8, 36, 3], **kwargs)
