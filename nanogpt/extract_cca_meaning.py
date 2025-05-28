import numpy as np
import matplotlib.colors as mcolors
from matplotlib import pyplot as plt
from vocabulary import Vocabulary

# === PARAMETERS ===
dim = 6
logscale = False
x_bin_count = 200
y_bin_count = 20

# === LOAD DATA ===
try:
    cca_embeddings = np.load("/tmp/cca_embeddings.npy")
except FileNotFoundError:
    cca_embeddings = (
        np.load("output/causal-fw2-embedding-768d.npy") @
        np.load("output/causal-fw2-wte-cca.npy").T
    )
    np.save("/tmp/cca_embeddings.npy", cca_embeddings)

print("CCA extracted")

occurrence = np.loadtxt("../shallow-backend/assets/direct_histogram2.txt")
vocab = Vocabulary.load("fineweb2.vocab")
print("vocab loaded, generating lists")

# === EXTRACT MEASURES ===
xs = cca_embeddings[:, dim]
ys = np.array(
    [
        sum((
            token.value.count(b"\xc3\xa4"),
            token.value.count(b"\xc3\xb6"),
            token.value.count(b"\xc3\xbc"),
            token.value.count(b"\xc3\x9f"),
        ))
        for token in vocab.tokens
    ]
)
print(ys)

# === FILTER ===
mask = ys > 0
xs = xs[mask]
ys = ys[mask]

# === BINNING ===
if logscale:
    y_bins = np.logspace(np.log10(ys.min()), np.log10(ys.max()), y_bin_count)
    norm = mcolors.LogNorm()
    yscale = "log"
else:
    y_bins = np.linspace(ys.min(), ys.max(), y_bin_count)
    norm = mcolors.Normalize()
    yscale = "linear"

x_bins = np.linspace(xs.min(), xs.max(), x_bin_count)

# === COMPUTE HISTOGRAM ===
H, xedges, yedges = np.histogram2d(xs, ys, bins=[x_bins, y_bins])

# === MASK EMPTY BINS ===
H_masked = np.ma.masked_where(H == 0, H)

# === PLOT WITH PCOLORMESH ===
fig, ax = plt.subplots(figsize=(8, 6))
mesh = ax.pcolormesh(
    xedges,
    yedges,
    H_masked.T,
    norm=norm,
    cmap='viridis',
    shading='auto'
)

ax.set_yscale(yscale)
ax.set_xlabel(f"CCA Embedding Dimension {dim}")
ax.set_ylabel("Token Measure")
plt.colorbar(mesh, ax=ax, label="Token Density")
plt.title(f"Token Measure vs CCA Embedding (Dim {dim}) [{yscale} scale]")
plt.tight_layout()
plt.show()
