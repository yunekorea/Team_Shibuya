from random import random as rand

import numpy as np


def make_dataset():
    input_ids_ = np.load('sequence_crs.npy')
    segment_ids_ = np.load('segments_crs.npy')

    count = 30000
    max_q_length = 70

    input_ids = np.zeros(shape=[count, 12, input_ids_.shape[2]], dtype=np.int32)
    segment_ids = np.zeros(shape=[count, 12, input_ids_.shape[2]], dtype=np.int32)
    mask_ids = np.zeros(shape=[count, 12, input_ids_.shape[2]], dtype=np.int32)

    input_ids_q = np.zeros(shape=[count, max_q_length], dtype=np.int32)
    segment_ids_q = np.zeros(shape=[count, max_q_length], dtype=np.int32)
    mask_ids_q = np.zeros(shape=[count, max_q_length], dtype=np.int32)

    rank_label = np.zeros(shape=[count], dtype=np.int32)

    for i in range(count):
        rank_label[i] = 0
        r_ix = int(rand() * (input_ids_.shape[0] - 1))

        input_ids_q[i] = input_ids_[r_ix, 0][0:max_q_length]
        segment_ids_q[i] = segment_ids_[r_ix, 0][0:max_q_length]
        for j in range(max_q_length):
            if input_ids_q[i, j] != 0 or j == 0:
                mask_ids_q[i, j] = 1
            else:
                break

        input_ids[i, 0] = input_ids_[r_ix, 1]
        segment_ids[i, 0] = segment_ids_[r_ix, 1]
        for j in range(input_ids_.shape[2]):
            if input_ids[i, 0, j] != 0 or j == 0:
                mask_ids[i, 0, j] = 1
            else:
                break

        for k in range(11):
            r_ix = int(rand() * (input_ids_.shape[0] - 1))

            input_ids[i, k + 1] = input_ids_[r_ix, 1]
            segment_ids[i, k + 1] = segment_ids_[r_ix, 1]
            for j in range(input_ids_.shape[2]):
                if input_ids[i, k + 1, j] != 0 or j == 0:
                    mask_ids[i, k + 1, j] = 1
                else:
                    break

    np.save('input_ids_q', input_ids_q)
    np.save('segment_ids_q', segment_ids_q)
    np.save('mask_ids_q', mask_ids_q)

    np.save('input_ids', input_ids)
    np.save('segment_ids', segment_ids)
    np.save('mask_ids', mask_ids)
    np.save('rank_label', rank_label)


def make_dataset2():
    input_ids_ = np.load('sequence_crs_dev.npy')
    segment_ids_ = np.load('segments_crs_dev.npy')

    count = input_ids_.shape[0]
    max_q_length = 70

    input_ids = np.zeros(shape=[count, 12, input_ids_.shape[2]], dtype=np.int32)
    segment_ids = np.zeros(shape=[count, 12, input_ids_.shape[2]], dtype=np.int32)
    mask_ids = np.zeros(shape=[count, 12, input_ids_.shape[2]], dtype=np.int32)

    input_ids_q = np.zeros(shape=[count, max_q_length], dtype=np.int32)
    segment_ids_q = np.zeros(shape=[count, max_q_length], dtype=np.int32)
    mask_ids_q = np.zeros(shape=[count, max_q_length], dtype=np.int32)

    rank_label = np.zeros(shape=[count], dtype=np.int32)

    for i in range(count):
        rank_label[i] = 0
        r_ix = int(rand() * (input_ids_.shape[0] - 1))

        input_ids_q[i] = input_ids_[r_ix, 0][0:max_q_length]
        segment_ids_q[i] = segment_ids_[r_ix, 0][0:max_q_length]
        for j in range(max_q_length):
            if input_ids_q[i, j] != 0 or j == 0:
                mask_ids_q[i, j] = 1
            else:
                break

        input_ids[i, 0] = input_ids_[r_ix, 1]
        segment_ids[i, 0] = segment_ids_[r_ix, 1]
        for j in range(input_ids_.shape[2]):
            if input_ids[i, 0, j] != 0 or j == 0:
                mask_ids[i, 0, j] = 1
            else:
                break

        for k in range(11):
            r_ix = int(rand() * (input_ids_.shape[0] - 1))

            input_ids[i, k + 1] = input_ids_[r_ix, 1]
            segment_ids[i, k + 1] = segment_ids_[r_ix, 1]
            for j in range(input_ids_.shape[2]):
                if input_ids[i, k + 1, j] != 0 or j == 0:
                    mask_ids[i, k + 1, j] = 1
                else:
                    break

        for k in range(12):
            print(mask_ids[i, k])
            print(segment_ids[i, k])
            print('-------------')
        input()

    np.save('input_ids_q_dev', input_ids_q)
    np.save('segment_ids_q_dev', segment_ids_q)
    np.save('mask_ids_q_dev', mask_ids_q)

    np.save('input_ids_dev', input_ids)
    np.save('segment_ids_dev', segment_ids)
    np.save('mask_ids_dev', mask_ids)



