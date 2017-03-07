#OpenStreetMap Data Case Study
---

## Map Area:
---

Brooklyn, NYC, United States

https://mapzen.com/data/metro-extracts/metro/brooklyn_new-york/

Chose the Brooklyn area to know a bit about what New York city has in store and I live near Brooklyn. Also this area included a bit of other
boroughs and New Jersey, which provides a bit more challenge to clean the data.


## Problems in the Map Area:
-------

Analyzing the sample data extracted from the main data revealed the problems listed below,

* Of course the major problem with this data is the inclusion of data for other boroughs and the neighbor state NJ.Stating few examples below,

  Few data points are City, County, Address, Postal code

  Data containing information for Hoboken, NJ

  ```XML
  <tag k="addr:city" v="Hoboken"/>
  <tag k="created_by" v="Merkaartor 0.11" />
  <tag k="addr:street" v="Washington St" />
  ```

  Neighboring boroughs

  ```XML
  <tag k="highway" v="motorway_link" />
  <tag k="tiger:cfcc" v="A63" />
  <tag k="tiger:tlid" v="59731500" />
  <tag k="tiger:county" v="Queens, NY" />
  ```

* Abbreviated street names like: **Atlantic Ave, 305 Schermerhorn St.**


* All the key tags did not have the same format of colon in between them.

  **addr:housenumber**      almost all of keys represented this way.

  **cityracks.housenum**    some of them or represented this way.


* Non uniform tag keys like, (housenum & housenumber), (city & city_2)

### Out of Brooklyn data points:

To tackle this i had to check and remove values for following entities
```
City
County
PostalCode
State
```
Below is the a snippet of code on how it was done

```python
if type == 'addr':      
        if key == 'city' and value.lower() != 'brooklyn':
            nonbrook_nodes.append(each_tag['id'])
            return None
elif key == 'postcode' and value[0:3] != '112':
            return None
        elif key == 'state' and value != 'NY':
            if value != 'NJ':
                each_tag['value'] = 'NY'
                return each_tag
            else:
                nonbrook_nodes.append(each_tag['id'])
                return None

if type == 'tiger':
   if key == 'county' and value[0:5].lower() != 'kings':
        nonbrook_nodes.append(each_tag['id'])
        return None
```

Additionally the out of brooklyn data has been taken care for other data points (nodes, ways, way_tags)

```python
if node_attribs['id'] in nonbrook_nodes:
            return None
if way_attribs['id'] in nonbrook_nodes:
            return None
```

### Abbreviated street names

Below code was used to get the overview of different non uniform street names

```python
def check_street_type(streettypes, streetname):
    trans = street_type_re.search(streetname)
    if trans.group() not in expected:   
        streettypes[trans.group()] = streetname
```

Based on the data found populated the mapping variable and following code is used to correct the street names,

```python
def update_streetval(nodetags, mapping=MAPPING, count=COUNT):
    for each in nodetags:
        if each['type'] == 'addr' and each['key'].lower() == 'street':        
            f = street_type_re.search(each['value'])           
            if f.group() in mapping.keys():   
                count += 1
                each['value'] = each['value'].replace(f.group(), mapping[f.group()])    
    return nodetags
```

### Problem tags with different delimiter

Important information on bicycle racks has been represented with a different delmited and below is how those were taken in to account,

```python
def handle_problemtags(each_tag, crit, key, value):   
    splitted = key.split('.')
    if splitted[0] == 'cityracks':     
        each_tag['type'] = 'cityracks'
        each_tag['key'] = splitted[len(splitted)-1]
        each_tag['value'] = value
        return each_tag
    else:
        pKeys.append(key)
        pVal.append(value)
        return None
```

### Non Uniform tags

The tags with different naming convention than the usual were on the lower side, so decided to remove them with the below code,

```python
  std_tags = ['city', 'housenumber', 'street', 'state', 'postcode', 'country', 'county']
    elif key not in std_tags:
        return None
```

### Non Brooklyn gnis data

The gnis data had information out of Brooklyn and below code was used to clean those

```python
if type == 'gnis':
        if key == 'County' and value != 'Kings':
            print 'removing others'
            nonbrook_nodes.append(each_tag['id'])
            return None
```

## Data Overview
---

### File Sizes
_____

    brooklyn.osm ---------- 667.8 MB
    project_brooklyn.db --- 422.8 MB
    nodes.csv ------------- 232.5 MB
    nodes_tags.csv -------- 7.8   MB
    ways.csv -------------- 33.1  MB
    ways_tags.csv --------- 81.5  MB
    ways_nodes ------------ 84.2  MB


### Record Counts
____

#### NODES = 2,490,973

```sql
select count(*) as count from nodes;
```

#### NODES_TAGS = 220,519

```sql
select count(*) as count from nodes_tags;
```

#### WAYS = 491,790

```sql
select count(*) as count from ways;
```

#### WAYS_TAGS = 2,494,921

```sql
select count(*) as count from ways_tags;
```

#### WAYS_NODES = 3,504,154

```sql
select count(*) as count from ways_nodes;
```
--------

## More Details on the selected data
---


### No. of Distinct users  ---- 1310

```sqlite
select count(distinct user) from nodes;
```


### Top ten contributors

```sql
select distinct user from nodes;
```

```
Rub21_nycbuildings | 1,498,618
ingalls_nycbuildings | 330,904
ediyes_nycbuildings | 170,019
celosia_nycbuildings | 106,916
lxbarth_nycbuildings | 69,913
ewedistrict_nycbuildings | 34,658
ingalls | 25,738
smlevine | 21,112
robgeb | 18,688
woodpeck_fixbot | 12,229
```

### Top ten amenities in the city

```sql
select id, key, value, type , count(*) as count
from nodes_tags where key = 'amenity'
group by value
order by count desc;
```
```sql
bicycle_parking | 2812
restaurant | 931
place_of_worship | 367
school | 361
cafe | 310
bench | 267
bicycle_rental | 265
bar | 190
fast_food | 185
fire_station | 120
```

## Additional Data statistics
--------

### Bicycle racks

The bike scene in NYC is really good and one of the preferred method of travel.

It can be seen from the data that Brooklyn has lot of bike racks and below are some statistics concerning those

```sql
select count(*) as count from nodes_tags where type = 'cityracks' and key = 'street';
```

There are **2611** total bicycle racks in the Brooklyn area

### Top ten streets based on the rack count

```sql
select id, type, key,  value, count(*) as count from nodes_tags
where type = 'cityracks' and
key = 'street'
group by value
order by count desc
limit 10;
```

```
Street Name | Rack_count
Atlantic Avenue | 103
Broadway | 84
Hudson Street | 62
2nd Avenue | 50
Bedford Avenue | 48
5th Avenue | 47
Myrtle Avenue | 42
Court Street | 37
4th Avenue | 36
E 11th Street | 35
```

### Top ten Cuisines

```sql
select value, count(*) as count from nodes_tags where
key = 'cuisine'
group by value
order by count desc;
```

```
Cuisine | Count
pizza | 75
coffee_shop | 72
mexican | 58
american | 55
italian | 55
burger | 51
chinese | 42
sandwich | 29
french | 27
japanese | 22
```

### Ways with bicycle lanes

There are **162** ways with dedicated bicylce lane

```sql
select distinct value from ways_tags where id in (select id from ways_tags where type = 'cycleway')
and key = 'name'
```

### Streets with most restaurants with particular cuisine

Pizza restaurants in this case

```sql
select wt.value, count(*) as count from
nodes_tags wt join (select * from nodes_tags where key = 'cuisine') cuisine on
wt.id = cuisine.id
where wt.key = 'street' and
cuisine.value = 'pizza'
group by wt.value
order by count desc
```

```
Street_name | Count
East 14th Street | 5
5th Avenue | 3
Court Street | 3
Front Street | 2
West Houston Street | 2
```

## Additional Ideas
-----------

### Nodes with out any information

There are about **2418139** nodes which do not have any tag information which is
whopping **97%** of the complete data.

```sql
select * from nodes nd left join nodes_tags nt on
nd.id = nt.id
where nt.id is Null
```

There were only **971** users who provided some useful tag information out of **1310**,
which is

```sql
select count(distinct user) as user_count from nodes where id in
(select distinct nd.id from nodes nd inner join nodes_tags nt on
nd.id = nt.id);
```

In conclusion about 74% of users provided all the tag information for nodes.

Users can be urged to put in more tag information to know places/features of any city.



### Key & Type guidelines

Various values of Keys and types are used to represent the same features like, county & County, housenumber & housenumber

A set of guidelines for users, who enter data, to follow for most commonly used keys in a Metropolitan would help in data
uniformity greatly.

## Conclusion
--------

The biggest challenge in this data set was to filter out the data which does not concern Brooklyn and feature wise this dataset does not
provide complete details and has a lot of room to improve. The quality of the dataset can be improved by imposing more guidelines and standards for the users to follow. That said, once parsed and cleaned, the dataset do provide some really meaningful information pertaining to understand the area of our interest.
