# coding=utf-8
from torch.utils.data import (RandomSampler, TensorDataset)
from transformers import RobertaForMaskedLM, RobertaConfig
from optimization import AdamW, WarmupLinearSchedule

import logging
import os
import random
import sys

import numpy as np
import torch

from torch.utils.data import (DataLoader, SequentialSampler, TensorDataset)
from tqdm import tqdm

from make_input import make_dataset
from make_npysave import make_AIhub_Book, make_AIhub, make_KorQuad, make_ALLdataset

import Retrieval_model

abs_path = os.path.dirname(os.path.abspath(__file__))
abs_path = str(abs_path[0: len(abs_path) - 1])

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CHK_PATH = os.path.join(abs_path, "korquad_final2.bin")
CONFIG_PATH = os.path.join(abs_path, "bert_small.json")
VOCAB_PATH = os.path.join(abs_path, "ko_vocab_32k.txt")
# CONFIG_PATH = os.path.join(MODEL_PATH, "bert_small.json")
# VOCAB_PATH = os.path.join(MODEL_PATH, "ko_vocab_32k.txt")

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

max_grad_norm = 1.0


def main():
    seed = 30
    fp16 = False

    print(torch.cuda.is_available())
    # input()

    # have to change when this code submitted
    # device = torch.device("cpu")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    n_gpu = torch.cuda.device_count()
    logger.info("device: {} n_gpu: {}".format(device, n_gpu))

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if n_gpu > 0:
        torch.cuda.manual_seed_all(seed)

    # Prepare model
    model = Retrieval_model.QuestionAnswering()

    # Prepare optimizer
    param_optimizer = list(model.named_parameters())
    no_decay = ['bias', 'LayerNorm.weight']
    optimizer_grouped_parameters = [
        {'params': [p for n, p in param_optimizer if not any(nd in n for nd in no_decay)],
         'weight_decay': 0.01},
        {'params': [p for n, p in param_optimizer if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
    ]

    train_batch_size = 1
    num_train_epochs = 2
    num_data_size = 30000

    num_train_optimization_steps = int(num_data_size /
                                       train_batch_size) * num_train_epochs

    optimizer = AdamW(optimizer_grouped_parameters,
                      lr=5e-5,
                      eps=1e-6)
    scheduler = WarmupLinearSchedule(optimizer,
                                     warmup_steps=num_train_optimization_steps * 0.1,
                                     t_total=num_train_optimization_steps)

    #model.load_state_dict(torch.load("retrieval_model.bin", map_location=device))
    model.to(device)
    model = torch.nn.DataParallel(model)
    logger.info("***** Running training *****")

    model.train()
    global_step = 0
    epoch = 0
    for ep in range(20):
        make_dataset()

        input_ids = np.load('input_ids.npy')
        input_mask = np.load('mask_ids.npy')
        input_segments = np.load('segment_ids.npy')

        input_ids_q = np.load('input_ids_q.npy')
        input_mask_q = np.load('mask_ids_q.npy')
        input_segments_q = np.load('segment_ids_q.npy')

        rank_label = np.load('rank_label.npy')

        seq_length = input_ids.shape[2]
        q_length = 50

        all_input_ids_q = torch.from_numpy(input_ids_q).type(torch.LongTensor)
        all_input_mask_q = torch.from_numpy(input_mask_q).type(torch.LongTensor)
        all_input_segments_q = torch.from_numpy(input_segments_q).type(torch.LongTensor)

        all_input_ids = torch.from_numpy(input_ids).type(torch.LongTensor)
        all_input_mask = torch.from_numpy(input_mask).type(torch.LongTensor)
        all_input_segments = torch.from_numpy(input_segments).type(torch.LongTensor)
        all_rank_label = torch.from_numpy(rank_label).type(torch.LongTensor)

        train_data = TensorDataset(all_input_ids, all_input_mask, all_input_segments,
                                   all_input_ids_q, all_input_mask_q, all_input_segments_q
                                   , all_rank_label)

        train_sampler = RandomSampler(train_data)
        train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=train_batch_size)

        iter_bar = tqdm(train_dataloader, desc="Train(XX Epoch) Step(XX/XX) (Mean loss=X.X) (loss=X.X)")
        tr_step, total_loss, mean_loss = 0, 0., 0.

        ce = torch.nn.CrossEntropyLoss()

        for step, batch in enumerate(iter_bar):
            input_ids, input_mask, input_segments, input_ids_q, input_mask_q, input_segments_q, rank_label = batch
            """
            input_ids = torch.reshape(input_ids, shape=[-1, seq_length])
            input_mask = torch.reshape(input_mask, shape=[-1, seq_length])
            input_segments = torch.reshape(input_segments, shape=[-1, seq_length])

            input_ids_q = torch.reshape(input_ids_q, shape=[-1, q_length])
            input_mask_q = torch.reshape(input_mask_q, shape=[-1, q_length])
            input_segments_q = torch.reshape(input_segments_q, shape=[-1, q_length])

            rank_label = torch.reshape(rank_label, shape=[-1])
            """
            loss = model(
                input_ids=input_ids,
                attention_mask=input_mask,
                token_type_ids=input_segments,
                input_ids_q=input_ids_q,
                attention_mask_q=input_mask_q,
                token_type_ids_q=input_segments_q,
                rank_label=rank_label,
                doc_num=12,
            )
            #loss = loss.mean()
            logits = model(
                input_ids=input_ids,
                attention_mask=input_mask,
                token_type_ids=input_segments,
                input_ids_q=input_ids_q,
                attention_mask_q=input_mask_q,
                token_type_ids_q=input_segments_q,
                rank_label=None,
                doc_num=12,
            )
            loss = ce(logits.to(device), rank_label.to(device))

            #print(logits)
            print(loss, torch.nn.CrossEntropyLoss()(logits.to(device), rank_label.to(device)))

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)

            scheduler.step()
            optimizer.step()
            optimizer.zero_grad()

            global_step += 1
            tr_step += 1
            total_loss += loss.data
            mean_loss = total_loss / tr_step
            iter_bar.set_description("Train Step(%d / %d) (Mean loss=%5.5f) (loss=%5.5f)" %
                                     (global_step, num_train_optimization_steps, mean_loss, loss.item()))

        logger.info("** ** * Saving file * ** **")
        model_checkpoint = "qa_model.bin"
        logger.info(model_checkpoint)
        output_model_file = os.path.join('C:\\Users\\CHKIM\\Desktop\\ret', model_checkpoint)
        if n_gpu > 1:
            torch.save(model.module.state_dict(), output_model_file)
        else:
            torch.save(model.state_dict(), output_model_file)
        epoch += 1


if __name__ == "__main__":
    main()
