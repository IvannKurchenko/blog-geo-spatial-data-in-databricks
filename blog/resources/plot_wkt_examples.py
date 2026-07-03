from pathlib import Path
import matplotlib.pyplot as plt

IMAGES_DIR = Path(__file__).parent.parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)

# POINT (0 0)
fig, ax = plt.subplots(figsize=(4, 4))
ax.set_title("POINT (0 0)")
ax.scatter(0, 0, color="firebrick", s=100, zorder=3)
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_aspect("equal")
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(IMAGES_DIR / "1_point.png", dpi=150)
plt.close(fig)

# LINESTRING (0 0, 1 1, 2 2)
line = [(0, 0), (1, 1), (2, 2)]
lx, ly = zip(*line)
fig, ax = plt.subplots(figsize=(4, 4))
ax.set_title("LINESTRING (0 0, 1 1, 2 2)")
ax.plot(lx, ly, color="navy", linewidth=2)
ax.scatter(lx, ly, color="navy", s=40, zorder=3)
ax.set_aspect("equal")
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(IMAGES_DIR / "1_linestring.png", dpi=150)
plt.close(fig)

# POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))
polygon = [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]
px, py = zip(*polygon)
fig, ax = plt.subplots(figsize=(4, 4))
ax.set_title("POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))")
ax.fill(px, py, color="steelblue", alpha=0.4)
ax.plot(px, py, color="steelblue", linewidth=2)
ax.set_aspect("equal")
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(IMAGES_DIR / "1_polygon.png", dpi=150)
plt.close(fig)

print(f"Saved to {IMAGES_DIR}")
