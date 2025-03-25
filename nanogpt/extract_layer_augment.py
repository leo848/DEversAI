from sklearn.decomposition import PCA
import gc
from tqdm import tqdm
import json
import pacmap
import bracex
import numpy as np

def main():
    # reference_variance = pca_variance("output/causal1.pt-embedding-768d.npy")
    result = {}
    anticausal_model = np.load("output/anticausal-fw2-embedding-768d.npy")
    causal_model = np.load("output/anticausal-fw2-embedding-768d.npy")
    print(causal_model.shape)
    data = np.concat((anticausal_model, causal_model), axis=1)

    model_id = "augmented-fw2"
    for dim in tqdm([2, 3, 768 * 2], leave=False):
        if dim != 768 * 2:
            embedding = pacmap.PaCMAP(n_components=dim, n_neighbors=None, num_iters=900, verbose=True)

            data_transformed = embedding.fit_transform(data, init="random")
        else:
            data_transformed = data

        np.save(f"output/{model_id}-embedding-{dim}d.npy", data_transformed)
        np.save(f"../shallow-backend/assets/embedding/{dim}d/{model_id}.npy", data_transformed)

        gc.collect()

if __name__ == "__main__":
    main()
