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
from vocabulary import Vocabulary
from torch.nn import functional as F

# -----------------------------------------------------------------------------
num_samples = 10 # number of samples to draw
max_new_tokens = 300 # number of tokens generated in each sample
temperature = 0.8 # 1.0 = no change, < 1.0 = less random, > 1.0 = more random, in predictions
top_k = 200 # retain only the top_k most likely tokens, clamp others to have 0 probability
seed = random.randint(0, int(1e10))
print(f"Using seed {seed}")
device = 'cuda' # examples: 'cpu', 'cuda', 'cuda:0', 'cuda:1', etc.

model_name = "anticausal1.pt"
compile = False # use PyTorch 2.0 to compile the model to be faster
causality = "anticausal" if "anticausal" in model_name else "causal" # 'causal' or 'anticausal'
show_probs = True
show_probs_tries = 3

exec(open('configurator.py').read()) # overrides from command line or config file
# -----------------------------------------------------------------------------

torch.manual_seed(seed)
torch.cuda.manual_seed(seed)

model = GPT.load(os.path.join("output", model_name))

if compile:
    model = torch.compile(model) # requires PyTorch 2.0 (optional)

vocab = Vocabulary.load("german-complete.vocab")

# encode the beginning of the prompt
prompt_input = True
while prompt_input:
    raw_input = input("\n\x1B[32m>>> \x1B[0m")
    eval_input = literal_eval(f'"{raw_input}"')
    if causality == "causal":
        prompt_input = eval_input
    else:
        prompt_input = eval_input
    start_ids = vocab.encode(prompt_input, reverse=causality == "anticausal")

    x = (torch.tensor(start_ids, dtype=torch.long, device=device)[None, ...])

    # run generation
    with torch.no_grad():
        if show_probs:
            if show_probs_tries == 1:
                logits, loss = model.forward(x)
                probs = F.softmax(logits / temperature, dim=-1)
                v, i = torch.topk(probs, 20)
                for prob, token_id in zip(v[0][0], i[0][0]):
                    print(f"{prob:.3f} {vocab.decode([int(token_id)])}")
            else:
                token_tries = [(x[0].tolist(), 1.0)]
                done = []
                while token_tries:
                    print(token_tries)
                    (cur_x, cur_prob) = token_tries[0]
                    token_tries = token_tries[1:]

                    if len(cur_x) >= show_probs_tries:
                        done.append((cur_x, cur_prob))
                        continue

                    logits, loss = model.forward(
                        torch.tensor(cur_x, dtype=torch.long, device=device)[None, ...]
                    )
                    probs = F.softmax(logits / temperature, dim=-1)
                    v, i = torch.topk(probs, 3)
                    for prob, token_id in zip(v[0][0], i[0][0]):
                        token_tries.append((cur_x + [token_id], float(prob) * cur_prob))
                print(done)

        elif causality == 'causal':
            gen = model.generate_generator(x, max_new_tokens, temperature=temperature, top_k=top_k)
            print()
            print(prompt_input, end="", flush=True)
            colored = False
            COLORS = ["168;213;226", "248;191;213", "251;231;161", "178;226;180"]
            current_color = 0
            try:
                for token in gen:
                    token_bytes = vocab.decode_bytes(
                        token.tolist()[0]
                    )
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
            string = vocab.decode(y, reverse=True)
            print(string + prompt_input)
