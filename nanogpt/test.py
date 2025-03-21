"""
Test the model's loss on a lot of data
"""
import os
import numpy as np
from contextlib import nullcontext
import torch
import random
from gpt import GPTConfig, GPT
from tqdm import tqdm
import bracex

# -----------------------------------------------------------------------------
init_from = 'resume' # either 'resume' (from an out_dir) or a gpt2 variant (e.g. 'gpt2-xl')
seed = random.randint(0, int(1e10))
print(f"Using seed {seed}")

ckpt_value = 100000
causality = "causal"
device = 'cuda:0' # examples: 'cpu', 'cuda', 'cuda:0', 'cuda:1', etc.
files = bracex.expand("fw2-shard-000{0,1,2}0.bin")

dtype = 'bfloat16' if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else 'float16' # 'float32' or 'bfloat16' or 'float16'
compile = True # use PyTorch 2.0 to compile the model to be faster
batch_size = 32
block_size = 1024

exec(open('configurator.py').read()) # overrides from command line or config file
# -----------------------------------------------------------------------------

torch.manual_seed(seed)
torch.cuda.manual_seed(seed)
torch.backends.cuda.matmul.allow_tf32 = True # allow tf32 on matmul
torch.backends.cudnn.allow_tf32 = True # allow tf32 on cudnn
device_type = 'cuda' if 'cuda' in device else 'cpu' # for later use in torch.autocast
ptdtype = {'float32': torch.float32, 'bfloat16': torch.bfloat16, 'float16': torch.float16}[dtype]
ctx = nullcontext() if device_type == 'cpu' else torch.amp.autocast(device_type=device_type, dtype=ptdtype)

ckpt_path = f"/output/{causality}-fw2/ckpt_{ckpt_value}.pt"
checkpoint = torch.load(ckpt_path, map_location=device, weights_only=True)
gptconf = GPTConfig(**checkpoint['model_args'])
model = GPT(gptconf)
state_dict = checkpoint['model']
unwanted_prefix = '_orig_mod.'
for k,v in list(state_dict.items()):
    if k.startswith(unwanted_prefix):
        state_dict[k[len(unwanted_prefix):]] = state_dict.pop(k)
model.load_state_dict(state_dict)

model.eval()
model.to(device)
if compile:
    model = torch.compile(model) # requires PyTorch 2.0 (optional)

# run generation
with torch.no_grad(), ctx:
    directory = "/data/fw2-tokenized/val"
    for file in tqdm(files):
        losses = []
        try:
            path = os.path.join(directory, file)
            if not os.path.isfile(path): exit(1)
            data = np.memmap(path, dtype=np.dtype(">u2"), mode="r")

            total_loss = 0
            num_batches = 0

            for start_i in tqdm(list(range(0, len(data) - block_size - batch_size - 1, block_size))):
                x, y = None, None
                if causality == "causal":
                    x = torch.stack( [
                        torch.from_numpy(
                            data[i:i + block_size].astype(np.int64)
                        )
                        for i in range(start_i, start_i + batch_size)
                    ])
                    y = torch.stack([
                        torch.from_numpy(
                            data[i + 1: i + 1 + block_size].astype(np.int64)
                        )
                        for i in range(start_i, start_i + batch_size)
                    ])
                elif causality == "anticausal":
                    x = torch.stack([
                        torch.from_numpy(
                            data[i + 1: i + 1 + block_size][::-1].astype(np.int64)
                        )
                        for i in range(start_i, start_i + batch_size)
                    ])
                    y = torch.stack( [
                        torch.from_numpy(
                            data[i:i + block_size][::-1].astype(np.int64)
                        )
                        for i in range(start_i, start_i + batch_size)
                    ])

                x, y = x.pin_memory().to(device, non_blocking=True), y.pin_memory().to(device, non_blocking=True)
                _, loss = model(x, y)
                losses.append(loss.item())
        except Exception as e:
            print(f"Exception: {e}")
        losses_numpy = np.array(losses)
        mean = np.mean(losses_numpy)
        filename = f"/output/{causality}-fw2/{file}-losses.npy"
        np.save(filename, losses_numpy)
        print(f"Saved {len(losses_numpy)} loss entries (mean {mean}) to {filename}")


