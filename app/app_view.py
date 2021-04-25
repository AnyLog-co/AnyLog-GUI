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
from flask import url_for

import json
from json.decoder import JSONDecodeError


from config import Config


# ------------------------------------------------------------------------
# The process to load a JSON file that maintanins the GUI view of the data/metadata
# ------------------------------------------------------------------------

class gui():

    def __init__(self):
        self.config_struct = None 
        self.config_error = None    # Error set if COnfig file with error in structure
        self.policies_table = []     # The list of policies in a 2 domentional list (representing the display of the list)
    # ------------------------------------------------------------------------
    # Get Base Info from the config / JSON file
    # ------------------------------------------------------------------------
    def get_base_info(self, key):
        '''
        Base Info is in the config file under "gui"
        i.e.
        Return the "query_node" value (IP:Port) from the JSON config struct
        '''
        if self.config_struct and "gui" in self.config_struct and key in self.config_struct["gui"]:
            query_node = self.config_struct["gui"][key]
        else:
            query_node = None
        return query_node
    # ------------------------------------------------------------------------
    # Load the JSON and set main structures
    # ------------------------------------------------------------------------
    def set_gui(self, file_name = None):
        '''
        Load the JSON file and adds error if file strcure is not of JSON.
        '''

        if not file_name:
            file_name = Config.GUI_VIEW    # get from system variable
        
        self.config_struct, self.config_error = load_json(file_name)

        if self.config_struct:
            # Load the ploicies to a structure that displays a table of policies
            line_list = []  # limits the number of columns
            links_in_row = 8
            policies_list = self.get_base_info("policies")     # get the list of policies from the config file
            if policies_list and isinstance(policies_list, list):
                for policy in policies_list:
                    if "name" in policy:
                        policy_name = policy["name"]
                        line_list.append(policy_name)

                        if len(line_list) == links_in_row:
                            self.policies_table.append(line_list)
                            line_list = []  # Start a new line
            if len(line_list):
                self.policies_table.append(line_list)

    # ------------------------------------------------------------------------
    # Return The list of policies
    # ------------------------------------------------------------------------
    def get_policies_list(self):
        return self.policies_table

    # ------------------------------------------------------------------------
    # Return The info of the policy
    # ------------------------------------------------------------------------
    def get_policy_info(self, policy_name):
        policies_list = self.get_base_info("policies")
        for policy in policies_list:
            if "name" in policy and policy['name'] == policy_name:
                return policy
        return None

    # ------------------------------------------------------------------------
    # Return config error
    # ------------------------------------------------------------------------
    def get_config_error(self):
        '''
        Error when config file read
        '''
        return self.config_error

    def is_config_error(self):
        '''
        Error when config file read
        '''
        return self.config_error != None
    # ------------------------------------------------------------------------
    # Test config file available
    # ------------------------------------------------------------------------
    def is_with_config(self):
        '''
        Test if config file available
        '''

        return self.config_struct != None

    # ------------------------------------------------------------------------
    # Get the dynamic menu based on the user navigation
    # ------------------------------------------------------------------------
    def get_dynamic_menu( self, gui_path ):
        '''
        Get the dynamic menu as f(user navigation)
        gui_path - the path to the parent --> get the children
        '''

        parent_menu = []       # Collection of the menu names of the parents
        children_menu = []         # Collection of the menu names of the children
        if self.config_struct and "gui" in self.config_struct:
            tree = self.config_struct["gui"]
            if gui_path:
                gui_keys = gui_path.split('@')
            else:
                gui_keys = None
            self.add_path_children( tree, 0, gui_keys, parent_menu, children_menu )
        return [parent_menu, children_menu]
    # ------------------------------------------------------------------------
    # Create the dynamic menu based on the GUI path
    # ------------------------------------------------------------------------
    def add_path_children( self, tree, level, gui_keys, parent_menu, child_menu ):

        if "children" in tree:
            child_tree = tree["children"]
        else:
            child_tree = None
        
        if gui_keys and level:
            parent_path = '@'.join(gui_keys[:level])
        else:
            parent_path = ""

        if not gui_keys or level == len(gui_keys):
            # Add all children to the child_menu list
            if child_tree:
                for child_name in child_tree:
                    url_link = url_for("tree")
                    if parent_path:
                        url_link += "/%s@%s" % (parent_path, child_name)
                    else:
                         url_link +=  "/%s" % (child_name)
                    child_menu.append((child_name, url_link))
        else:
            # Add all parents to the parent_name list

            parent_name = gui_keys[level]      # Get the link name from the path
                            
            url_link = url_for("tree")
            if parent_path:
                url_link +=  "/%s@%s" % (parent_path, parent_name)
            else:
                url_link +=  "/%s" % (parent_name)
            parent_menu.append((parent_name, url_link))

            if parent_name in child_tree:
                # Move to next layer
                child_tree = child_tree[parent_name]
 
            self.add_path_children(child_tree, level + 1, gui_keys, parent_menu, child_menu)
    # ------------------------------------------------------------------------
    # Get the AnyLog command as f (level) from the user JSON configuration struct
    # ------------------------------------------------------------------------
    def get_command(self, level):
        '''
        Get the AnyLog command as f (level) from the user JSON configuration struct
        '''

        command = None
        if "gui" in self.config_struct:
            json_struct = self.config_struct["gui"]
            for i in range(level):
                if not isinstance(json_struct, dict):
                    break
                if i == (level - 1):
                    # get the command to get the entries
                    if "query" in json_struct:
                        command = json_struct["query"]
                    else:
                        break
                else:
                    if "children" in json_struct:
                        json_struct = json_struct["children"]
                    else:
                        command = None
                        break

        return command      # the AL command - if available
    # ------------------------------------------------------------------------
    # Get the SUbtree by the selection path
    # ------------------------------------------------------------------------
    def get_subtree( self, selection ):
        select_list = selection.split('@')
        json_struct = self.config_struct["gui"]
        for entry in select_list:
            if not "children" in json_struct:
                json_struct = None
                break
            json_struct = json_struct["children"]
            if entry not in json_struct:
                json_struct = None  # Path not found
                break
            json_struct = json_struct[entry]
            
        return json_struct

# ------------------------------------------------------------------------
# The process to load a JSON file that maintanins the GUI view of the data/metadata
# ------------------------------------------------------------------------

def load_json(file_name):

    try:
        f = open(file_name)
        data = json.load(f)
    except JSONDecodeError as e:
        data = None
        error_msg = "AnyLog: Config File format error - line: {} column: {} message: {}".format(e.lineno, e.colno, e.msg)
    except:
        error_msg = "AnyLog: Config File format error"
        data = None
    else:
        error_msg = None
    return [data, error_msg]

# ------------------------------------------------------------------------
# Get entree from the JSON tree
# ------------------------------------------------------------------------
def get_tree_entree( json_struct, attr_name):

    if attr_name in json_struct:
        value = json_struct[attr_name]
    else:
        value = None
    return value
# ------------------------------------------------------------------------
# Test if has children
# ------------------------------------------------------------------------
def is_edge_node(json_struct:dict):
    '''
    Retun False if node has "children" attribute
    '''
    
    return not "children" in json_struct

# =======================================================================================================================
# String to list
# =======================================================================================================================
def str_to_list(data: str):

    try:
        list_obj = list(eval(data))
    except:
        list_obj = None
    return list_obj


