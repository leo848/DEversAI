from sklearn.decomposition import PCA
from tqdm import tqdm
import json
import pacmap
import bracex
import numpy as np

def main():
    # reference_variance = pca_variance("output/causal1.pt-embedding-768d.npy")
    result = {}
    anticausal_model = np.load("output/anticausal1.pt-embedding-768d.npy")
    causal_model = np.load("output/causal1.pt-embedding-768d.npy")
    print(causal_model.shape)
    augmented = np.concat((anticausal_model, causal_model), axis=1)

    embedding = pacmap.PaCMAP(n_components=2, n_neighbors=None, num_iters=900, verbose=True)
    data_transformed = embedding.fit_transform(augmented)
    print(data_transformed)
    np.savetxt(f"output/augmented-embedding-2d.csv", data_transformed, delimiter=",")

if __name__ == "__main__":
    main()
