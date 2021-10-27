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

import Retrieval_model

from transformers import AutoTokenizer, RobertaTokenizer


tokenizer = AutoTokenizer.from_pretrained("klue/roberta-base")

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


def get_batch(question, documents):
    max_length = 350
    query_length = 50

    input_ids_q = np.zeros(shape=[len(documents), query_length], dtype=np.long)
    mask_ids_q = np.zeros(shape=[len(documents), query_length], dtype=np.long)
    segments_ids_q = np.zeros(shape=[len(documents), query_length], dtype=np.long)

    input_ids = np.zeros(shape=[len(documents), max_length], dtype=np.long)
    mask_ids = np.zeros(shape=[len(documents), max_length], dtype=np.long)
    segments_ids = np.zeros(shape=[len(documents), max_length], dtype=np.long)

    query_tokens = tokenizer.tokenize(question)
    query_tokens.insert(0, '[CLS]')

    for i, document in enumerate(documents):
        ids = tokenizer.convert_tokens_to_ids(query_tokens)
        for j in range(len(ids)):
            input_ids_q[i, j] = ids[j]
            mask_ids_q[i, j] = 1
            segments_ids_q[i, j] = 1

        tokens = tokenizer.tokenize(document)
        tokens.insert(0, '[CLS]')
        ids = tokenizer.convert_tokens_to_ids(tokens)

        for j in range(len(ids)):
            input_ids[i, j] = ids[j]
            mask_ids[i, j] = 1
            segments_ids[i, j] = 1

    return input_ids, mask_ids, segments_ids, input_ids_q, mask_ids_q, segments_ids_q


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

    print('restore model...')
    state_dict = torch.load('ret.bin')
    # create new OrderedDict that does not contain `module.`
    from collections import OrderedDict
    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        name = k[7:]  # remove `module.`
        new_state_dict[name] = v
    # load params
    model.load_state_dict(new_state_dict)

    model.to(device)
    model = torch.nn.DataParallel(model)
    logger.info("***** Running training *****")

    model.eval()

    question = '정형돈의 복귀는 언제인가?'

    documents = [
        '소니의 성공을 점치는 사람은 아무도 없었지만 뛰어난 하드웨어, 영리한 마케팅과 함께 개발자와 서드파티 발굴을 위한 노력, CD의 채택, 닌텐도 64와 세가 새턴의 실수 등에 힘입어 피터지게 경쟁했지만 승리는 시장에 처음 데뷔한 신인의 몫이 되었다. ',
        '일본의 엔터테인먼트 기업 중에서 가장 대중적으로 인지도가 높은 기업이며 비디오 게임 산업의 초창기인 1970년대부터 현재까지 명맥을 유지하고 있는, 그것도 이런 시대에 여전히 독자적인 플랫폼 비즈니스로 순수 게임 산업 시가총액 2위에 앉아 있는 기업이다.',
        '크게 반도체, LCD, 휴대폰, 가전 부문으로 사업부가 나뉘었으나 2008년부터 2009년까지 불어닥친 글로벌 경제 위기에 대응해 반도체와 LCD로 대표되는 부품 부문과 TV와 휴대폰, 냉장고로 대표되는 완제품 부문으로 사업부를 통합했다. 분야가 완전히 달랐던 삼성테크윈의 디지털 카메라 부문과 삼성SDI의 플래시 메모리, 낸드플래시도 통합되었고 그 외 삼성전기 LED 사업부도 통합되었다.',
        '코미디언 출신 MC, 방송인이며 대한민국의 국민 MC이다. 1991년 KBS 공채 개그맨 7기[28]로 데뷔했다. 대한민국 방송계 역사에 전무후무한 17회 대상 수상[29]을 기록했으며 국민MC라는 별명으로 전 국민적인 인기를 누리고 있다.',
        '1회에서 정형돈 본인이 언급했듯이 완전 복귀는 아닌것으로 보인다. 공식 홈페이지에서도 뭉뜬 4인방 중 정형돈만 빠져있으며, 6회부턴 출연을 안하고 있다. 또한 선수 이야기에서 정형돈을 제외하고 인원 카운트 이야기를 하는 것보면 소속 선수로 취급되지 않는 것이 보인다.',
        '부정적인 상념이 어둠의 힘에 의해 모여서 출현한 수수께끼의 디지몬. 그 정체를 아는 자는 아무도 없고, 이 물체가 디지몬인지도 해석할 수 없다. 그 출현 이유는 확실치 않지만 혼란한 사이버 세계(디지털 월드)를 숙청하고 "무"로 돌아가려 한다고 생각된다. 일설에는 태고의 예언서에서 아포카리몬의 출현을 예언하고 있다는 것이 알려져 있다.',
        '소니의 성공을 점치는 사람은 아무도 없었지만 뛰어난 하드웨어, 영리한 마케팅과 함께 개발자'
    ]

    input_ids, input_mask, input_segments, input_ids_q, input_mask_q, input_segments_q = get_batch(
        question=question,
        documents=documents
    )

    print(input_ids[0][0:70])
    print(input_mask[0][0:70])
    print(input_segments[0][0:70])
    print()
    print(input_ids[1][0:70])
    print(input_mask[1][0:70])
    print(input_segments[1][0:70])

    input_ids = torch.from_numpy(input_ids).type(torch.long)
    input_mask = torch.from_numpy(input_mask).type(torch.long)
    input_segments = torch.from_numpy(input_segments).type(torch.long)

    input_ids_q = torch.from_numpy(input_ids_q).type(torch.long)
    input_mask_q = torch.from_numpy(input_mask_q).type(torch.long)
    input_segments_q = torch.from_numpy(input_segments_q).type(torch.long)

    logits = model(
        input_ids=input_ids,
        attention_mask=input_mask,
        token_type_ids=input_segments,
        input_ids_q=input_ids_q,
        attention_mask_q=input_mask_q,
        token_type_ids_q=input_segments_q,
        rank_label=None,
    )

    print(logits)

if __name__ == "__main__":
    main()
