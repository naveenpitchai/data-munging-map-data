# data-munging-map-data
Data munging on Brooklyn map data in python

This data wrangling/munging project takes an OSM file of Brooklyn,USA and
converting in to csv files based on,

nodes
tags on nodes
ways
tags on ways
ways _ nodes

### The data munding included

1. Parsing the features in the osm file using XML iter parse in to python variables
2. Identifying and filtering out area other than brooklyn
3. fixing abbreviated street names in a more common formats
4. keys were modified to be more uniform across the dataset

process_file.py -> contains major chunk of the data munging code. 

project_brooklyn_code.ipynb --> jupyter notebook version for the code added in the 
								code folder.

brooklyn_sample.osm --> a sample file cut out from the much larger OSM file. 