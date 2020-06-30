#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ray
from enum import Enum
from tqdm.auto import tqdm
from grpc import insecure_channel
from .kr.re.keit.Komoran_pb2_grpc import KomoranStub
from .kr.re.keit.Komoran_pb2 import TokenizeRequest
from textrank import KeywordSummarizer


class DicType(Enum):
    DEFAULT = 0
    OVERALL = 1
    MINIMAL = 2


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


@ray.remote
def summarize(sentence_list, target, window, verbose, topk, dic_type):
    tokenize = GrpcTokenizer(target, dic_type=dic_type)
    summarizer = KeywordSummarizer(
        tokenize = tokenize,
        window = window,
        verbose = verbose,
    )
    try:
        return summarizer.summarize(sentence_list, topk=topk)
    except ValueError:
        return []


def summarize_batch_with_ray(sentence_list_series, with_tqdm=True,
                             target='localhost:50051', window=-1, verbose=False, topk=10,
                             dic_type=DicType.DEFAULT):
    obj_ids = [
        summarize.remote(sentence_list, target=target, window=window, verbose=verbose, topk=topk,
                         dic_type=dic_type)
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

