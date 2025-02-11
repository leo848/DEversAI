from model import GPTConfig, GPT
from matplotlib import pyplot as plt
from tqdm import tqdm
import pacmap
import torch
import os
import sys
import random
import numpy as np


device = 'cpu' # examples: 'cpu', 'cuda', 'cuda:0', 'cuda:1', etc.
dtype = 'bfloat16' if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else 'float16' # 'float32' or 'bfloat16' or 'float16'
compile = False # use PyTorch 2.0 to compile the model to be faster

input_directory = "/output/anticausal1/"
models = os.listdir(input_directory)

for model_name in tqdm(models):
    path = os.path.join(input_directory, model_name)
    if not os.path.isfile(path): continue
    checkpoint = torch.load(path, map_location=device, weights_only=True)
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


    wpe_data = model.transformer.wpe(torch.tensor(np.arange(0, 1024))).detach().clone().transpose(0, 1).numpy()
    wte_data = model.transformer.wte(torch.tensor(np.arange(0, 50256))).detach().clone().numpy()

    # def mad(row):
    # total_differences = 0
    # for i in range(len(row)-1):
    # total_differences += abs(row[i] - row[i+1])
    # return (mad := total_differences / len(row))
    np.save(input_directory + "wte/" + model_name.split(".")[0] + ".npy", wte_data)
    np.save(input_directory + "wpe/" + model_name.split(".")[0] + ".npy", wpe_data)

    # mads = [mad(row) for row in data]
    # average_mads = sum(mads) / len(mads)
    # print(model_name, ":", average_mads)

    # np.save("output/anticausal1-wpe.npy", data)

    # print(data)

    # embedding = pacmap.PaCMAP(n_components=2, n_neighbors=None, num_iters=900, verbose=True)

    # data_transformed = embedding.fit_transform(data)

    # np.save("output/causal1-embedding-2d.npy", data_transformed)

