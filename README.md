# cola-komoran-python-client

## 주의

> 라이브러리를 업데이트되면, ray.remote 객체 재생성을 위해 ray cluster stop/start가 필요할 수도 있습니다.

## 라이브러리 설치

```sh
pip install https://github.com/euclidsoft/cola-komoran-python-client/archive/master.zip
```

## ray를 활용한 bulk 호출 샘플 코드

```python
from cola_komoran_python_client import ray_init, ray_shutdown, summarize_batch_with_ray

ray_init()  # 처음 1회만 수행해주세요.

# ray를 활용한 summarize 수행합니다. tqdm은 내부적으로 수행됩니다.
# tqdm을 수행하지 않으려면 with_tqdm=False 인자를 지정해주세요.
keyword_list = summarize_batch_with_ray(sentence_list_series)

ray_shutdown()  # 모든 작업이 끝내거나, ray cluster를 초기화시키고자 할 때
```

## 단일 호출 샘플 코드

```python
from cola_komoran_python_client import GrpcTokenizer

tokenize = GrpcTokenizer("localhost:50051")
summarizer = KeywordSummarizer(
    tokenize = tokenize,
    window = -1,
    verbose = False,
)
summarizer.summarize(sentence_list, topk=10)

```

