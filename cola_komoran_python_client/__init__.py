#!/usr/bin/env python
# -*- coding: utf-8 -*-

# tqdm
# https://github.com/lovit/textrank/archive/master.zip
# grpcio

import ray
from tqdm.auto import tqdm
from grpc import insecure_channel
from kr.re.keit.Komoran_pb2_grpc import KomoranStub
from kr.re.keit.Komoran_pb2 import TokenizeRequest
from textrank import KeywordSummarizer


def to_iterator(obj_ids):
    while obj_ids:
        done, obj_ids = ray.wait(obj_ids)
        yield ray.get(done[0])

class GrpcTokenizer:
    def __init__(self, target):
        channel = insecure_channel(target)
        self.stub = KomoranStub(channel)

    def __call__(self, sentence):
        request = TokenizeRequest(sentence=sentence)
        response = self.stub.tokenize(request)
        keyword_list = response.keyword
        return keyword_list


@ray.remote
def summarize(sentence_list, target='localhost:50051', window=-1, verbose=False, topk=10):
    tokenize = GrpcTokenizer(target)
    summarizer = KeywordSummarizer(
        tokenize = tokenize,
        window = window,
        verbose = verbose,
    )
    try:
        return summarizer.summarize(sentence_list, topk=topk)
    except ValueError:
        return []


def ray_init():
    ray.init(address="auto")


def ray_shutdown():
    ray.shutdown()


def summarize_batch_with_ray(sentence_list_series, with_tqdm=True):
    obj_ids = [
        summarize.remote(sentence_list)
        for sentence_list in sentence_list_series
    ]
    if with_tqdm:
        return list(tqdm(to_iterator(obj_ids), total=len(obj_ids)))
    else:
        return ray.get(obj_ids)


__call__ = ["ray_init", "ray_shutdown", "summarize_batch_with_ray"]

