from model import GPTConfig, GPT
import gc
from tqdm import tqdm
import itertools
import bracex
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

for model_name in tqdm(bracex.expand("{anti,}causal1-{plenar,laws}1.pt")):
    print(model_name)
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


    data = model.transformer.wte(tokens).detach().clone().numpy()

    for dim in [2, 3]:
        embedding = pacmap.PaCMAP(n_components=dim, n_neighbors=None, num_iters=900, verbose=True)

        data_transformed = embedding.fit_transform(data)

        np.save(f"output/{model_name}-embedding-{dim}d.npy", data_transformed)

        gc.collect()

def extract_wpe(model):
    data = model.transformer.wpe(torch.tensor(np.arange(0, 1024))).detach().clone().transpose(0, 1).numpy()
    # np.save(f"output/{model_name}-embedding-{dim}d.npy", data_transformed)
