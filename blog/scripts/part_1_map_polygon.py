from pathlib import Path
import folium

MAPS_DIR = Path(__file__).parent.parent / "maps"
MAPS_DIR.mkdir(exist_ok=True)

# WKT: POLYGON ((30.5235417 50.4499077, 30.5243239 50.4504775, 30.5227595 50.4512945, 30.522253 50.4511905, 30.5220898 50.4508967, 30.5235417 50.4499077))
# WKT uses (lon lat), folium expects [lat, lon]
locations = [
    [50.4499077, 30.5235417],
    [50.4504775, 30.5243239],
    [50.4512945, 30.5227595],
    [50.4511905, 30.522253],
    [50.4508967, 30.5220898],
    [50.4499077, 30.5235417],
]

m = folium.Map(location=[50.4507, 30.5232], zoom_start=17)

folium.Polygon(
    locations=locations,
    color="crimson",
    weight=3,
    fill_color="crimson",
    fill_opacity=0.3,
    fill=True,
    tooltip="Independence Square, Kyiv",
).add_to(m)

# WKT: POINT(30.5228081 50.4506574)
folium.Marker(
    location=[50.4506574, 30.5228081],
    tooltip="POINT(30.5228081 50.4506574)",
    icon=folium.Icon(color="blue"),
).add_to(m)

output = MAPS_DIR / "part_1_polygon.html"
m.save(output)
print(f"Saved to {output}")
