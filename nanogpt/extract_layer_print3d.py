import numpy as np
from sklearn.neighbors import KernelDensity
import trimesh

# --------------------------- CONFIGURATION ---------------------------

# I/O-Pfade
INPUT_NPY = "output/augmented-fw2-embedding-2d.npy"
OUTPUT_STL = "output/augmented-fw2-density-print3d-grid300.stl"
# INPUT_NPY = "output/causal-fw2-embedding-2d.npy"
# OUTPUT_STL = "output/causal-fw2-density-print3d.stl"
# INPUT_NPY = "output/anticausal-fw2-embedding-2d.npy"
# OUTPUT_STL = "output/anticausal-fw2-density-print3d.stl"

# Grid-Auflösung (Anzahl Punkte pro Achse)
GRID_SIZE = 300

# KDE-Parameter
KDE_BANDWIDTH = 0.1  # Kernel-Bandbreite für Dichteschätzung

# Maßstab: Größe einer Einheit im Koordinatensystem in Zentimetern
SCALE = 0.4  # [MODIFIED] 1.0 cm pro Einheit

# Plateau-Parameter (Minimale Höhe in mm)
PLATEAU_HEIGHT = 0.0

# Maximale Modellhöhe über Plateau in mm
MAX_HEIGHT = 60.0 * SCALE

# Basisplatte (Rechteck unter dem Modell)
BASEPLATE_THICKNESS = 1.0  # mm
BASEPLATE_MARGIN = 1.0     # mm Abstand um das Modell

# Modellgrenzen (None = automatisch anhand der Daten)
# # causal
# X_MIN = -9
# X_MAX = 15
# Y_MIN = 13
# Y_MAX = -11
# # anticausal
# X_MIN = -9
# X_MAX = 15
# Y_MIN=-14
# Y_MAX=15
# augmented
X_MIN = -20
X_MAX = 16
Y_MIN = -12
Y_MAX = 8


# ----------------------------------------------------------------------

def load_points(path):
    pts = np.load(path)
    assert pts.ndim == 2 and pts.shape[1] == 2, "Erwartetes Format (N,2)"
    return pts

def clamp_nonzero(arr, min_val, max_val):
    result = arr.copy()
    mask = result > min_val
    result[mask] = np.clip(result[mask] + 0.0002, min_val, max_val)
    return result

def compute_density(points, bandwidth, grid_size, bounds):
    kde = KernelDensity(bandwidth=bandwidth, kernel='gaussian')
    kde.fit(points)
    xmin, xmax = bounds['xmin'], bounds['xmax']
    ymin, ymax = bounds['ymin'], bounds['ymax']
    xx, yy = np.meshgrid(
        np.linspace(xmin, xmax, grid_size),
        np.linspace(ymin, ymax, grid_size)
    )
    grid = np.vstack([xx.ravel(), yy.ravel()]).T
    print("sampling grid")
    log_d = kde.score_samples(grid)
    density = clamp_nonzero(np.exp(log_d), 0.0002, 0.03).reshape(xx.shape)
    # Scale xx and yy to cm [MODIFIED]
    xx *= SCALE * 10
    yy *= SCALE * 10
    return xx, yy, density

def normalize_and_plateau(density, plateau_h, max_h):
    dmin, dmax = density.min(), density.max()
    dnorm = (density - dmin) / (dmax - dmin + 1e-12)
    return plateau_h + dnorm * (max_h - plateau_h)

def make_height_mesh(xx, yy, heights):
    verts, faces = [], []
    rows, cols = xx.shape
    for i in range(rows-1):
        for j in range(cols-1):
            v0 = [xx[i,j],   yy[i,j],   heights[i,j]]
            v1 = [xx[i,j+1], yy[i,j+1], heights[i,j+1]]
            v2 = [xx[i+1,j], yy[i+1,j], heights[i+1,j]]
            v3 = [xx[i+1,j+1], yy[i+1,j+1], heights[i+1,j+1]]
            idx = len(verts)
            verts.extend([v0, v1, v2, v3])
            faces.append([idx,   idx+1, idx+2])
            faces.append([idx+1, idx+3, idx+2])
    return trimesh.Trimesh(vertices=np.array(verts),
                           faces=np.array(faces),
                           process=True)

def make_baseplate(xx, yy, plate_h, thickness, margin):
    xmin, xmax = xx.min()-margin, xx.max()+margin
    ymin, ymax = yy.min()-margin, yy.max()+margin
    width, depth = xmax - xmin, ymax - ymin
    center = ((xmin+xmax)/2, (ymin+ymax)/2, plate_h - thickness/2)
    return trimesh.creation.box(
        extents=(width, depth, thickness),
        transform=trimesh.transformations.translation_matrix(center)
    )

def main():
    pts = load_points(INPUT_NPY)
    bounds = {
        'xmin': X_MIN if X_MIN is not None else pts[:,0].min(),
        'xmax': X_MAX if X_MAX is not None else pts[:,0].max(),
        'ymin': Y_MIN if Y_MIN is not None else pts[:,1].min(),
        'ymax': Y_MAX if Y_MAX is not None else pts[:,1].max()
    }
    print("computing density")
    xx, yy, dens = compute_density(pts, KDE_BANDWIDTH, GRID_SIZE, bounds)
    print("normalize and plateau")
    heights = normalize_and_plateau(dens, PLATEAU_HEIGHT, MAX_HEIGHT)
    print("Erzeuge Höhen-Mesh...")
    mesh_topo = make_height_mesh(xx, yy, heights)
    print("Erzeuge Basisplatte...")
    mesh_plate = make_baseplate(xx, yy, PLATEAU_HEIGHT, BASEPLATE_THICKNESS, BASEPLATE_MARGIN)
    print("Kombiniere und exportiere STL...")
    combined = trimesh.util.concatenate([mesh_topo, mesh_plate])
    combined.export(OUTPUT_STL)
    print(f"Fertig: {OUTPUT_STL}")

if __name__ == "__main__":
    main()
