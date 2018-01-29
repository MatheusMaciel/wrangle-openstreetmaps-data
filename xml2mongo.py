#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
This module contains functions used to convert osm data to json and save to MongoDB.
"""

import xml.etree.cElementTree as ET
import json

#some post on stackoverflow
def elementtree_to_dict(element):

    """ Function used to recursively convert a element tree object to a dictionary

    Args:
        element (:obj:): cElementTree object.

    Returns:
        dict: A elementtree object in a JSON formated dict .

    """
    node = dict()
    
    node['xml_tag_type'] = element.tag

    text = getattr(element, 'text', None)
    if text is not None:
        node['text'] = text

    node.update(element.items()) # element's attributes

    child_nodes = {}
    for child in element: # element's children
        child_nodes.setdefault(child.get('k'), []).append( elementtree_to_dict(child))
        
    # convert all single-element lists into non-lists
    for key, value in child_nodes.items():
        #print key, value
        if len(value) == 1:
             child_nodes[key] = value[0]

    node.update(child_nodes.items())

    return node
	
def convert_to_json(osm):

    """ Convert a osm file to a json and save to a file.
    Args:
        osm (string): Path to the osm file.
    """

    NODE_TAG = 'node'
    WAY_TAG = 'way'
    
    context = ET.iterparse(osm, events=("start",))
    
    with open("miami_osm.json", "a") as jsonfile:
        for event, elem in context:
            if elem.tag == NODE_TAG or elem.tag == WAY_TAG:
                jsonfile.write(json.dumps(elementtree_to_dict(elem)))
                jsonfile.write('\n')
				
				
				
				
def save_to_mongo():

    """ Insert a JSON formated OSM in MongoDB.
    """

    import pymongo
	
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.osm
	
    with open('miami_osm.json') as f:
        for line in f:
		    db.miami.insert_one(json.loads(line))
    client.close()