import os
import grpc
from concurrent import futures
from cola_komoran_python_client.kr.re.keit.Komoran_pb2 import TokenizeResponse
from cola_komoran_python_client.kr.re.keit.Komoran_pb2_grpc import KomoranServicer, add_KomoranServicer_to_server


class MyServicerExample(KomoranServicer):
    def tokenize(self, request, context):
        response = TokenizeResponse(keyword=["키워드1", "키워드2", "키워드3", "키워드4"])
        return response


def serve(port=50051):
    # 파이썬 3.5에서 변경: max_workers 가 None 이거나 주어지지 않았다면, 기본값으로 기계의 프로세서 수에 5 를 곱한 값을 사용
    # 파이썬 3.8에서 변경: max_workers의 기본값은 min(32, os.cpu_count() + 4)로 변경
    max_workers = (min(32, os.cpu_count() + 4)) // 2
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    add_KomoranServicer_to_server(MyServicerExample(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print("Started ...")
    server.wait_for_termination()
