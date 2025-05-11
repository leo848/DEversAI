import numpy as np

FILE = "/input/fw2-tokenized/train/fw2-shard-00069.bin"

data = np.memmap(FILE, dtype=np.dtype(">u2"))

print(data)
