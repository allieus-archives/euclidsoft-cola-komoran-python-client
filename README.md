# cola-komoran-python-client

```python
from cola_komoran_python_client import ray_init, ray_shutdown, summarize_batch_with_ray

ray_init()  # 처음 1회만 수행

# ray를 활용한 summarize 수행
keyword_list = summarize_batch_with_ray(sentence_list_series)

ray_shutdown()  # 모든 작업이 끝내거나, ray cluster를 초기화시키고자 할 때
```

