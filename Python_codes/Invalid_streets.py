#finding and updating street types
import csv
import codecs
import pprint
from collections import defaultdict
import re
import xml.etree.cElementTree as ET

sfilename = '/Users/naveenpitchai/Naveen/Mission DataScience/Udacity/openstreetwrangling/Working/brooklyn.osm'


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons", "Broadway"]

MAPPING = {'St': 'Street',
           'St.': 'Street',
           'Ave.': 'Avenue',
           'Ave' : 'Avenue',
           'ave' : 'Avenue',
           'avenue' : 'Avenue',
           'Strt' : 'Street',
           'PKWY': 'Parkway'
          }

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

def check_street_type(streettypes, streetname):

    trans = street_type_re.search(streetname)
    if trans.group() not in expected:
        streettypes[trans.group()] = streetname

defectivestreet_set = set()

def update_streetval_sample(streetname, mapping, defect = defectivestreet_set):

    f = street_type_re.search(streetname)

    if f.group() in mapping.keys():
        defect.add(streetname)
        return streetname.replace(f.group(), mapping[f.group()])

def audit(osmfile):

    file = open(osmfile, 'r')

    st_types = defaultdict(set)

    parsed = ET.parse(osmfile)

    context = ET.iterparse(file, events = ('start',))

    for event, element in context:

        if element.tag == 'way' or element.tag == 'node':

            for each in element.iter('tag'):

                if each.attrib['k'] == 'addr:street':
                    check_street_type(st_types, each.attrib['v'])
                    update_streetval_sample(each.attrib['v'], MAPPING)
    file.close()

    return st_types

print audit(sfilename)