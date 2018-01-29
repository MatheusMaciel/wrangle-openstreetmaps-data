#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

This module contains functions used to fix a osm file.

Attributes:
    postcode_re (:re obj:): Regex compiler to USA postal codes.

"""

import xml.etree.cElementTree as ET  # Use cElementTree or lxml if too slow
import pprint
import re

#postcode regex https://stackoverflow.com/questions/7425860/regular-expression-get-us-zip-code
postcode_re = re.compile(r'.*(\d{5}(\-\d{4})?)$', re.IGNORECASE)

# Como e WAY so existe 'US' defini que o padrao é US
def fix_country(tag):

    fix_dict = {'USA': 'US'}
    if tag.get('v') in fix_dict:
        tag.attrib['v'] = fix_dict[tag.get('v')]

#O padrao é Florida ou FL
def fix_state(tag):
    fix_dict = {'florida': 'Florida', 'F': 'Florida', 'fl': 'Florida', 'Fl': 'Florida', 'FL.': 'Florida'}
    if tag.get('v') in fix_dict:
         tag.attrib['v'] = fix_dict[tag.get('v')]

# http://mentalfloss.com/article/53384/what%E2%80%99s-deal-those-last-4-digits-zip-codes
def fix_postcode(tag):
    postal_code = postcode_re.search(tag.get('v'))
    if postal_code:
        tag.attrib['v'] = postal_code.groups()[0]
    else:
        tag.clear()
    

def fix_node(element):

    """ Function that fixes NODE tags.
    
    Args:
        element (:obj:): cElementTree object. In this case, a NODE tag.

    """
    
    for tag in element.iter("tag"):
        if tag.get('k') == 'addr:country':
            fix_country(tag)
        elif tag.get('k') == 'addr:state':
            fix_state(tag)
        if tag.get('k') == 'addr:postcode':
            fix_postcode(tag)
			
def fix_way(element):

    """ Function that fixes WAY tags.
    
    Args:
        element (:obj:): cElementTree object. In this case, a WAY tag.

    """
    for tag in element.iter("tag"):
        if tag.get('k') == 'addr:country':
            fix_country(tag)
        elif tag.get('k') == 'addr:state':
            fix_state(tag)
        elif tag.get('k') == 'addr:postcode':
            fix_postcode(tag)
			
def fix_data(osm):

    """Main function used to fix the osm data. This function call all other specific audition funcitons and save the results to a file.

    Args:
        osm (string): Path to the osm file.

    """
    
    NODE_TAG = 'node'
    WAY_TAG = 'way'
    
    context = ET.iterparse(osm, events=("start",))
    
    for event, elem in context:
        if elem.tag == NODE_TAG:
            fix_node(elem)
        if elem.tag == WAY_TAG:
            fix_way(elem)
            
    ET.ElementTree(context.root).write('miami_florida_v1.osm') 	