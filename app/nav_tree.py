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
        self.policy = None
        self.policy_key = None
        self.policy_value = None        # shows value if the value is not a list or a dictionary
        self.dbms_name = None           # DBMS name or the key to pull the dbms name from the policy
        self.table_name = None          # Table name or the key to pull the table name from the policy
        self.option = None              # If node maintains a metadata option representing a type of a child
        self.parent = None              # Parent node

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

        params['parent'] = self                     # Set a link from a child to the parent

        child_node = TreeNode( **params )

        self.children.append( child_node )
        self.with_children = True

        return child_node

    # -----------------------------------------------------------------------------------
    # Add the metadata options which are the next selection in the hierarchy
    # -----------------------------------------------------------------------------------
    def add_select_grandchilds(self, gui_options):
        '''
        For each one of the children of the current node, add a child (a grandchild to the current).
        Each grandchild represents a navigation option in the hierarchy, based on the setup in the config file.

        gui_options - the dictionary with the navigation options
        '''

        children = self.children

        for child in children:
            for key in gui_options:
                # Every option maintains a metadata option representing a type of a child
                # The options reprent a select under the data in the GUI
                child.add_child( name='option', option=key )  # For every granchild - Add all options from the config file


    # -----------------------------------------------------------------------------------
    # Add the children resulting from a query of the parent usinf the method - get_path_info(...)
    # -----------------------------------------------------------------------------------
    def add_children(self, list_columns, list_keys, table_rows, dbms_name, table_name):
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

            if dbms_name:
                # This is an edge node that can pull a report using the dbms and table info
                params['dbms_name'] = dbms_name     # DBMS name or the bring (from the policy) instructions
                params['table_name'] = table_name   # Table name or the bring (from the policy) instructions

            self.add_child( **params )

    # -----------------------------------------------------------------------------------
    # Add a policy info to a node
    # -----------------------------------------------------------------------------------
    def add_policy( self, retrieved_policy ):
       self.policy = retrieved_policy
    # -----------------------------------------------------------------------------------
    # Add a policy info to a node
    # -----------------------------------------------------------------------------------
    def is_with_policy( self ):
       return self.policy != None

    # -----------------------------------------------------------------------------------
    # Set Policy value
    # -----------------------------------------------------------------------------------
    def set_policy_value(self, policy_value):
        if isinstance(policy_value,str):
            self.policy_value = "\"%s\"" % policy_value
        else:
            self.policy_value = str(policy_value)

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
    '''
    Update a list that represents the order of lines printed in the navigation tree
    :param current_node: The node to consider
    :param print_list:  Structure to update
    :return:
    '''

    if current_node.with_children:
        for child in current_node.children:
            print_list.append(child)
            if child.is_with_policy():
                setup_print_policy( child.policy, print_list )
            if child.with_children:
                setup_print_list(child, print_list)
        print_list.append(None)     # All children onsidered - this is a flag to issue </li> and </ul>


# -----------------------------------------------------------------------------------
# Setup a policy in the print_list structure
# -----------------------------------------------------------------------------------
def setup_print_policy( policy, print_list):

    if len(policy):
        counter = 0
        for policy_key, policy_value in policy.items():
            counter += 1
            params = {}
            params['policy_key'] = policy_key
            if counter == 1:
                params['first_child'] = True
            if counter == len(policy):
                params['last_child'] = True

            new_node = TreeNode(**params)
            print_list.append(new_node)

            if isinstance(policy_value,dict):
                setup_print_policy(policy_value, print_list)
            elif isinstance(policy_value, list):
                for list_entry in policy_value:
                    if isinstance(list_entry,dict) or isinstance(list_entry,list):
                        setup_print_policy(policy_value, print_list)
                    else:
                        new_node.set_policy_value(policy_value)
            else:
                new_node.set_policy_value(policy_value)

        print_list.append(None)  # All children onsidered - this is a flag to issue </li> and </ul>


# -----------------------------------------------------------------------------------
# Update AL command to retrieve info with info from the parent
#
# -----------------------------------------------------------------------------------
def update_command(current_node, selection, command):
    '''
    If the bring command references the parent, bring the info from the parents.
    selection - describes the parents path.
    Example:
        "blockchain get tag where machine = [machine][id]  bring.unique.json [tag][name] [tag][description] [tag][id] separator = ,"
        --> [machine][id] is taken from the parents usinf the path described in the selection variable
    '''
    cmd_words = command.split()
    value = None
    if len(cmd_words) > 7:
        if cmd_words[3] == "where" and cmd_words[5] == '=':
            for index, word in enumerate(cmd_words[6:]):
                if word == 'bring' or word.startswith("bring."):
                    break  # End of WHERE part
                value = None
                if word[0] == '[' and word[-1] == ']':
                    keys_list = word[1:].split('[')  # The list of keys to use to retrieve from the JSON
                    if len(keys_list) > 1:  # at least 2 keys (the first is the policy type)
                        parent_type = keys_list[0][:-1]
                        parent_policy = current_node.get_parent()
                        if parent_policy:
                            if parent_type in parent_policy:
                                # pull the attribute value
                                value = parent_policy
                                for entry in keys_list:
                                    if isinstance(value, dict):
                                        key = entry[:-1]  # Remove closing brakets
                                        if key in value:
                                            value = value[key]
                                        else:
                                            value = None
                                            break
                                    else:
                                        value = None
                                        break
                if value:
                    cmd_words[6 + index] = value  # Replace with value from parent
                else:
                    break
    if value:
        # command text was replaced with values from parents
        updated_cmd = ' '.join(cmd_words)
    else:
        updated_cmd = command

    return updated_cmd

# -----------------------------------------------------------------------------------
# Get user Path overview
# Example Reply
'''
    Name              Names of Info Fields       Names of policies keys            Values from Queries (based on policies keys)   
 (from Config)            (from Config)             (From Config)

[('Manufacturer', ['ID', 'Name', 'URL'],       ['id', 'name', 'url'],       [['9990b1b7d5ed51508cdca8f53d6a6621', 'Orics', 'http://orics.com/']]),
 ('Company',      ['ID', 'Customer'],          ['id', 'customer'],          [['0d255db48d048f80e32953a836b27495', 'TuscanBrands']
                                                                             ['0d597850005688024900ab432245563e', 'Costco']])
]
'''
# -----------------------------------------------------------------------------------
def get_step_from_tree(level, parent_menu):
    '''
    Return the step name and the name from the data instance at this layer
    '''
    global active_state_

    user_info = active_state_[user_name]

    path_info = user_info["path"]  # the report maintains the path info
    path_steps = []
    path_level = user_info["level"]
    # Set the path to the data location
    for index in range(level - 1):
        step_name = parent_menu[index][0]
        if index < len(path_info):
            if path_info[index]["data"]:
                step_data = path_info[index]["data"]
                step_keys = path_info[index]["keys"]
                step_title = path_info[index]["title"]
                policy_type = get_policy_type(step_data)
                if policy_type:
                    policy = step_data[policy_type]     # Get the data from the JSON structure
                    columns_val = []
                    for key in step_keys:
                        if key in policy:
                            value = str(policy[key])
                        else:
                            value = ""
                        columns_val.append(value)
                    path_steps.append( (step_name, step_title, step_keys, [columns_val]) )

    return path_steps