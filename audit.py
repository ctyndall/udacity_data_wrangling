"""
Your task in this exercise has two steps:

- audit the OSMFILE and change the variable 'mapping' to reflect the changes needed to fix 
    the unexpected street types to the appropriate ones in the expected list.
    You have to add mappings only for the actual problems you find in this OSMFILE,
    not a generalized solution, since that may and will depend on the particular area you are auditing.
- write the update_name function, to actually fix the street name.
    The function takes a string with street name as an argument and should return the fixed name
    We have provided a simple test so that you see what exactly is expected
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import sys
import json

OSMFILE = "example.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
street_type_re_sp = re.compile(r'\A\S+\.?', re.IGNORECASE)  # must use re.match instead of re.search

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Hill", "Bay", "Cove", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Circle", "Way", "Terrace", "Ridge", "Corte"]

expected_sp = ["Avenida", "Camino", "Caminito", "Calle", "Corte", "El", "Paseo", "Plaza", "Sitio", "Via", "Vista"]

mapping = { "Rd":"Road", #1 instance
            "Ave.": "Avenue",  # 1 instance
            "Py": "Parkway", # 1
            "Blvd.":"Boulevard", # 1
            "St": "Street", # 2 instances
            "Ct": "Court",  # 1 instance
            "Dr": "Drive", # 4 instances
            "Blvd": "Boulevard",  # 1
            }


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    m_sp = street_type_re_sp.match(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_type_sp = m_sp.group().strip()
            if street_type_sp not in expected_sp:  # added extra check for spanish streen names
                street_types[street_type].add(street_name)  # default street_type and not the spanish stree_type


def is_street_name(elem, elem_type):
    if elem_type == 'node':
        return (elem.attrib['k'] == "addr:street")
    elif elem_type == 'way':
        return (elem.attrib['k'] == "street" or elem.attrib['k'] == 'addr:street')  #some way tags use addr:street

def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag, elem.tag):
                    audit_street_type(street_types, tag.attrib['v'])
        root.clear()
    osm_file.close()
    return street_types


def update_name(name, mapping):
    m = street_type_re.search(name)
    street_type = m.group()
    if street_type in mapping:
        better_name = re.sub(street_type_re, mapping[street_type], name)
        return better_name
    else:
        return False


def test(fn):
    #st_types = audit(OSMFILE)
    st_types = audit(fn)
   # print st_types
    with open('output.txt', 'w') as outfile:
        for key in st_types:
            outfile.write(key + "," + str(list(st_types[key])) + "\n")
            # assert len(st_types) == 3
    # pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            if better_name:
                print name, "=>", better_name
    #         if name == "West Lexington St.":
    #             assert better_name == "West Lexington Street"
    #         if name == "Baldwin Rd.":
    #             assert better_name == "Baldwin Road"


if __name__ == '__main__':
    test(sys.argv[1])