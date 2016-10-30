#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import codecs
import re
import xml.etree.cElementTree as ET
import cerberus
import schema
from collections import defaultdict
import pprint

OSM_PATH = "new-york.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons", "Way", "Terrace", "Walk","Alley", "Circle", "Crescent", "Highway", "Lane", "Path", "Plaza", "Real", "Parkway"]

# UPDATE THIS VARIABLE, updated Blvd.
mapping = { "St": "Street",
            "St.": "Street",
            "Ave":"Avenue",
            "Ave.": "Avenue",
            "Rd.": "Road",
            "Blvd.":"Boulevard",
            "Blvd":"Boulevard",
            "Boulvard":"Boulevard",
            "Cres": "Crescent",
            "Dr": "Drive",
            "Ln":"Lane",
            "Ln.":"Lane",
            "Plz": "Plaza",
            "Steet":"Street"}




# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    street_types = defaultdict(set)
    invalid_zipcodes = defaultdict(set)
    for event, elem in context:

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    #print "before", tag.attrib['v']
                    audit_street_type(street_types, tag.attrib['v'])
                    tag.attrib['v']=update_name(tag.attrib['v'], mapping)
                    #print "after", tag.attrib['v']

                if tag.attrib['k'].strip() == "address":
                    #print "before", tag.attrib['v']
                    parts = tag.attrib['v'].split(',')
                    street = parts[0].strip()
                    street=update_name(street,mapping)
                    tag.attrib['v'] = street
                    #print "after", tag.attrib['v']

                if is_zipcode(tag):
                    audit_zipcode(invalid_zipcodes,tag.attrib['v'])
                    tag.set("v", update_zip(tag.attrib['v']))
                    #print tag.attrib['v']


        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""

    if validator.validate(element, schema) is not True:
        print element
        field, errors = next(validator.errors.iteritems())
        print errors

        message_string = "\nElement of type '{0}' has the following errors:\n{1}"

        error_strings = (
            "{0}: {1}".format(k, v if isinstance(v, str) else ", ".join(v))
            for k, v in errors.iteritems()
        )
        raise cerberus.ValidationError(
            message_string.format(field, "\n".join(error_strings))
        )


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)



def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    # Handle secondary tags the same way for both node and way elements

    if element.tag == 'node':
        node_tags = []
        node_attribs = normalize_dict(element.attrib, ['id','user','uid', 'version', 'lat', 'lon', 'timestamp', 'changeset'])
        for child in element:
            tags_value = {}
            tags_value["value"] = child.attrib['v'] if 'v' in child.attrib else "9999999"
            tags_value["id"] = str(element.attrib['id']) if 'id' in element.attrib else "9999999"
            if re.search(PROBLEMCHARS, child.attrib["k"]):
                continue
            if ":" in child.attrib["k"]:
                tags_value["type"] = child.attrib["k"].split(":", 1)[0] if "k" in child.attrib else "9999999"
                tags_value["key"] = child.attrib["k"].split(":", 1)[-1] if "k" in child.attrib else "9999999"
            if ":" not in child.attrib["k"]:
                tags_value["key"] = child.attrib["k"] if "k" in child.attrib else "9999999"
                tags_value["type"] = "regular"
            node_tags.append(tags_value)
        return {'node': node_attribs, 'node_tags': node_tags}



    if element.tag == 'way':
        way_tags = []
        way_attribs = normalize_dict(element.attrib, ['id', 'user', 'uid', 'version', 'timestamp', "changeset"])
        tags_value = {}
        tags_value["id"] = str(element.attrib['id'])
        node_value = {}
        node_value['id'] = str(element.attrib['id'])
        position = 0
        for child in element:
            tags_value = {}
            tags_value["id"] = element.attrib['id']
            node_value = {}
            node_value['id'] = element.attrib['id']
            if child.tag == "nd":
                node_value['node_id']=child.attrib['ref']
                node_value['position'] = position
                position +=1
                way_nodes.append(node_value)
                #print way_nodes
            if child.tag == "tag":
                tags_value["value"] = child.attrib['v']
                if re.search(PROBLEMCHARS, child.attrib["k"]):
                    continue
                if ":" in child.attrib["k"]:
                    tags_value["type"] = child.attrib["k"].split(":", 1)[0]
                    tags_value["key"] = child.attrib["k"].split(":", 1)[-1]
                if ":" not in child.attrib["k"]:
                    tags_value["key"] = child.attrib["k"]
                    tags_value["type"] = "regular"
                way_tags.append(tags_value)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': way_tags}


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def update_name(name, mapping):
    name = name.title()
    #print name.rsplit(" ", 1)[-1]
    words = name.split()
    for w in range(len(words)):
        if words[w] in mapping:
            if words[w].lower() not in ['suite', 'ste.', 'ste']:
            # For example, don't update 'Suite E' to 'Suite East'
                words[w] = mapping[words[w]]
                name = " ".join(words)
    return name

def normalize_dict(input_dict, keys):
    output_dict = {}
    for key in keys:
        output_dict[key] = input_dict[key] if key in input_dict else "9999999"
    return output_dict

def audit_zipcode(invalid_zipcodes, zipcode):
    twoDigits = zipcode[0:2]
    if twoDigits != "10" or twoDigits != "11" or not twoDigits.isdigit() or len(zipcode)>5:
        try:
            invalid_zipcodes[twoDigits].add(zipcode)
        except TypeError:
            print zipcode
    return invalid_zipcodes

def is_zipcode(elem):
    return (elem.attrib['k'] == "addr:postcode")

def update_zip(zipcode):
    try:
        zipcode = (re.findall(r'\d+', zipcode))[0]
    except IndexError:
        zipcode = "10000"
    return zipcode

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

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])

                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)
