"""
Sample from a trained model
"""
import os
import sys
from ast import literal_eval
from more_itertools import windowed
import pickle
from contextlib import nullcontext
import torch
import random
from gpt import GPTConfig, GPT
from torch.nn import functional as F

# -----------------------------------------------------------------------------
num_samples = 10 # number of samples to draw
max_new_tokens = 400 # number of tokens generated in each sample
temperature = 0.8 # 1.0 = no change, < 1.0 = less random, > 1.0 = more random, in predictions
top_k = 200 # retain only the top_k most likely tokens, clamp others to have 0 probability
seed = random.randint(0, int(1e10))
print(f"Using seed {seed}")
device = 'cuda' # examples: 'cpu', 'cuda', 'cuda:0', 'cuda:1', etc.

model_name = "anticausal1-plenar1.pt"
compile = False # use PyTorch 2.0 to compile the model to be faster
causality = "anticausal" if "anticausal" in model_name else "causal" # 'causal' or 'anticausal'
show_probs = False

exec(open('configurator.py').read()) # overrides from command line or config file
# -----------------------------------------------------------------------------

torch.manual_seed(seed)
torch.cuda.manual_seed(seed)

model = GPT.load(os.path.join("output", model_name))

if compile:
    model = torch.compile(model) # requires PyTorch 2.0 (optional)

# ok let's assume gpt-2 encodings by default
vocab_file = "german-complete.vocab"
print(f"Using {vocab_file} vocab")
with open(vocab_file) as f:
    merge_rules = list(map(lambda s: list(map(int, s.strip().split(" "))), list(f)))
token_to_byte = []
token_pairs_set = {}
for i in range(256):
    token_to_byte.append(bytes([i]))
for [left, right, result] in merge_rules:
    token_to_byte.append(token_to_byte[left] + token_to_byte[right])
    token_pairs_set[((left, right))] = result

def encode(string):
    tokens = list(bytes(string.encode("utf-8")))
    while True:
        next_mergeable_pair = None
        for pair in windowed(tokens, n=2):
            if pair in token_pairs_set and (next_mergeable_pair is None or token_pairs_set[next_mergeable_pair] > token_pairs_set[pair]):
                next_mergeable_pair = pair
        if next_mergeable_pair is None:
            break
        new_tokens = []
        merged = False
        for (left, right) in windowed(tokens, n=2):
            if merged:
                merged = False
                continue
            if (left, right) == next_mergeable_pair:
                new_tokens.append(token_pairs_set[(left, right)])
                merged = True
            else:
                new_tokens.append(left)
        if not merged:
            new_tokens.append(tokens[-1])
        tokens = new_tokens
    if causality == "anticausal":
        tokens = list(reversed(tokens))
    print(tokens)
    return tokens

def decode(tokens, return_bytes=False):
    if causality == "anticausal":
        tokens = list(reversed(tokens))
    token_bytes = bytes()
    for token in tokens:
        if token == 0xFF:
            break
        token_bytes += token_to_byte[token]
    if return_bytes:
        return token_bytes
    else:
        return token_bytes.decode(encoding="utf-8", errors="replace")

# encode the beginning of the prompt
prompt_input = True
while prompt_input:
    raw_input = input("\n\x1B[32m>>> \x1B[0m")
    eval_input = literal_eval(f'"{raw_input}"')
    if causality == "causal":
        prompt_input = eval_input
    else:
        prompt_input = eval_input
    start_ids = encode(prompt_input)
    if causality == "anticausal":
        start_ids = [0xFF] + start_ids

    x = (torch.tensor(start_ids, dtype=torch.long, device=device)[None, ...])

    # run generation
    with torch.no_grad():
        if show_probs:
            logits, loss = model.forward(x)
            probs = F.softmax(logits, dim=-1)
            v, i = torch.topk(probs, 10)
            print(v)
            print(i)
        elif causality == 'causal':
            gen = model.generate_generator(x, max_new_tokens, temperature=temperature, top_k=top_k)
            print()
            print(prompt_input, end="", flush=True)
            colored = False
            COLORS = ["168;213;226", "248;191;213", "251;231;161", "178;226;180"]
            current_color = 0
            try:
                for token in gen:
                    token_bytes = decode(token.tolist()[0], return_bytes=True)
                    if colored:
                        sys.stdout.buffer.write(f"\x1B[30;48;2;{COLORS[current_color]}m".encode())
                    sys.stdout.buffer.write(token_bytes)
                    if colored:
                        sys.stdout.buffer.write(f"\x1B[0m".encode())
                        current_color += 1
                        if current_color == len(COLORS):
                            current_color = 0
                    sys.stdout.flush()
            except KeyboardInterrupt:
                continue
            print()
        elif causality == 'anticausal':
            y = model.generate(x, max_new_tokens, temperature=temperature, top_k=top_k)
            string = decode(y)
            print(string + prompt_input)
