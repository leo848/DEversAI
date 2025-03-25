import json
import numpy as np
from sklearn.cross_decomposition import CCA

# Load 768-dimensional embeddings
model_suffix = ""
model_ids = ["anticausal-fw2" + model_suffix, "causal-fw2" + model_suffix]
wtes = [np.load("output/" + model_id + "-embedding-768d.npy") for model_id in model_ids]
X, Y = wtes

# Compute CCA with 10 components
num_components = min(10, X.shape[1])  # Ensure we don’t exceed 768
cca = CCA(n_components=num_components)
X_c, Y_c = cca.fit_transform(X, Y)

# Extract canonical weights
x_weights = cca.x_weights_  # Shape: (768, num_components)
y_weights = cca.y_weights_  # Shape: (768, num_components)

# Number of significant dimensions per component
num_top_dims = 20

# Collect results
results = {"anticausal": [], "causal": []}

for comp in range(num_components):
    # Find top dimensions for this component
    top_x_dims = np.argsort(-np.abs(x_weights[:, comp]))[:num_top_dims]
    top_y_dims = np.argsort(-np.abs(y_weights[:, comp]))[:num_top_dims]

    # Store results
    results["anticausal"].append([
        {"dim": int(dim), "coeff": float(x_weights[dim, comp])} for dim in top_x_dims
    ])
    results["causal"].append([
        {"dim": int(dim), "coeff": float(y_weights[dim, comp])} for dim in top_y_dims
    ])

# Output JSON to stdout
print(json.dumps(results, indent=2))
