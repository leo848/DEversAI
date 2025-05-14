import json
import numpy as np

def parse_sparse_pca_json(sparse_pca_json):
    num_components = len(sparse_pca_json)
    output = np.zeros((num_components, 768), dtype=np.float32)

    for i, component in enumerate(sparse_pca_json):
        for entry in component:
            dim = entry['dim']
            coeff = entry['coeff']
            output[i, dim] = coeff

    return output

if __name__ == "__main__":
    with open('/output/wte-cca-output.json', 'r') as f:
        sparse_data = json.load(f)
    causal_project = parse_sparse_pca_json(sparse_data["causal"])
    anticausal_project = parse_sparse_pca_json(sparse_data["anticausal"])

    np.save("/output/causal-fw2-wte-cca.npy", causal_project)
    np.save("/output/anticausal-fw2-wte-cca.npy", anticausal_project)
