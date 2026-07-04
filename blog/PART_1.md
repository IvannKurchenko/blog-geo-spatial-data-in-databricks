## Geospatial Data in Databricks — Part 1: ST_* functions

### Introduction
The following series of blog posts focuses on working with geospatial data in Databricks.
In the previous part of the series we outlined theoretical basis's that will be references heavily in this part. 
In this pos we will get more familiar with [`ST_*` family of functions](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-st-geospatial-functions-alpha)

A bit of historical context. Spatial functions for SQL first introduced in "ISO 19125-2 (SFA-SQL)" standard in "SQL/MM Spatial" section.
`ST` prefix original meant Spatial and Temporal. Nowadays, this standard is implemented by various vendors, so don't 
wonder to see same ST function signature in other SQL implementation.

Overall Databricks provides implementation for around spatial 80 functions. To avoid overwhelming, we will focus on some 
portion of them split by topic.

To keep overview more grounded, lets take as an example location [Independence Square in Kyiv, Ukraine](https://www.openstreetmap.org/?mlat=50.45&mlon=30.524167&zoom=15#map=18/50.450519/30.523340).  

Note that ST_ functions are supported in Databricks Runtime version 17.1 and higher.

### Types: GEOMETRY and GEOGRAPHY
https://docs.databricks.com/aws/en/sql/language-manual/data-types/geometry-type
https://docs.databricks.com/aws/en/sql/language-manual/data-types/geography-type
These types are not serializable per se. In other words you can't write data frame with GEOGRAPHY or GEOMETRY type
into Delta table or other location.
In [the previous post](https://medium.com/p/01cb2ef77992/edit) the "Well Known" markup language was introduced for 
that purpose. So lets start with that.

### Deserialisation
Prior to any manipulation with geo data in dataframe wee need to be able to read it. So this will be first portion
of functions to get familiar with - deserializing "Well Known" values into GEOMETRY and GEOGRAPHY types.
Databricks provides functions that covers a whole combination of source formats (WKT, WKB, EWKT, EWKB) and target
types (GEOMETRY and GEOGRAPHY).

- [`st_geogfromwkt`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_geogfromwkt)
- [`st_geogfromwkb`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_geogfromwkb)
- [`st_geogfromewkt`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_geogfromewkt)

- [`st_geomfromewkb`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_geomfromewkb)
- [`st_geomfromewkt`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_geomfromewkt)
- [`st_geomfromwkb`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_geomfromwkb)
- [`st_geomfromwkt`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_geomfromwkt)

For instance to WKT conversion looks following
```sql
select st_geogfromwkt('POLYGON ((30.5235417 50.4499077, 30.5243239 50.4504775, 30.5227595 50.4512945, 30.522253 50.4511905, 30.5220898 50.4508967, 30.5235417 50.4499077))') as polygon
```

### Serialisation
Consequently, To store these types they are needed to be converted in one of "Well Known" formats correspondingly with a help
of one of these functions:

- [`st_asewkb`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_asewkb)
- [`st_asewkt`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_asewkt)
- [`st_aswkb`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_aswkb)
- [`st_aswkt`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_aswkt)

Taking previous example, we can convert polygon geography back to EWKT string:
```
select st_asewkt(st_geogfromwkt('POLYGON ((30.5235417 50.4499077, 30.5243239 50.4504775, 30.5227595 50.4512945, 30.522253 50.4511905, 30.5220898 50.4508967, 30.5235417 50.4499077))')) as polygon_ewkt
```
That returns EWKT representation:
`SRID=4326;POLYGON((30.5235417 50.4499077,30.5243239 50.4504775,30.5227595 50.4512945,30.522253 50.4511905,30.5220898 50.4508967,30.5235417 50.4499077))`
The only noticeable difference is explicit SRID added at the beginning.

### Geo JSON
GeoJson as it was reviewed in [the previous part](https://medium.com/@ivan-kurchenko/01cb2ef77992) one of the open
formats for working with spatial data. Its support is provided via the following API:

- [`st_geogfromgeojson`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_geogfromgeojson)
- [`st_geomfromgeojson`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_geomfromgeojson)
- [`st_asgeojson`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_asgeojson)

For example, the following query to conver example polygon to GeoJSON: 
```sql
select st_asgeojson(st_geogfromwkt('POLYGON ((30.5235417 50.4499077, 30.5243239 50.4504775, 30.5227595 50.4512945, 30.522253 50.4511905, 30.5220898 50.4508967, 30.5235417 50.4499077))'))
```
that gives the following result:
```json
{"type":"Polygon","coordinates":[[[30.5235417,50.4499077],[30.5243239,50.4504775],[30.5227595,50.4512945],[30.522253,50.4511905],[30.5220898,50.4508967],[30.5235417,50.4499077]]]}
```
Pay attention that this value is [`Geometry`](https://datatracker.ietf.org/doc/html/rfc7946#section-3.1) object type from GeoJSON.
So to construct complete GeoJSON the result needs to be wrapped into [`Feature`](https://datatracker.ietf.org/doc/html/rfc7946#section-3.2) or [`FeatureCollection`](https://datatracker.ietf.org/doc/html/rfc7946#section-3.3).

### Distance
After we have spatial types in memory we can proceed to some analytical tasks, such as distance measuring.
The following set of functions can help with that:
- [`st_distance`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_distance)
- [`st_distancesphere`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_distancesphere)
- [`st_distancespheroid`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_distancespheroid)
- [`st_dwithin`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_dwithin)

For more specific, example lets consider measuring distance between previously considered independence square and 
[Market Square in Lviv, Ukraine](https://www.openstreetmap.org/#map=18/49.841913/24.030694).

Let's first consider `st_distance`. Pay attention that this functions works only with `GEOMETRY` type which means
that surface curvature won't be taken into account. Additionally, the distance is returned in the same unit as geometry
defined, hence in degrees. So to get approximate distance in kilometers the result needs to be [multiplied after this by 111](https://stackoverflow.com/questions/1253499/simple-calculations-for-working-with-lat-lon-and-km-distance)
```sql
select st_distance( 
    st_geomfromwkt('POINT(24.0317835 49.8419343)'),
    st_geomfromwkt('POINT(30.5235417 50.4499077)')
) * 111 as distance
```
Which gives a result of 723 KM. As you might guess this value is not very accurate due to nature of calculation.

Another option is to use `st_distancesphere` that returns distance in meters on the sphere which radius is mean radius of
WGS84 ellipsoid. This function  is more restrictive and works with only with `GEOMETRY` points.
```sql
select st_distancesphere( 
    st_geomfromwkt('POINT(24.0317835 49.8419343)'),
    st_geomfromwkt('POINT(30.5235417 50.4499077)')
) / 1000 as distance
```
Which returns 467 kilometers. 

The last one function to review is `st_distancespheroid` that returns geodesic distance on WGS84 ellipsoid.
```sql
select st_distancespheroid( 
    st_geomfromwkt('POINT(24.0317835 49.8419343)'),
    st_geomfromwkt('POINT(30.5235417 50.4499077)')
) / 1000 as distance
```
That results to 468 kilometers.
Natual question arise "which one to choose when?". The order from least performant and more accurate goes:
`st_distancespheroid`, `st_distancesphere` and `st_distance`.

### Relations
Another set of operation that we will review is determine relation between spatial objects. 
It might be useful for various analytical cases, such as [geofencing](https://en.wikipedia.org/wiki/Geofence)
The following set of functions gives this possibility.

- [`st_touches`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_touches)
- [`st_within`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_within)
- [`st_intersects`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_intersects)
- [`st_covers`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_covers)
- [`st_contains`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_contains)
- [`st_disjoint`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_disjoint)

All these functions heavily utilise "DE-9IM" model reviewed in [the previous part](https://medium.com/@ivan-kurchenko/01cb2ef77992).
For instance, we can check whether a single point is inside previously reviewed polygon:
```sql
select st_contains(
    st_geomfromwkt('POLYGON((30.5235417 50.4499077, 30.5243239 50.4504775, 30.5227595 50.4512945, 30.522253 50.4511905, 30.5220898 50.4508967, 30.5235417 50.4499077))'),
    st_geomfromwkt('POINT(30.5228081 50.4506574)')
) as contains
```
which is true as you can verify from the following map:
![img.png](../blog/images/part_1_0_contains_polygon.png)

### Geo Hashing
[Geo Hash](https://en.wikipedia.org/wiki/Geohash) is part of wider topic of geospatial index, which is out of the scope 
of current post. By the way, H3 that will be covered in the next part is a part of this topic.
Working with geospatial data might be slow and cumbersome while solving some problems such as [reverse geocoding](https://en.wikipedia.org/wiki/Reverse_geocoding).
Imaging working traffic data when we need to understand mileage driven per country. Such dataset will be more
likely describe location via longitude and latitude value. To convert this location into more human-readable representation
such as name of country we execute `st_contains` over each region. On large scale, this operation will be too slow, and 
we would need faster alternative. This is a case when Geo Hash or other spatial indexes shines. 

Geo Hash subdivides entire glob in hierarchical manner in to number of square. Each square has distinct alphanumeric value
in scope of hierarchy. As a result, each location can be encoded into a string with length up to 12 characters depending
on precision. 
Resulting string can be using as key which is way more suitable for operations like `JOIN`.

Databricks provides the following set of operations to work with geo hashing:
- [`st_geohash`](https://docs.databricks.com/gcp/en/sql/language-manual/functions/st_geohash)
- [`st_geomfromgeohash`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_geomfromgeohash)
- [`st_pointfromgeohash`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_pointfromgeohash)

For instance, to conver 

```sql
select st_geohash(st_geomfromwkt('POINT(30.5228081 50.4506574)'), 6) as geohash
```

`st_geohash` receives precision as second argument. You can think of precision as hierarchy level from top to bottom.
In our example precision of 6 covers area about 1.2 km by 0.6 km.

The query above returns a value 'u8vxn8' which can be visualised as following:
![](../blog/images/part_1_0_contains_polygon.png)

## Conclusion
In this part we covered main functions of `ST_*` family. However, there are operations left out-of-scope like
geometry manipulaitons via [`st_rotate`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_rotate) 
or [`st_scale`](https://docs.databricks.com/aws/en/sql/language-manual/functions/st_scale). In the upcoming part, our 
focus will shift to [H3](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-h3-geospatial-functions) functions
and H3 spacial index as such.


## References
- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-st-geospatial-functions-alpha
- https://en.wikipedia.org/wiki/Simple_Features#Spatial
- https://dekart.xyz/blog/st_-prefix-in-sql-a-tale-of-time-space-and-standardization/
- https://spark.apache.org/docs/4.2.0-preview4/sql-ref-geospatial-types.html
- https://www.databricks.com/blog/introducing-spatial-sql-databricks-80-functions-high-performance-geospatial-analytics
