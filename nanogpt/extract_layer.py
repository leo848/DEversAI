from model import GPTConfig, GPT
from matplotlib import pyplot as plt
import pacmap
import torch
import os
import sys
import random
import numpy as np

init_from = 'resume' # either 'resume' (from an out_dir) or a gpt2 variant (e.g. 'gpt2-xl')
model_name = "causal1.pt"
out_dir = 'output' # ignored if init_from is not 'resume'

device = 'cpu' # examples: 'cpu', 'cuda', 'cuda:0', 'cuda:1', etc.
dtype = 'bfloat16' if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else 'float16' # 'float32' or 'bfloat16' or 'float16'
compile = False # use PyTorch 2.0 to compile the model to be faster

assert init_from == "resume"

exec(open('configurator.py').read()) # overrides from command line or config file

ckpt_path = os.path.join(out_dir, model_name)
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


tokens = torch.tensor(np.arange(0, 50256))


data = model.transformer.wpe(torch.tensor(np.arange(0, 1024))).detach().clone().transpose(0, 1).numpy()


mads = [mad(row) for row in data]

# np.save("output/anticausal1-wpe.npy", data)

# print(data)

# embedding = pacmap.PaCMAP(n_components=2, n_neighbors=None, num_iters=900, verbose=True)

# data_transformed = embedding.fit_transform(data)

# np.save("output/causal1-embedding-2d.npy", data_transformed)

