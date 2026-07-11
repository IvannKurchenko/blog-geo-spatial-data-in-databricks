## Geospatial Data in Databricks — Part 2: Visualisation

### Introduction
The following series of blog posts focuses on working with geospatial data in Databricks.
In the previous two parts of the series, we covered the theoretical basis, `ST_*` and `H3_*` families of functions.
This post forces on other aspect working with the data - visualisation.

As you already got impression from previous posts, working with geo spacial data differs from regular from other 
plain tabular types, especially in terms of debugging. For instance, to investigate why a point:
```
POINT(30.525266 50.449621)
```
lies outside expected polygon:
```
POLYGON ((30.5235417 50.4499077, 30.5243239 50.4504775, 30.5227595 50.4512945, 30.522253 50.4511905, 30.5220898 50.4508967, 30.5235417 50.4499077))
```
both object should be shown on map to. 
This is just a one exemple, which can be generalised - geospatial data as any other sort of data requires tools 
for visualisation for different purposes, starting from low level overview to presenting high level analysis. 
This is what we're going to explore today.
Before we proceed it worth mentioning that there are a lot of excellent online tools for this purpose, however 

That is also available in [Databricks Marketplace](https://docs.overturemaps.org/getting-data/data-mirrors/databricks/) that makes the access way easier because of integrated experience.

## Visualise Longitude and Latitude
Let's start from the simplest case that we can imagine: visualising point described by longitude and latitude.
Databricks offers [inbuilt notebook experience](https://docs.databricks.com/aws/en/dashboards/manage/visualizations/maps#point-map-options
that allows you to show such points on the map.
Lets take for example: 
```sql
SELECT latitude, longitude
FROM VALUES
  (50.450031, 30.524096),
  (50.449396, 30.523313),
  (50.449020, 30.522906),
  (50.447893, 30.522122),
  (50.44629,  30.52167)
AS t(latitude, longitude)
```
Then in the notebook visualisation they can be shown as markers:
![](../blog/images/part_3_0_long_lat_vis.png)

## Visualise `GEOMETRY` and `GEOGRAPHY`
Although with more complicated cases of generic `GEOMETRY` and `GEOGRAPHY` this is more tricky as external tools are required to do a job.
Visualising geographic objects is pretty well discovered problem and you might find a number of tools that does this
pretty well. For instance, you can find list of tools for [geo pandas](https://geopandas.org/en/stable/community/ecosystem.html#visualization).

For the sake of bravity we will keep focus on probably the popular libraries in the area.

### Geo-pandas and Folium
[GeoPandas](https://geopandas.org) similarly to famous Pandas library provides possibility to work with in memory 
dataframes in Apache Arrow format. The notable difference is additional `geometry` column added to a dataframe that
represents a geo object the data associated with. [Folium](https://python-visualization.github.io/folium/latest/index.html)
is another python library that allows render interactive maps from various sources including GeoPandas dataframe

Hence to visualise our Spark dataframe with `GEOMETRY` we need first to convert it to `GeoPandas` dataframe and render
with folium. For visualization example lets take polygon of Kyiv, Ukraine from [Overture maps divisions areas dataset](https://docs.overturemaps.org/schema/reference/divisions/division_area/)

Please, first make sure you have installed [`geopandas`](https://pypi.org/project/geopandas/) and [`folium`](https://pypi.org/project/folium/)

```python
from pyspark.sql import functions as F
import geopandas
import folium

# Select the area of the city of Kyiv into Pandas dataframe with `area` column of WKT format.
pdf = (
    spark
    .table("carto_overture_maps_divisions.carto.division_area")
    .filter((F.col("country") == "UA") & (F.lower(F.col("names.common.en")) == "kyiv"))
    .select(F.expr("st_aswkt(st_geogfromwkb(geom))").alias("area"))
    .toPandas()
)

# Convert WKT column to Geo Pandas geometry
pdf["area_geometry"] = geopandas.GeoSeries.from_wkt(pdf["area"], crs='EPSG:4326')

# Create Geo Pandas DataFrame out from regular Pandas DataFrame
gdf = geopandas.GeoDataFrame(pdf, geometry="area_geometry")

# Create folium map
m = folium.Map(zoom_start=1, tiles="cartodbpositron", width=800, height=400)

# Render GoeoPandas DataFrame on it
folium.GeoJson(gdf).add_to(m)

m
```

So after you you could find map similar to next:
![](../blog/images/part_3_1_geopandas_folium.png)

### Kepler.gl
[Kepler.gl](https://kepler.gl) is another map solution. To render Kyiv's map using Kepler we just need to given it 
Pandas dataframe without specifying additional details:

```python
from pyspark.sql import functions as F
from keplergl import KeplerGl
import pandas as pd

map = KeplerGl()

# Select the area of the city of Kyiv into Pandas dataframe with `area` column of WKT format.
pdf = (
    spark
    .table("carto_overture_maps_divisions.carto.division_area")
    .filter((F.col("country") == "UA") & (F.lower(F.col("names.common.en")) == "kyiv"))
    .select(F.expr("st_aswkt(st_geogfromwkb(geom))").alias("area"))
    .toPandas()
)

map.add_data(pdf, "df_w_wkt")
map
```
That gives us the following map:
![part_3_2_kepler.png](../blog/images/part_3_2_kepler.png)

## Visualise Geo JSON
Similarly, using Kepler.gl it is possible without any additional transformations to visualise GeoJSON right away. 
Lets take previous example of Kyiv region but reconvert WKB to GeoJSON this time:
```python
from pyspark.sql import functions as F
from keplergl import KeplerGl

# Select the area of the city of Kyiv into Pandas dataframe with `area` column of Geo JSON format.
pdf = (
    spark
    .table("carto_overture_maps_divisions.carto.division_area")
    .filter((F.col("country") == "UA") & (F.lower(F.col("names.common.en")) == "kyiv"))
    .select(F.expr("st_asgeojson(st_geogfromwkb(geom))").alias("geojson"))
    .toPandas()
)

map = KeplerGl()
map.add_data(pdf)
map
```

So we can get the following interactive map:
![](../blog/images/part_3_3_kepler_geo_json.png)

## Visualise geo hash
[Geo Hashes](https://en.wikipedia.org/wiki/Geohash) was briefly touched [in the previous part](https://medium.com/gitconnected/geospatial-data-in-databricks-part-1-st-functions-e1e817616442).
For sake of reminder: geo hash is a hierarchical, square based grid  that consists of 18 levels filled using Z-Curve order. 
The geo hash cell defined by alphanumeric string, such as "u8vxn84u".

At the moment of writing both Folium and [Kepler.gl](https://github.com/keplergl/kepler.gl/issues/989) do not provide
geo hash visualisation capabilities out of the box. 

```python
from pyspark.sql import functions as F
from pygeohash.viz import folium_map

# Select the area of the city of Kyiv into Pandas dataframe with `geohash` column of geohash value.
pdf = (
    spark.table("carto_overture_maps_divisions.carto.division_area")
    .filter((F.col("country") == "UA") & (F.lower(F.col("names.common.en")) == "kyiv"))
    .select(F.expr("st_geohash(st_geomfromwkb(geom))").alias("geohash"))
    .toPandas()
)
pdf

# Create and show map with the geo hash 
m = folium_map()
for geohash in pdf['geohash']:
    m.add_geohash(geohash)
m
```
Will give you the following visualisation of Kyiv region expressed in geohash:
![part_3_4_geo_hash.png](../blog/images/part_3_4_geo_hash.png)

## Visualise H3
[H3](https://h3geo.org/) indexes where covered in [the previous part of the series](https://medium.com/gitconnected/geospatial-data-in-databricks-part-2-h3-functions-45b07439fb57).
To refresh our memory on the subject, H3 is geospatial hierachical index that subdivides the globe primarily with hexagons and consists of 16 layers.
Each hexagon cell can be represented with long number that encodes meta such as precision.  

### Kepler.js
Kepler provides dedicated [H3 layer](https://github.com/keplergl/kepler.gl/blob/master/docs/user-guides/c-types-of-layers/j-h3.md)
that makes visualising H3 cell index effortless. All is required to provide pandas dataframe with at least `hex_id`
column which contains as name stands H3 cell ids.

```python
%python
from pyspark.sql import functions as F
from keplergl import KeplerGl

# Convert Kyiv region polygon from WKT to array of H3 cells with resolution 8
pdf = (
    spark
    .table("carto_overture_maps_divisions.carto.division_area")
    .filter(F.lower(F.col("names.common.en")) == "kyiv")
    .select(F.explode(F.expr("h3_coverash3string(geom, 8)")).alias("hex_id"))
    .toPandas()
)

# Visualise Pandas dataframe with `hex_id` string column
map = KeplerGl()
map.add_data(pdf)
map
```
That gives nice interactive map:
![](../blog/images/part_3_5_h3_kepler.png)

### Folium
Unfortunately, at the moment of writing there is no strait wait to draw H3 cells in folium. Off course, it is always
possible to make [extra implementation](https://jens-wirelesscar.medium.com/lhexagone-in-hexagons-uber-h3-map-1566bc412172) but lets keep it simple.
Luckily, Databricks provide a number of [export functions](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-h3-geospatial-functions#export) for H3 
which we can use to convert it to already known formats such as WKT and reuse previously seen tools. 

```python
%python
from pyspark.sql import functions as F
import geopandas
import folium

# Convert Kyiv region polygon from WKT to array of H3 cells with resolution 8 and convert each cell to WKT of cell boundaries
pdf = (
    spark
    .table("carto_overture_maps_divisions.carto.division_area")
    .filter(F.lower(F.col("names.common.en")) == "kyiv")
    .select(F.explode(F.expr("h3_coverash3string(geom, 8)"))).alias("hex_id")
    .select(F.expr("h3_boundaryaswkt(hex_id)").alias("hex_id_wkt"))
    .toPandas()
)

# Convert WKT column to Geo Pandas geometry
pdf["hex_geometry"] = geopandas.GeoSeries.from_wkt(pdf["hex_id_wkt"], crs='EPSG:4326')

# Create Geo Pandas DataFrame out from regular Pandas DataFrame
gdf = geopandas.GeoDataFrame(pdf, geometry="hex_geometry")

# Create folium map
m = folium.Map(zoom_start=1, tiles="cartodbpositron", width=1600, height=400)

# Render GeoPandas DataFrame on it
folium.GeoJson(gdf).add_to(m)

m
```
Which gives us the following visualisation with each cell drawn separately:
![part_3_6_h3_folium.png](../blog/images/part_3_6_h3_folium.png)


## Conclusion
In this part we got a sense how to visualise geo spacial data. This is unlocks a variety of use-cases we can cover,
starting from low level data troubleshooting to building visual for high level analytics.
At the next part we will go over topic partially touched here: open source data.


## References
- https://docs.databricks.com/aws/en/dashboards/manage/visualizations/maps#point-map-options
- https://geopandas.org/en/stable/community/ecosystem.html#visualization