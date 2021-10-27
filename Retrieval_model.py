# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import math
import torch
import torch.nn as nn

from torch.nn import CrossEntropyLoss, Dropout, Embedding, Softmax, MSELoss

from transformers import AutoModel

logger = logging.getLogger(__name__)

LayerNorm = nn.LayerNorm


def Linear(i_dim, o_dim, bias=True):
    m = nn.Linear(i_dim, o_dim, bias)
    nn.init.normal_(m.weight, std=0.02)
    if bias:
        nn.init.constant_(m.bias, 0.)
    return m


def gelu(x):
    """ Implementation of the gelu activation function currently in Google Bert repo (identical to OpenAI GPT).
        Also see https://arxiv.org/abs/1606.08415
    """
    return 0.5 * x * (1 + torch.tanh(math.sqrt(2 / math.pi) * (x + 0.044715 * torch.pow(x, 3))))


def swish(x):
    return x * torch.sigmoid(x)


class QuestionAnswering(nn.Module):
    def __init__(self):
        super(QuestionAnswering, self).__init__()
        self.bert = AutoModel.from_pretrained("monologg/koelectra-base-v3-discriminator")
        self.bert_q = AutoModel.from_pretrained("monologg/koelectra-base-v3-discriminator")

        # TODO check with Google if it's normal there is no dropout on the token classifier of SQuAD in the TF version
        # self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.hidden_layer_p = Linear(768, 768)
        self.hidden_layer_q = Linear(768, 768)

        self.dropout = Dropout(0.2)

        self.sigmoid = torch.nn.Sigmoid()
        self.softmax = torch.nn.Softmax(dim=1)

    def forward(self, input_ids, token_type_ids=None, attention_mask=None,
                input_ids_q=None, token_type_ids_q=None, attention_mask_q=None,
                rank_label=None, doc_num=12):

        input_ids = torch.reshape(input_ids, shape=[-1, 350])
        token_type_ids = torch.reshape(token_type_ids, shape=[-1, 350])
        attention_mask = torch.reshape(attention_mask, shape=[-1, 350])

        outputs = self.bert.forward(input_ids=input_ids,
                                    token_type_ids=token_type_ids,
                                    attention_mask=attention_mask,
                                    )
        sequence_output = outputs.last_hidden_state[:, 0, :]
        sequence_output = self.hidden_layer_p(sequence_output)
        sequence_output = torch.reshape(sequence_output, shape=[-1, doc_num, 768])

        outputs = self.bert_q.forward(input_ids=input_ids_q,
                                      token_type_ids=token_type_ids_q,
                                      attention_mask=attention_mask_q,
                                    )
        sequence_output_q = outputs.last_hidden_state[:, 0, :]
        sequence_output_q = self.hidden_layer_q(sequence_output_q)
        sequence_output_q = torch.unsqueeze(sequence_output_q, dim=-1)


        logits = torch.bmm(sequence_output, sequence_output_q)
        logits = torch.squeeze(logits, dim=-1)

        if rank_label is not None:
            loss_fct = CrossEntropyLoss()
            total_loss = loss_fct(logits, rank_label)
            return total_loss
        else:
            return logits
