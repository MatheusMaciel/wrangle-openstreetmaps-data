#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

This module contains functions used to audit a osm file.

Attributes:
    street_type_re (:re obj:): Regex compiler to street types.
    node_subtags_count (dict of str: int): Node subtag count.
    node_subtags_unique_values (dict of str: list of str): Node subtag unique values.
    way_subtags_count (dict of str: int): Way subtag count.
    way_subtags_unique_values (dict of str: list of str): Way subtag unique values.

"""

import xml.etree.cElementTree as ET  # Use cElementTree or lxml if too slow
import pprint
import re

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

node_subtags_count = {}
node_subtags_unique_values = {}

way_subtags_count = {}
way_subtags_unique_values = {}

def save_to_file(data, filename):
    with open(filename, 'w') as output:
        for line in data:
            output.write('{}   {}\n'.format(line[0], line[1]))

def save_values_to_file(data, filename):
    with open(filename, 'w') as output:
        for key in data:
            output.write('{}:\n'.format(key))
            for value in data[key]:
                output.write('    {}\n'.format(value))
            
def audit_structure(element, expected_attributes):

    """Verify if a given tag has the expected attributes. If not, describe the differences between the expected attributes and the found attributes.

    Args:
        element (:obj:): cElementTree object. A NODE tag or a WAY tag.
        expected_attributes (list of str): List of expected attributes for the specified tag.

    """
    
    if len(element.attrib) != len(expected_attributes):        
        print "Element {} does not have the right number of attributes. Found: {}, Expected {}".format(element.get('id'), len(element.attrib), len(expected_attributes))
        
    missing_att = expected_attributes - element.attrib.viewkeys()
    extra_att = element.attrib.viewkeys() - expected_attributes
    if len(missing_att) > 0: pprint.pprint("Missing tags: {}".format(','.join(list(missing_att))))
    if len(extra_att) > 0: pprint.pprint("Extra tags: {}".format(','.join(list(extra_att))))
        

def add_node_tag_key(key):

    """Increment the number of times a subtagkey was faound in a NODE tag. Updates the dict node_subtags_count

    Args:
        key (string): Subtag key.

    """
    if key not in node_subtags_count:
        node_subtags_count[key] = 0
    node_subtags_count[key] += 1
    
def add_node_tag_value(key, value):

    """Adds values from selected subtags in node_subtags_unique_values. If the subtag is 'addr:street' adds only the last word from the value.
    
    Args:
        key (string): Subtag key.
        value (string): Subtag value.

    """
    
    if key not in node_subtags_unique_values:
        node_subtags_unique_values[key] = set()
    if key in ['addr:street']:
        street_type = street_type_re.search(value)
        if street_type:
            node_subtags_unique_values[key].add(street_type.group(0).encode('UTF-8'))
    else:
        node_subtags_unique_values[key].add(value.encode('UTF-8'))

        
def audit_node(element, iter):

    """Function designed to audit NODE type tags. The dicts node_subtags_count and node_subtags_unique_values will be update by functions called by this function, 
       depending on the iter parameter.

    Args:
        element (:obj:): cElementTree object. In this case, a NODE tag.
        iter (int): Current iteration of the analysis. 1 for tag counting. 2 for selected tags analysis

    """



    # top5 tags with most occurrences: 'highway','addr:housenumber','addr:street','name','addr:city'
    # problematic tags from top5: 
    target_tags = ['addr:street', 'addr:city', 'addr:state', 'addr:postcode', 'addr:country']
    
    #without 'visible'
    expected_attributes = {'id','lat','lon','version','changeset','user','uid','timestamp'}
    
    audit_structure(element, expected_attributes)
    
    for tag in element.iter("tag"):
        if iter == 1:
            add_node_tag_key(tag.get('k'))
        elif iter == 2:
            if tag.get('k') in target_tags:
                add_node_tag_value(tag.get('k'), tag.get('v'))

def add_way_tag_key(key):

    """Increment the number of times a subtagkey was faound in a WAY tag. Updates the dict way_subtags_count

    Args:
        key (string): Subtag key.

    """
    if key not in way_subtags_count:
        way_subtags_count[key] = 0
    way_subtags_count[key] += 1

    
def add_way_tag_value(key, value):

    """Adds values from selected subtags in way_subtags_unique_values. If the subtag is 'addr:street' adds only the last word from the value.
    

    Args:
        key (string): Subtag key.
        value (string): Subtag value.

    """
    
    if key not in way_subtags_unique_values:
        way_subtags_unique_values[key] = set()
    if key in ['addr:street']:
        street_type = street_type_re.search(value)
        if street_type:
            way_subtags_unique_values[key].add(street_type.group(0).encode('UTF-8'))
    else:
        way_subtags_unique_values[key].add(value.encode('UTF-8'))
        

def audit_way(element, iter):

    """Function designed to audit WAY type tags. The dicts way_subtags_count and way_subtags_unique_values will be update by functions called by this function, 
       depending on the iter parameter.

    Args:
        element (:obj:): cElementTree object. In this case, a WAY tag.
        iter (int): Current iteration of the analysis. 1 for tag counting. 2 for selected tags analysis

    """
    
    target_tags = ['addr:street', 'addr:postcode', 'addr:city', 'addr:state', 'addr:country']    
    
    #without 'visible'
    expected_attributes = {'id','version','changeset','user','uid','timestamp'}
    
    audit_structure(element, expected_attributes)
    
    for tag in element.iter("tag"):
        if iter == 1:
            add_way_tag_key(tag.get('k'))
        elif iter == 2:
            if tag.get('k') in target_tags:
                add_way_tag_value(tag.get('k'), tag.get('v'))

                

# sort dict by value: https://stackoverflow.com/questions/15371691/python-sorted-sorting-a-dictionary-by-value-desc-then-by-key-asc
def audit_osm(osm, iter):

    """Main function used to audit the osm data. This function call all other specific audition funcitons and save the results in files.

    Args:
        osm (string): Path to the osm file.
        iter (int): Current iteration of the analysis. 1 for tag counting. 2 for selected tags analysis

    """
    
    NODE_TAG = 'node'
    WAY_TAG = 'way'
    
    if iter == 1:
        for event, elem in ET.iterparse(osm, events=("start",)):
            if elem.tag == NODE_TAG:
                audit_node(elem, iter)
            elif elem.tag == WAY_TAG:
                audit_way(elem, iter)
            
        sorted_node_subtags_count = sorted(node_subtags_count.items(), key=lambda x: (-x[1], x[0]))
        save_to_file(sorted_node_subtags_count, 'node-tag-count.txt')
        
        sorted_way_subtags_count = sorted(way_subtags_count.items(), key=lambda x: (-x[1], x[0]))
        save_to_file(sorted_way_subtags_count, 'way-tag-count.txt')
    
    elif iter == 2:
        for event, elem in ET.iterparse(osm, events=("start",)):
            if elem.tag == NODE_TAG:
                audit_node(elem, iter)
            elif elem.tag == WAY_TAG:
                audit_way(elem, iter)
    
        save_values_to_file(node_subtags_unique_values, 'node-subtags-unique-values.txt')
        save_values_to_file(way_subtags_unique_values, 'way-subtags-unique-values.txt')