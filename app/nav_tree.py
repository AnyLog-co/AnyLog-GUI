'''
By using this source code, you acknowledge that this software in source code form remains a confidential information of AnyLog, Inc.,
and you shall not transfer it to any other party without AnyLog, Inc.'s prior written consent. You further acknowledge that all right,
title and interest in and to this source code, and any copies and/or derivatives thereof and all documentation, which describes
and/or composes such source code or any such derivatives, shall remain the sole and exclusive property of AnyLog, Inc.,
and you shall not edit, reverse engineer, copy, emulate, create derivatives of, compile or decompile or otherwise tamper or modify
this source code in any way, or allow others to do so. In the event of any such editing, reverse engineering, copying, emulation,
creation of derivative, compilation, decompilation, tampering or modification of this source code by you, or any of your affiliates (term
to be broadly interpreted) you or your such affiliates shall unconditionally assign and transfer any intellectual property created by any
such non-permitted act to AnyLog, Inc.
'''

import json
import sys
from json.decoder import JSONDecodeError

class Details():
    def __init__(self, names, keys, values):
        self.names = names       # The list of the attributes in the config file
        self.keys = keys       # The list of the attributes in the JSON file
        self.values = values      # The list of values

# -----------------------------------------------------------------------------------
# Objects to describe a tree hierarchy used in output_tree.html
# -----------------------------------------------------------------------------------
class TreeNode():

    def __init__(self, **params):

        self.name = None  # The root node
        self.is_anchor = False          # The root node
        self.id = None                  # The ID of the entry
        self.first_child = False        # The entry is at the top of the list
        self.last_child = False         # The entry is at the end of the list
        self.key = None                 # Key to display
        self.value = None               # The value to display
        self.children = []
        self.with_children = False
        self.details = None

        # Setup params
        for key, value in params.items():
            setattr(self, key, value)

    # -----------------------------------------------------------------------------------
    # Add a child to the list of nodes
    # -----------------------------------------------------------------------------------
    def add_child(self, **params):
        '''
        Add a new child to thee current node, return the child
        '''

        if not len(self.children):
            params['first_child'] = True       # First child
        else:
            self.children[-1].last_child = False    # Remove last chaild from the previously set child

        params['last_child'] = True

        child_node = TreeNode( **params )

        self.children.append( child_node )
        self.with_children = True

        return child_node

    # -----------------------------------------------------------------------------------
    # Add the children resulting from a query of the parent usinf the method - get_path_info(...)
    # -----------------------------------------------------------------------------------
    def add_path_children(self, list_columns, list_keys, table_rows):
        '''
        Create children to the specifird node
        :param list_columns:    The attribute names retrieved from the config file
        :param list_keys:       The keys of the policies
        :param table_rows:      The children
        :return:
        '''

        # Find if id and name are available
        id_offset = list_keys.index('id')
        name_offset = list_keys.index('name')

        for entry in table_rows:
            params = {}

            details = Details(list_columns, list_keys, entry)
            params['details'] = details     # The Details class in a node

            # Get the name and ID from the data
            if id_offset >= 0:
                params['id'] = entry[id_offset]

            if name_offset >= 0:
                params['name'] = entry[name_offset]

            self.add_child( **params )


# -----------------------------------------------------------------------------------
# Given a node and a list of keys - return the node addressed by the keys
# -----------------------------------------------------------------------------------
def get_current_node(current_node, keys_list, offset):
    '''
    Return the node addresssed by the key
    :param current_node:
    :param keys_list:
    :param offset:
    :return:
    '''

    if current_node.with_children:
        for child in current_node.children:
            if child.id:
                # The child has an ID - test the ID
                if child.id == keys_list[offset]:
                    if offset == (len(keys_list) - 1):
                        # The entire key was validated
                        return child
                    else:
                        return get_current_node(child, keys_list, offset + 1)
            elif child.name:
                # The child has a name - test the name
                if child.name == keys_list[offset]:
                    if offset == (len(keys_list) - 1):
                        # The entire key was validated
                        return child
                    else:
                        return get_current_node(child, keys_list, offset + 1)
    return None


# -----------------------------------------------------------------------------------
# Setup a list that is printed in the list order and delivers a tree structure using metadata.html
# -----------------------------------------------------------------------------------
def setup_print_list( current_node, print_list):

    if current_node.with_children:
        for child in current_node.children:
            print_list.append(child)
            if child.with_children:
                setup_print_list(child, print_list)
        print_list.append(None)     # All children onsidered - this is a flag to issue </li> and </ul>





