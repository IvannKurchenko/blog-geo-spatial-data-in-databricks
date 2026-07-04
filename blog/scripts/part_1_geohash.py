# Create interactive maps with Folium
from pathlib import Path

from pygeohash.viz import folium_map

MAPS_DIR = Path(__file__).parent.parent / "maps"
MAPS_DIR.mkdir(exist_ok=True)

m = folium_map(center_geohash="u8vxn8")
m.add_geohash("u8vxn8", color="blue")
m.add_geohash_grid(precision=6)

output = MAPS_DIR / "part_1_geohash.html"
m.save(output)