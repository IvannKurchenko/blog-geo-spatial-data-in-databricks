## Geospatial Data in Databricks — Part 2: H3_* functions

### Introduction
The following series of blog posts focuses on working with geospatial data in Databricks.
In the previous two parts of the series we familiarized theoretical basis's and `ST_*` functions.
This post focuses on [`H3_*` family of functions](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-h3-geospatial-functions).

A bit of historical and theoretical context. [H3 index](https://h3geo.org) was initially developed at Uber.
This is discrete grid that subdivides the globe using [hexagons](https://en.wikipedia.org/wiki/Hexagon) mostly, 
although it has several [pentagons](https://en.wikipedia.org/wiki/Pentagon) at the top level.
The grid has hierarchy of 16 levels. At each level cell subdivides on 6 cell, each indexed by a number. Hence, resulting index value can have both numerical and string representations.
The cell at the top of hierarchy (level 0) covers are of approximately 4.25 million square kilometers  and smallest cell are (level 15) covers are about 0.9 square meters.

More about H3 index it is strongly encountered to visit corresponding [learning resources](https://h3geo.org/docs/community/tutorials)
To enrich overview we will use location example from the previous post of [Independence Square in Kyiv, Ukraine](https://www.openstreetmap.org/?mlat=50.45&mlon=30.524167&zoom=15#map=18/50.450519/30.523340) location.


### Importing
Unlike previously considered `GEOMETRY` and `GEOGRAPHY` types, we don't need to perform any (de)serialisation since index values are serializable as such.
Although we still need mechanism to covert values of familiar formats like WKT to indexes. 
This is where we need [import functions](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-h3-geospatial-functions#import)

#### Cover as H3
The most generic methods are:
- [h3_coverash3](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_coverash3) - converts WKT, WKB or GeoJSON into array of H3 cell ids as `BIGINT` type.
- [h3_coverash3string](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_coverash3string) - variation of the previous function, but cell ids are of `STRING` type.

The important detail to understand is that cells returned covers given geo object, in other works area of the cell includes geo object and might be bigger then it.

Let's consider previous polygon example from the previous part and turn it into H3 cells with 9th precision. 

```sql
select h3_coverash3string('POLYGON ((30.5235417 50.4499077, 30.5243239 50.4504775, 30.5227595 50.4512945, 30.522253 50.4511905, 30.5220898 50.4508967, 30.5235417 50.4499077))', 9)
```
Which returns result of the following array: `["891e6384a27ffff","891e6384a2fffff","891e6384a23ffff"]`

That can be visualised strictly on [h3 website](https://h3geo.org/#hex=891e6384a27ffff%2C891e6384a2fffff%2C891e6384a23ffff):
![](images/part_2_0_h3_covers.png)

#### Convert long/lat to H3
Additionally, provided more narrower functions doing similar job: 
- [h3_longlatash3](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_longlatash3) - get cell ID for long/lat and precision;
- [h3_longlatash3string](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_longlatash3string) - version for the string hex; 
 
- [h3_pointash3](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_pointash3) - convert `POINT` geometry from WKT, WKB or GeoJSON to H3 cell id. 
- [h3_pointash3string](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_pointash3string) - version for the string hex; 

#### Polyfill as H3

- [h3_polyfillash3](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_polyfillash3) -
- [h3_polyfillash3string](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_polyfillash3string)

Unlike `h3_coverash3`,  `h3_polyfillash3` cell ids that should be strictly inside the input geo object. Hence the following query returns empty array as result:
```sql
select h3_polyfillash3('POLYGON ((30.5235417 50.4499077, 30.5243239 50.4504775, 30.5227595 50.4512945, 30.522253 50.4511905, 30.5220898 50.4508967, 30.5235417 50.4499077))', 9)
```
Because H3 cell with precision 9 is roughly 100 square meters, which is larger than given polygon.

But higher precision - 12
```sql
select h3_polyfillash3('POLYGON ((30.5235417 50.4499077, 30.5243239 50.4504775, 30.5227595 50.4512945, 30.522253 50.4511905, 30.5220898 50.4508967, 30.5235417 50.4499077))', 9)
```
returns array `["626534952618319871","626534952618348543","626534952617721855","626534952617734143","626534952617717759"]` that lies strictly inside the example polygon:
![](images/part_2_0_h3_polyfill.png)

#### Tesselation
- [h3_tessellateaswkb](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_tessellateaswkb)
Tesselation provide more advanced capabilities. It returns array of structures with additional fields:
- `cellid` - already familiar H3 cell id;
- `core` - boolean flag indicating whether a cell is located on the edge (not core, `false`) or inside (core, value `true`) of the area;
- `chip` - WKB that represents intersection of current cell and given geometry. 

For instance, you can leverage this function to get cell ids that lies on the edge of the polygon: 
```sql
select tessel.cellid
from (select explode(h3_tessellateaswkb('POLYGON ((30.5235417 50.4499077, 30.5243239 50.4504775, 30.5227595 50.4512945, 30.522253 50.4511905, 30.5220898 50.4508967, 30.5235417 50.4499077))', 12)) as tessel)
where tessel.core = false
```
![](images/part_2_1_h3_tessel.png)

#### Safe import
Safe versions of aforementioned functions that would return `null` value instead of raising error:  
- [h3_try_coverash3](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_try_coverash3)
- [h3_try_coverash3string](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_try_coverash3string)
- [h3_try_polyfillash3](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_try_polyfillash3)
- [h3_try_polyfillash3string](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_try_polyfillash3string)
- [h3_try_tessellateaswkb](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_try_tessellateaswkb)

- Which might be especially useful for the dealing with potentially invalid data that should be filtered.  

### Exporting
Consequently, to convert H3 cell id into other formats we can leverage following options.

Convert cell boundaries to GeoJSON, WKT, WKB:
- [h3_boundaryasgeojson](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_boundaryasgeojson)
- [h3_boundaryaswkb](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_boundaryaswkb)
- [h3_boundaryaswkt](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_boundaryaswkt)

Convert cell center to GeoJSON, WKT, WKB:
- [h3_centerasgeojson](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_centerasgeojson)
- [h3_centeraswkb](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_centeraswkb)
- [h3_centeraswkt](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_centeraswkt)

For example for one previously seen cell:
```sql
select h3_boundaryasgeojson(631038552244795391)
```
geo json result would
```json
{"type":"Polygon","coordinates":[[[30.522091699,50.451039847],[30.522027024,50.450958459],[30.522115956,50.450881138],[30.522269562,50.450885206],[30.522334237,50.450966593],[30.522245306,50.451043914],[30.522091699,50.451039847]]]}
```

which visualisation looks following:
![](images/part_2_2_boundary_geojson.png)

### Predicates
As it was described at the beginning, H3 is hierarchical index. Hence we can check this sort of relation between two cells using: 
[`h3_ischildof`](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_ischildof)

For instance take `613024153737363455` cell that covers large area in the center of Kyiv and slightly smaller are of cell `617527753363161087`
![](images/part_2_3_parent_cell.png)

So query:
```sql
select h3_ischildof(617527753363161087, 613024153737363455)
```
returns `true` as well.

### Distancing
Databricks also provides API to measure distances on H3 grid.

- [h3_distance](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_distance)
Gives a distance in number of cells of same resolution of the given cell resolution. NOTE: both cells should have same resolution, otherwise the error will be raised. Alternatively you can use [h3_try_distance](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_try_distance) that returns `null` instead.
For example the distance for two cells of 9th resolution 
```sql
select h3_distance(617527753372073983, 617527753363161087) as distance
```
gives 2. In other words the distance between them is two cells of same 9th resolution.

![](images/part_2_4_distance.png)

Needless to say, that converting such distance to kilometers is tricky, since such distance can be measured in many ways:
between centroids, minimal distance between boundaries or max distance between boundaries. H3 has table of [Edge lengths](https://h3geo.org/docs/core-library/restable/#edge-lengths)
which can be considered cell radius and used for distance measuring. But this should be used on distances where Earth curvature can be neglected, otherwise discrepancies with be too large.

```sql
select h3_distance(617527753372073983, 617527753363161087) * 0.200786148 * 2 * 1000 as distance_m
```
where
- `0.200786148` - edge length for resolution 9.
- `2` - multiplies edge length to get diameter
- `1000` - multiples to conver kilometers into meters

returns distance of 800 meters.
With the following query we can get precise spheroid distance query for between these two cells centroids
```sql
select st_distancespheroid(st_geomfromwkt(h3_centeraswkt(617527753372073983)), st_geomfromwkt(h3_centeraswkt(617527753363161087))) as distance_m
```
That returns result of 673 meters.

- [h3_hexring](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_hexring)
One of H3 advantages over other indexes like [geo hash](https://medium.com/@ivan-kurchenko/e1e817616442) is the ability
to get neighbour cells. This might be especially useful for the use cases such geofencing with certain approximation.
Hex ring method returns neighbour cell by cell id and distance, including given cell id.
Let's consider example of cell id "617527753363161087" which located almost in the center of Kyiv.

![](images/part_2_5_hexring_cell.png)

The query to get neighbours on distance 2:
```sql
select h3_hexring(617527753363161087, 2)
```
returns an array of neighbour cells on distance:
```["617527753372073983","617527753363947519","617527753364471807","617527753363423231","617527767765090303","617527767765352447","617527753382297599","617527753381773311","617527753383084031","617527753390948351","617527753390161919","617527753391734783"]```

This cells' visualisation looks following:
![](images/part_2_6_hexring_cells.png)

- [h3_kring](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_kring)
As you may notice `h3_hexring` returns ring border. For the cases when entier are needs to be covered this method will be helpful:
```sql
select h3_kring(617527753363161087, 2)
```
returns entire are covered with cell on distance of 2: `["617527753363161087","617527753362898943","617527753363685375","617527753383346175","617527753382821887","617527753390686207","617527753364209663","617527753363947519","617527753364471807","617527753363423231","617527767765090303","617527767765352447","617527753382297599","617527753381773311","617527753383084031","617527753390948351","617527753390161919","617527753391734783","617527753372073983"]`
You can compare visualisation with previous result:
![](images/part_2_7_kring_cells.png)

- [h3_kringdistances](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_kringdistances)
Version of `h3_kring` method that returns array of structs with two fields: `cellid` - cell id and `distance` - distance in cells from the given center. 

### Traversal
As it was mentioned at the beginning H3 is hierarchical index. So in this section we will familiarise with part of API
to traver over the hierarchy.
To get list of child cells you can use the following function. 
- [h3_tochildren](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_tochildren)

Let's consider previous example of "617527753363161087" cell with resolution 9.
```sql
select h3_tochildren(617527753363161087, 10)
```
That will give us the following result: `["622031352990302207","622031352990334975","622031352990367743","622031352990400511","622031352990433279","622031352990466047","622031352990498815"]`
Visually it can be represented as following, including "617527753363161087" parent for visibility:

Consequently to get parent cell we can use the following function:
- [h3_toparent](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_toparent)

Using our previous example, the following query 
```sql
select h3_toparent(617527753363161087, 8)
```
returns "613024153737363455" value. Visually both cells looks following:
![](images/part_2_9_to_parent.png)

This perhaps are main methods to consider. Additionally, Databricks provide the following functions for quality of life: 
- [h3_maxchild](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_maxchild) - get child of integer max value.
- [h3_minchild](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_minchild) - get child of integer min value. 
- [h3_resolution](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_resolution) - get resolution of a cell;

### Compaction
Lets imaging you are working with large area covered cell with resolution smaller then area itself.
For instance, we can get such by take large amount of neighbours for a cell:
```sql
select h3_kring(617527753363161087, 6)
```
That results to 127 cells. Visualisation is following:
![](images/part_2_10_compact_original.png)

As you can guess, of them can be "joined" without losing precision. This is where compaction helps:
- [h3_compact](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_compact)
So the query
```sql
select h3_compact(h3_kring(617527753363161087, 3))
```
returns array of 19 elements that can draw as following:

![](images/part_2_10_compact_compacted.png)

Similarly, if array of cells that represents certain are needs to be reverted back from compacted state to certain
resolution the following function helps with this:
- [h3_uncompact](https://docs.databricks.com/aws/en/sql/language-manual/functions/h3_uncompact)

### Conclusion
Today we reviewed how to work with H3  index.

Although we covered main topics some more detailed yet important API's left out of scope:  
- [Conversions](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-h3-geospatial-functions#conversions)
- [Validity](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-h3-geospatial-functions#validity)

H3 indexation is especially usefully for many for solving many geo problems like reverse geocoding, geofencing or similar
when precision can be sacrificed for the benefit of performance.

### References
- https://h3geo.org/docs