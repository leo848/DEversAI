import json
from gpt import GPT
import torch
from torch.nn import functional as F
from vocabulary import Vocabulary

def main():
    model = GPT.load("output/causal-fw2.pt")
    vocab = Vocabulary.load("fineweb2.vocab")

    model_x = []
    for number in range(101):
        string = f"{number} "
        tokens = vocab.encode(string)
        # assert len(tokens) == 1
        model_x.append(tokens)

    tensor = torch.tensor(model_x).to("cuda")
    logits, _ = model(tensor)
    # probs = F.softmax(logits, dim = -1)

    _, top_tokens = torch.topk(logits, 1)

    token_set = set()

    for number in range(101):
        print(number, end=": ")
        for token_id in top_tokens[number, 0].tolist():
            token_set.add(token_id)
            print(vocab.decode([token_id]), end=" ")
        print()

    result = {}
    for i, token_id in enumerate(token_set):
        string = vocab.decode([token_id])
        print(i, ":", string)

        prob_over_number = logits[:, 0, token_id].tolist()
        result[token_id] = {"string": string, "data": prob_over_number}

    with open("output/causal-fw2-numbers-encoding.json", "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    main()
