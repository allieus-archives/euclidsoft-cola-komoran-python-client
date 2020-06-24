#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ray
from tqdm.auto import tqdm
from grpc import insecure_channel
from .kr.re.keit.Komoran_pb2_grpc import KomoranStub
from .kr.re.keit.Komoran_pb2 import TokenizeRequest
from textrank import KeywordSummarizer


def to_iterator(obj_ids):
    while obj_ids:
        done, obj_ids = ray.wait(obj_ids)
        for obj_id in done:
            yield ray.get(obj_id)


class GrpcTokenizer:
    def __init__(self, target, dic_type=0):
        channel = insecure_channel(target)
        self.stub = KomoranStub(channel)
        self.dic_type = dic_type

    def __call__(self, sentence):
        request = TokenizeRequest(dicType=self.dic_type, sentence=sentence)
        response = self.stub.tokenize(request)
        keyword_list = response.keyword
        return keyword_list


def ray_init(address="auto"):
    ray.init(address=address)


def ray_shutdown():
    ray.shutdown()


def summarize_batch_with_ray(sentence_list_series, dic_type=0, target='localhost:50051', verbose=False, with_tqdm=True):
    obj_ids = [
        summarize.remote(sentence_list, target=target, verbose=verbose, dic_type=dic_type)
        for sentence_list in sentence_list_series
    ]
    if with_tqdm:
        return list(tqdm(to_iterator(obj_ids), total=len(obj_ids)))
    else:
        return ray.get(obj_ids)


@ray.remote
def summarize(sentence_list, target, verbose, dic_type=0):
    tokenize = GrpcTokenizer(target, dic_type)
    summarizer = KeywordSummarizer(
        tokenize = tokenize,
        window = -1,
        verbose = verbose,
    )
    try:
        return summarizer.summarize(sentence_list, topk=10)
    except ValueError:
        return []


__call__ = ["ray_init", "ray_shutdown", "summarize_batch_with_ray"]

