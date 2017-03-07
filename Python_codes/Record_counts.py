import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

sfilename = '/Users/naveenpitchai/Naveen/Mission DataScience/Udacity/openstreetwrangling/Working/brooklyn.osm'

#finding the # of all element

from collections import defaultdict
import re

def count_tags(fname):
    res = defaultdict(int)
    for event, elm in ET.iterparse(fname):
        res[elm.tag] += 1
    return res

element_count = count_tags(sfilename)

print element_count