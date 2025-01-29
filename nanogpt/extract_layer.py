from model import GPTConfig, GPT
from matplotlib import pyplot as plt
import pacmap
import torch
import os
import sys
import random
import numpy as np

tokens = torch.tensor(np.arange(0, 50256))

init_from = 'resume' # either 'resume' (from an out_dir) or a gpt2 variant (e.g. 'gpt2-xl')
model_name = "ckpt_300000.pt"
out_dir = 'output' # ignored if init_from is not 'resume'

device = 'cuda' # examples: 'cpu', 'cuda', 'cuda:0', 'cuda:1', etc.
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

data = model.transformer.wte(tokens).detach().clone().numpy()

# print(data)

embedding = pacmap.PaCMAP(n_components=2, n_neighbors=None, num_iters=900, verbose=True)

data_transformed = embedding.fit_transform(data)

np.save("output/anticausal1-embedding-2d.npy", data_transformed)

# from mpl_toolkits.mplot3d import Axes3D

# # Create a 3D scatter plot
# fig = plt.figure(figsize=(8, 8))
# ax = fig.add_subplot(111, projection='3d')

# # Plotting the points
# ax.scatter(data_transformed[:, 0], data_transformed[:, 1], data_transformed[:, 2], s=0.5, alpha=0.6)

# # Set labels
# ax.set_xlabel('Component 1')
# ax.set_ylabel('Component 2')
# ax.set_zlabel('Component 3')

# plt.title('3D Visualization using PaCMAP')
# plt.show()
