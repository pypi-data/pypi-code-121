import torch
import torch.nn as nn
import math
import copy


def swish(x):
    return x * torch.sigmoid(x)


ACT2FN = {
    "gelu": torch.nn.functional.gelu,
    "relu": torch.nn.functional.relu,
    "swish": swish,
}


class Attention(nn.Module):
    def __init__(self, hidden_size, attention_head_num, dropout, vis=False):
        super().__init__()
        self.vis = vis
        self.attention_head_num = attention_head_num
        self.attention_head_size = int(hidden_size / self.attention_head_num)
        self.all_head_size = self.attention_head_num * self.attention_head_size

        self.query = nn.Linear(hidden_size, self.all_head_size)
        self.key = nn.Linear(hidden_size, self.all_head_size)
        self.value = nn.Linear(hidden_size, self.all_head_size)

        self.out = nn.Linear(hidden_size, hidden_size)
        self.attn_dropout = nn.Dropout(dropout)
        self.proj_dropout = nn.Dropout(dropout)

        self.softmax = nn.Softmax(dim=-1)

    def transpose_for_scores(self, x):
        new_x_shape = x.size()[:-1] + (
            self.attention_head_num,
            self.attention_head_size,
        )
        x = x.view(*new_x_shape)
        return x.permute(0, 2, 1, 3)

    def forward(self, hidden_states, attn_embedding=None):
        """attn_embedding: [1,Head,N,N]"""
        mixed_query_layer = self.query(hidden_states)
        mixed_key_layer = self.key(hidden_states)
        mixed_value_layer = self.value(hidden_states)

        query_layer = self.transpose_for_scores(mixed_query_layer)
        key_layer = self.transpose_for_scores(mixed_key_layer)
        value_layer = self.transpose_for_scores(mixed_value_layer)
        attention_scores = torch.matmul(query_layer, key_layer.transpose(-1, -2))
        attention_scores = attention_scores / math.sqrt(self.attention_head_size)
        if attn_embedding is not None:
            attention_scores = attention_scores + attn_embedding
        attention_probs = self.softmax(attention_scores)
        weights = attention_probs if self.vis else None
        attention_probs = self.attn_dropout(attention_probs)

        context_layer = torch.matmul(attention_probs, value_layer)
        context_layer = context_layer.permute(0, 2, 1, 3).contiguous()
        new_context_layer_shape = context_layer.size()[:-2] + (self.all_head_size,)
        context_layer = context_layer.view(*new_context_layer_shape)
        attention_output = self.out(context_layer)
        attention_output = self.proj_dropout(attention_output)
        return attention_output, weights


class Mlp(nn.Module):
    def __init__(self, hidden_size, dropout, mlp_dim):
        super(Mlp, self).__init__()
        self.fc1 = nn.Linear(hidden_size, mlp_dim)
        self.fc2 = nn.Linear(mlp_dim, hidden_size)
        self.act_fn = ACT2FN["gelu"]
        self.dropout = nn.Dropout(dropout)

        self._init_weights()

    def _init_weights(self):
        nn.init.xavier_uniform_(self.fc1.weight)
        nn.init.xavier_uniform_(self.fc2.weight)
        nn.init.normal_(self.fc1.bias, std=1e-6)
        nn.init.normal_(self.fc2.bias, std=1e-6)

    def forward(self, x):
        x = self.fc1(x)
        x = self.act_fn(x)
        x = self.dropout(x)
        x = self.fc2(x)
        x = self.dropout(x)
        return x


class Block(nn.Module):
    def __init__(
        self,
        hidden_size,
        mlp_dropout,
        attention_head_num,
        attention_dropout,
        vis=False,
        mlp_ratio=4,
    ):
        super(Block, self).__init__()
        self.hidden_size = hidden_size
        self.attention_norm = nn.LayerNorm(hidden_size, eps=1e-6)
        self.ffn_norm = nn.LayerNorm(hidden_size, eps=1e-6)
        self.ffn = Mlp(hidden_size, mlp_dropout, int(hidden_size * mlp_ratio))
        self.attn = Attention(hidden_size, attention_head_num, attention_dropout, vis)

    def forward(self, x, attn_embedding=None):
        h = x
        x = self.attention_norm(x)
        x, weights = self.attn(x, attn_embedding)
        x = x + h

        h = x
        x = self.ffn_norm(x)
        x = self.ffn(x)
        x = x + h
        return x, weights


class Encoder(nn.Module):
    def __init__(
        self,
        hidden_size,
        num_layers,
        mlp_dropout,
        attention_head_num,
        attention_dropout,
        mlp_ratio=4,
        vis=False,
    ):
        super().__init__()

        self.vis = vis
        self.layer = nn.ModuleList()
        self.encoder_norm = nn.LayerNorm(hidden_size, eps=1e-6)
        for _ in range(num_layers):
            layer = Block(
                hidden_size=hidden_size,
                mlp_dropout=mlp_dropout,
                attention_head_num=attention_head_num,
                attention_dropout=attention_dropout,
                vis=vis,
                mlp_ratio=mlp_ratio,
            )
            self.layer.append(copy.deepcopy(layer))

    def forward(self, hidden_states, attn_embedding=None):
        """attn_embedding: [1,Head,N,N]"""
        attn_weights = []
        for layer_block in self.layer:
            hidden_states, weights = layer_block(hidden_states, attn_embedding)
            if self.vis:
                attn_weights.append(weights)

        encoded = self.encoder_norm(hidden_states)
        return encoded, attn_weights
