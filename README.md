# cola-komoran-python-client

## 주의

라이브러리를 업데이트되면, ray.remote 객체 재생성을 위해 ray cluster stop/start가 필요할 수도 있습니다.

Ray는 Remote함수와 의존성있는 함수를 한꺼번에 직렬화하여 Ray Cluster상에 저장을 합니다. 의존성있는 함수가 변경되었음에도Ray Cluster상에 직렬화된 함수가 업데이트되지 않을 수 있습니다. 이때 ray cluster stop/start를 통해 초기화를 해볼 수 있겠습니다.

```sh
ray stop
ray start --head --num-cpus 36 --num-gpus 1
```

## 라이브러리 설치

```sh
pip install https://github.com/euclidsoft/cola-komoran-python-client/archive/master.zip
```

## ray를 활용한 bulk 호출 샘플 코드

```python
from cola_komoran_python_client import ray_init, ray_shutdown, summarize_batch_with_ray, DicType

ray_init()  # 처음 1회만 수행해주세요.

# ray를 활용한 summarize 수행합니다. tqdm은 내부적으로 수행됩니다.
# tqdm을 수행하지 않으려면 with_tqdm=False 인자를 지정해주세요.
keyword_list = summarize_batch_with_ray(sentence_list_series, dic_type=DicType.DEFAULT)

keyword_list = summarize_batch_with_ray(sentence_list_series, dic_type=DicType.OVERALL)

keyword_list = summarize_batch_with_ray(sentence_list_series, dic_type=DicType.MINIMAL)

ray_shutdown()  # 모든 작업이 끝내거나, ray cluster를 초기화시키고자 할 때
```

## 단일 호출 샘플 코드

### GrpcTokenizer 예시

```python
from grpc import insecure_channel
from cola_komoran_python_client import DicType
from cola_komoran_python_client.kr.re.keit.Komoran_pb2_grpc import KomoranStub
from cola_komoran_python_client.kr.re.keit.Komoran_pb2 import TokenizeRequest

class GrpcTokenizer:
    def __init__(self, target, dic_type=DicType.DEFAULT):
        channel = insecure_channel(target)
        self.stub = KomoranStub(channel)
        self.dic_type = dic_type

    def __call__(self, sentence):
        request = TokenizeRequest(dicType=self.dic_type, sentence=sentence)
        response = self.stub.tokenize(request)
        keyword_list = response.keyword
        return keyword_list
```

```python
sentence = """
    워크에 대해 권선 동작을 수행하기 위한 방법 및 그 장치가 개시되는데,
    클램프에 의해 그 단부가 파지 되는 와이어는 훅의 의해 걸리고(hooked),
    상기 걸려진 와이어는 워크에 제공된 구멍으로 삽입되며, 그 다음 클램프는
    와이어가 훅을 끌어 당길 때 훅과는 반대 위치로 이동되고, 와이어의 단부를
    파지하는 클램프는 워크에 대해 선회되어 워크에 와이어를 감는다. 따라서,
    상기 구멍의 에지와 와이어 사이의 접 촉 압력은 제거된다.
"""
tokenize = GrpcTokenizer("localhost:50051")
print(tokenize(sentence))
# ['워크', '대해', '권선', '동작', '수행', '하기', '위한', '방법', '장치가', '개시', '클램프', '의해', '단부', '파지', '와이어', '훅', '의해', '걸리', '상기', '와이어', '워크', '제공', '구멍', '삽입', '다음', '클램프', '와이어', '당기', '훅', '반대', '위치', '이동', '와이어', '단부', '파지', '클램프', '워크', '대해', '선회', '워크', '와이어', '상기', '구멍', '에지', '와 와', '이어', '사이', '접', '압력', '제거']
```

### textrank의 KeywordSummarizer 활용하기

```python
from cola_komoran_python_client import GrpcTokenizer, KeywordSummarizer, DicType

tokenize = GrpcTokenizer("localhost:50051", dic_type=DicType.DEFAULT)
summarizer = KeywordSummarizer(
    tokenize = tokenize,
    window = -1,
    verbose = False,
)

sentence_list = [
    '조미료 제조시에 부산물로 얻어지는 발효 폐액과 인산암모니움염의 혼합 현탁액을 이용하여 분말형 용성인비를 조립할 수 있게 한다.분말 용성인비 80-95부에 조미료 폐액에 인산 암모니움을 첨가 혼합하여 얻어진 중성 현탁액(잔여 고형분으로서 20-5부)을 분무하여 조립한다.',
    '[구성]본문에 설명하고 도면에 예시한 바와 같이, 기록매체로 형성한  정전 잠상을 토너로 현상하고 이 현상한 토너상을 기록매체와   동기하여 구동되는 중간매체에 일단 전사하고 이 중간 매체의   일부가 피마-킹 부재와 대면하는 전사 구간에 있어서 상기 토너 상을 주행중의 피마-킹 부재에 전사하는 마-킹 장치에 있어서   상기 피마-킹 부재의 마-킹 위치가 이송라인의 소정위치를 통과 하였을때에 정전 잠상의 형성을 개시하고 적어도 이 정전 잠상의형성 개시시로부터 토너상의 중간매체에의 전사가 완료할때까지 는 마-킹 장치를 일정속도로 구동하고 이 전사완료로부터 토너상이 상기 전사구간 또는 그 직전에 달할 사이는 정전 잠상 및 이 토너상의 이동한 거리가 상기 소정위치로부터의 피마-킹부재의  이동거리와 대응하도록 오차수정한 속도로 마-킹 장치를 구동   하고 상기 토너상이 전사 구간에 있을때는 마-킹 장치를 피마-킹부재에 동기한 속도로 구동하도록 한것을 특징으로 하는 구동   제어방법.',
     '[구성]불포화 폴리에스테르 수지(A), 진주 광택 안료(B), 경화 촉매(C), 알루미늄 알콕시드 및(또는) 그 유도체(D) 및 알코올성  수산기 함유 화합물(E)를 주성분으로 하고, 그 중의 알루미늄 알콕시드 및(또는) 그의 유도체(D)와 알코올성 수산기 함유  화합물(E)는 전자 100중량부에 대하여 후자가 50 내지 200중량부의 범위내의 비율인 수지 조성물(I)을 실온 또는 필요에 따라 가열하여 증점시켜 25도씨에 있어서의 점도가 200 내지 2000뽀아즈인 증점  조성물(II)로 한후, 필름(III)에 협지시킨 상태에서 금형을 사용하여 가열 가압하에 프레스하는 것을 특징으로 하는 진주 광택을갖는 단추의 제조방법.',
]

summarizer.summarize(sentence_list, topk=10)
```

실행결과는 다음과 같습니다.

```
[('킹', 2.7325503958210313),
 ('토너', 2.4095415247870546),
 ('하여', 2.0853219740616473),
 ('구동', 1.7635237827190942),
 ('전사', 1.7635237827190942),
 ('피마', 1.7635237827190942),
 ('상기', 1.7635237827190942),
 ('마', 1.7635237827190942),
 ('장치', 1.4405149116851135),
 ('어서', 1.1193510145338008)]
```

