from pathlib import Path
import matplotlib.pyplot as plt

IMAGES_DIR = Path(__file__).parent.parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)

# Exact WKT coordinates from the blog draft (DE-9IM relationships)
RELATIONSHIPS = [
    (
        "2_rel_equals",
        "Equals",
        [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)],   # POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))
        [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)],   # POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))
    ),
    (
        "2_rel_disjoint",
        "Disjoint",
        [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)],   # POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))
        [(2, 2), (3, 2), (3, 3), (2, 3), (2, 2)],   # POLYGON ((2 2, 3 2, 3 3, 2 3, 2 2))
    ),
    (
        "2_rel_touches",
        "Touches",
        [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)],   # POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))
        [(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)],   # POLYGON ((1 1, 1 2, 2 2, 2 1, 1 1))
    ),
    (
        "2_rel_contains",
        "Contains",
        [(0, 0), (0, 3), (3, 3), (3, 0), (0, 0)],   # POLYGON ((0 0, 0 3, 3 3, 3 0, 0 0))
        [(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)],   # POLYGON ((1 1, 1 2, 2 2, 2 1, 1 1))
    ),
    (
        "2_rel_covers",
        "Covers",
        [(0, 0), (0, 3), (3, 3), (3, 0), (0, 0)],   # POLYGON ((0 0, 0 3, 3 3, 3 0, 0 0))
        [(1, 1), (1, 3), (3, 3), (3, 1), (1, 1)],   # POLYGON ((1 1, 1 3, 3 3, 3 1, 1 1))
    ),
    (
        "2_rel_intersects",
        "Intersects",
        [(0, 0), (0, 3), (3, 3), (3, 0), (0, 0)],   # POLYGON ((0 0, 0 3, 3 3, 3 0, 0 0))
        [(1, 1), (1, 4), (4, 4), (4, 1), (1, 1)],   # POLYGON ((1 1, 1 4, 4 4, 4 1, 1 1))
    ),
    (
        "2_rel_within",
        "Within",
        [(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)],   # POLYGON ((1 1, 1 2, 2 2, 2 1, 1 1))
        [(0, 0), (0, 3), (3, 3), (3, 0), (0, 0)],   # POLYGON ((0 0, 0 3, 3 3, 3 0, 0 0))
    ),
]


def poly_centroid(pts):
    interior = pts[:-1]
    return sum(p[0] for p in interior) / len(interior), sum(p[1] for p in interior) / len(interior)


def plot_relationship(filename, title, poly_a, poly_b):
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.set_title(title, fontsize=11)

    ax.fill(*zip(*poly_a), color="steelblue", alpha=0.4)
    ax.plot(*zip(*poly_a), color="steelblue", linewidth=2)

    ax.fill(*zip(*poly_b), color="firebrick", alpha=0.4)
    ax.plot(*zip(*poly_b), color="firebrick", linewidth=2)

    ax.text(*poly_centroid(poly_a), "A", ha="center", va="center", fontsize=12, fontweight="bold", color="steelblue")
    ax.text(*poly_centroid(poly_b), "B", ha="center", va="center", fontsize=12, fontweight="bold", color="firebrick")

    all_x = [p[0] for p in poly_a + poly_b]
    all_y = [p[1] for p in poly_a + poly_b]
    pad = 0.5
    ax.set_xlim(min(all_x) - pad, max(all_x) + pad)
    ax.set_ylim(min(all_y) - pad, max(all_y) + pad)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(IMAGES_DIR / f"{filename}.png", dpi=150)
    plt.close(fig)
    print(f"Saved {filename}.png")


for filename, title, poly_a, poly_b in RELATIONSHIPS:
    plot_relationship(filename, title, poly_a, poly_b)

print(f"Done — {IMAGES_DIR}")
