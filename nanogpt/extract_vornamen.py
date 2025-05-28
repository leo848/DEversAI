import re
import numpy as np
import json
from scipy import stats
from collections import defaultdict
from math import inf
from torch.nn import functional as F
from tqdm import tqdm
from vocabulary import Vocabulary
from gpt import GPT
import torch

VORNAMEN = [
  "Frank",
  "Max",
  "Walter",
  "Clara",
  "Frieda",
  "Klara",
  "Frank-Walter",
  "Steffi",
  "Müller",
  "Vorname",
  "Sebastian",
  "Auguste",
  "Norman",
  "Felix",
  "Louisa",
  "Luisa",
  "Eva",
  "André",
  "Heinrich",
  "Friedrich",
  "Karl",
  "Hermann",
  "Elisabeth",
  "Gertrud",
  "Heinz",
  "Ursula",
  "Günter",
  "Inge",
  "Klaus",
  "Monika",
  "Peter",
  "Sabine",
  "Jürgen",
  "Andrea",
  "Michael",
  "Nicole",
  "Christian",
  "Stefanie",
  "Kevin",
  "Jennifer",
  "Leon",
  "Lina",
  "Wilhelmine",
  "Lena",
  "Ben",
  "Mia",
  "Noah",
  "Emilia",
  "Clara",
  "Mandy",
  "Justin",
  "Chantal",
  "Sabrina",
  "Oskar",
  "Clara",
  "Mia",
  "Leonie",
  "Brunhilde",
  "Adelheid",
  "Eberhard",
  "Siegfried",
  "Gertrud",
  "Martin",
  "Thomas",
  "Katharina",
  "Wolfgang",
  "Otto",
  "Emil",
  "Adolf",
  "Fritz",
  "Josef",
  "Martha",
  "Johanna",
  "Wilhelmine",
  "Else",
  "Katharina",
  "Hedwig",
  "Olga",
  "Dora",
  "Silke",
]

INCLUDE_EXPR = re.compile(r"^[0-9]+ ?")
COMPLETE_YEAR = re.compile(r"^[0-9]{4}")
NECESSARY_EXPR = re.compile(r"^[0-9]{0,3}$")

def main():
    vocab = Vocabulary.load("fineweb2.vocab")

    token_mask = torch.zeros(50304).to("cuda")
    for token in range(50256):
        string = vocab.decode([token])
        if not re.match(INCLUDE_EXPR, string):
            token_mask[token] = -inf

    print(token_mask)

    model = GPT.load("output/causal-fw2-wikipedia1.pt")

    json_output = []

    bar = tqdm(set(VORNAMEN))
    for vorname in bar:
        bar.set_description(vorname)
        results = defaultdict(float)
        continuations: set[tuple[tuple[int, ...], float]] = {((), 1.0)}
        while continuations:
          (tokens, prob) = continuations.pop()
          if prob < 1e-4:
              continue
          string = vocab.decode(list(tokens))
          input_string = f"# {vorname} Müller\n\n{vorname} Müller (* 20. September {string}"
          if re.match(COMPLETE_YEAR, string):
            year = int(string[:4])
            results[year] += prob
          if not re.match(NECESSARY_EXPR, string):
            continue

          model_x = torch.tensor([vocab.encode(input_string)]).to("cuda")
          model_y, _ = model(model_x)

          probs_vorname = F.softmax(model_y[0][0] + token_mask, dim = -1)
          top_probs, top_tokens = torch.topk(probs_vorname, 100)

          new_continuations = {(int(token.item()), prob.item(),) for (token, prob) in zip(top_tokens, top_probs)}
          for (new_token, new_prob) in new_continuations:
            continuations.add((
              tokens + (new_token,),
              prob * new_prob
            ))

        prob_sum = sum(results.values())
        results = {year: prob / prob_sum for (year, prob) in results.items()}
        decade_results = defaultdict(float)
        for year, prob in results.items():
          decade_results[year // 10 * 10] += prob

        keys = np.array(list(results.keys()))
        values = np.array(list(results.values()))
        stats_mean = np.average(keys, weights=values)
        stats_variance = np.average((keys - stats_mean) ** 2, weights=values)
        stats_std = np.sqrt(stats_variance)
        stats_mode = keys[np.argmax(values)]
        stats_third_moment = np.average((keys - stats_mean) ** 3, weights=values)
        stats_skew = stats_third_moment / stats_std**3

        stats = {
          "mean": stats_mean,
          "variance": stats_variance,
          "std": stats_std,
          "mode": stats_mode,
          "skew": stats_skew,
        }

        json_output.append({
          "vorname": vorname,
          "year_data": results,
          "decade_results": decade_results,
          "stats": {key: float(stat) for (key, stat) in stats.items()},
        })

    with open("output/causal-fw2-wikipedia1-vornamen.json", "w") as f:
      json.dump(json_output, f)

if __name__ == "__main__":
  main()
