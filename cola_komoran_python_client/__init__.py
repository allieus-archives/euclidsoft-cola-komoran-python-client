#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ray
from enum import Enum
from tqdm.auto import tqdm
from grpc import insecure_channel
from textrank import KeywordSummarizer

from .kr.re.keit.Komoran_pb2_grpc import KomoranStub
from .kr.re.keit.Komoran_pb2 import TokenizeRequest
from .U_dripwordFinder import (CompoundRegex, term1_remove_sql_exp)


class DicType(Enum):
    DEFAULT = 0
    OVERALL = 1
    MINIMAL = 2


TARGET_DEFAULT = 'localhost:50051'
WINDOW_DEFAULT = -1
MIN_COUNT_DEFAULT = 1
VERBOSE_DEFAULT = False
TOPK_DEFAULT = 10
DIC_TYPE_DEFAULT = DicType.DEFAULT


term1_regex = CompoundRegex(term1_remove_sql_exp)


def to_iterator(obj_ids):
    while obj_ids:
        done, obj_ids = ray.wait(obj_ids)
        for obj_id in done:
            yield ray.get(obj_id)


class GrpcTokenizer:
    def __init__(self, target, dic_type=DicType.DEFAULT):
        channel = insecure_channel(target)
        self.stub = KomoranStub(channel)
        if isinstance(dic_type, DicType):
            self.dic_type = dic_type.value
        else:
            self.dic_type = dic_type

    def __call__(self, sentence):
        request = TokenizeRequest(dicType=self.dic_type, sentence=sentence)
        response = self.stub.tokenize(request)
        keyword_list = list(response.keyword)
        return keyword_list


def summarize_without_ray(sentence_list, target=TARGET_DEFAULT, window=WINDOW_DEFAULT,
                          verbose=VERBOSE_DEFAULT, topk=TOPK_DEFAULT, dic_type=DIC_TYPE_DEFAULT,
                          min_count=MIN_COUNT_DEFAULT):
    tokenize = GrpcTokenizer(target, dic_type=dic_type)
    summarizer = KeywordSummarizer(
        tokenize=tokenize,
        window=window,
        min_count=min_count,
        verbose=verbose,
    )
    try:
        keyword_list = summarizer.summarize(sentence_list, topk=topk)
    except ValueError:
        return []

    # term1_regex 필터링 적용
    return [
        (word, rank)
        for (word, rank) in keyword_list
        if not term1_regex.remove(word)
    ]


@ray.remote
def summarize(sentence_list, target, window, verbose, topk, dic_type, min_count):
    return summarize_without_ray(sentence_list, target, window, verbose, topk, dic_type, min_count)


def summarize_batch_with_ray(sentence_list_series, with_tqdm=True,
                             target=TARGET_DEFAULT, window=WINDOW_DEFAULT, verbose=VERBOSE_DEFAULT,
                             topk=TOPK_DEFAULT, dic_type=DIC_TYPE_DEFAULT, min_count=MIN_COUNT_DEFAULT):
    obj_ids = [
        summarize.remote(sentence_list, target=target, window=window, verbose=verbose, topk=topk,
                         dic_type=dic_type, min_count=min_count)
        for sentence_list in sentence_list_series
    ]
    if with_tqdm:
        return list(tqdm(to_iterator(obj_ids), total=len(obj_ids)))
    else:
        return ray.get(obj_ids)


def ray_init(address="auto"):
    ray.init(address=address)


def ray_shutdown():
    ray.shutdown()


__all__ = ["summarize_batch_with_ray", "ray_init", "ray_shutdown"]

