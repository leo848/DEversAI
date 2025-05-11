import numpy as np
import json
from random import randint
from vocabulary import Vocabulary

FILE = "/data/fw2-tokenized/train/fw2-shard-00069.bin"

data = np.memmap(FILE, dtype=np.dtype(">u2"))
vocab = Vocabulary.load("fineweb2.vocab")

n = 100

result = []
for i in range(n):
    random_idx = randint(0, len(data) // 2)
    tokens = data[random_idx:random_idx+100]
    result_str = vocab.decode(list(tokens))
    result.append(result_str)

print(json.dumps(result))
