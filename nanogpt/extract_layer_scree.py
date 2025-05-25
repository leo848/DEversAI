from sklearn.decomposition import PCA
from tqdm import tqdm
import json
import bracex
import numpy as np

last_file = None
def pca_variance(file):
    global last_file
    if file is not None:
        last_file = file
        embedding = np.load(file)
    elif last_file is not None:
        embedding = np.load(last_file).reshape((50256 * 768,))
        np.random.shuffle(embedding)
        embedding = embedding.reshape((50256, 768))
    else:
        exit(1)
    print(embedding.shape)
    pca = PCA()
    pca.fit_transform(embedding)
    return np.cumsum(pca.explained_variance_ratio_) * (-1) + 1

def main():
    # reference_variance = pca_variance("output/causal1.pt-embedding-768d.npy")
    result = {}
    for file in tqdm([*bracex.expand("output/{anti,}causal-fw2{,-laws1,-plenar1,-gutenberg1,-wikipedia1}-embedding-768d.npy"), None]):
        variance = pca_variance(file)
        if file is not None:
            key = file.split("-em")[0].split("/")[-1]
        else:
            key = "random"
        result[key] = variance.tolist()

    with open("output/wpe-scree2.json", "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    main()
