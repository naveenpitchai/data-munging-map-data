#import cerberus

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import schema

sfilename = '/Users/naveenpitchai/Naveen/Mission DataScience/Udacity/openstreetwrangling/Working/brooklyn_sample.osm'

PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

SCHEMA = schema.schema

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

MAPPING = {'St': 'Street',
           'St.': 'Street',
           'Ave.': 'Avenue',
           'Av' : 'Avenue',
           'avenue' : 'Avenue',
           'Strt' : 'Street',
           'PKWY': 'Parkway',
           'Ave' : 'Avenue',
           'Rd' : 'Road',
           'Pl' : 'Place',
           'pl' : 'Place',
           'Bl' : 'Boulevard',
           'bl' : 'Boulevard'
          }

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

COUNT = 0

pKeys = []
pVal = []

nonbrook_nodes = []


def handle_problemtags(each_tag, crit, key, value):
    splitted = key.split('.')
    '''if splitted[len(splitted)-1] in crit:
        each_tag['type'] = 'addr'
        each_tag['key'] = splitted[len(splitted)-1]
        each_tag['value'] = value
        if each_tag['key'] == 'housenum':
            each_tag['key'] = 'housenumber'
        return each_tag'''

    if splitted[0] == 'cityracks':
        each_tag['type'] = 'cityracks'
        each_tag['key'] = splitted[len(splitted)-1]
        each_tag['value'] = value

        return each_tag

    else:
        pKeys.append(key)
        pVal.append(value)
        return None


def key_value_uniformity(each_tag):

    key = each_tag['key']
    value = each_tag['value']
    type = each_tag['type']

    if type == 'addr':
        if key == 'city' and value.lower() != 'brooklyn':  #removing all other city except brooklyn
            nonbrook_nodes.append(each_tag['id'])
            return None
        elif key not in ['city', 'housenumber', 'street', 'state', 'postcode', 'country', 'county']:
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

    if type == 'gnis':
        if key == 'County' and value != 'Kings':
            nonbrook_nodes.append(each_tag['id'])
            return None

    return each_tag

def tag_manipulation(element,problem_chars = PROBLEMCHARS, default_tag_type='regular', problemkeys = pKeys, problemvalues = pVal ):

    tags_list = []
    for each in element.iter('tag'):
            each_tag = {}
            each_tag['id'] = int(element.attrib['id'])
            #Key manipulation
            key = each.attrib['k']
            val = each.attrib['v']
            if problem_chars.search(key):  #checking if it is a problematic field & adding
                each_tag = handle_problemtags(each_tag, ['street', 'housenum'], key, val)
                if each_tag is None:
                    continue
            elif key.find(':') > 0: #checing if : is present (if not it will return -1)
                l = key.split(':', 1) #splitting the word based on the given conditions.
                each_tag['type'] = l[0]
                each_tag['key'] = l[1]
                each_tag['value'] = val
            else:
                each_tag['type'] = default_tag_type
                each_tag['key'] = key
                each_tag['value'] = val

            if each_tag['type'] == 'addr' or each_tag['type'] == 'tiger' or each_tag['type'] == 'gnis':
                if key_value_uniformity(each_tag) is None:  #making the keywords uniform for address
                    continue
            tags_list.append(each_tag)

    return tags_list


def update_streetval(nodetags, mapping=MAPPING, count=COUNT):
    for each in nodetags:
        if each['key'].lower() == 'street':
            f = street_type_re.search(each['value'])
            if f.group() in mapping.keys():
                count += 1
                each['value'] = each['value'].replace(f.group(), mapping[f.group()])
    return nodetags

def shape_element(element,problem_chars = PROBLEMCHARS, default_tag_type='regular'):
    #print element.attrib
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []
    if element.tag == 'node':
        node_attribs = element.attrib
        tags = tag_manipulation(element)
        if node_attribs['id'] in nonbrook_nodes:
            return None

    if element.tag == 'way':
        way_attribs = element.attrib
        #below removing any extra attribs other than the one mentioned in the list
        for each in way_attribs.keys():
            if each not in ['id','user','uid','version','timestamp','changeset']:
                del way_attribs[each]
        tags = tag_manipulation(element)
        i = 0
        for each in element.iter('nd'):
            if each.attrib['ref'] not in nonbrook_nodes: #checking non brooklyn nodes and removing
                each_nd = {}
                each_nd['id'] = element.attrib['id']
                each_nd['node_id'] = each.attrib['ref']
                each_nd['position'] = i
                i += 1
                way_nodes.append(each_nd)
            else:
                continue

        for i,each in enumerate(way_nodes):
            if each['node_id'] in nonbrook_nodes:
                del way_nodes[i]
            else:
                continue



    if element.tag == 'node':
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        #validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    el['node_tags'] = update_streetval(el['node_tags'])  #updating the street values here
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    el['way_tags'] = update_streetval(el['way_tags']) #updating the street values here
                    way_tags_writer.writerows(el['way_tags'])

process_map(sfilename, validate=False)