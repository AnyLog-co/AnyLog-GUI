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

# Conversion table to allow propper dbms names and table names
translate_dict_ = {}
for x in range (256):

    char_x = chr(x)
    if char_x == '_' or char_x == ' ' or char_x == '-' or char_x == '.' or char_x == '/' or char_x == '\\' or char_x == ':':
        char_y = '_'
    else:
        if (char_x >= 'A' and char_x <= 'Z') or  (char_x >= 'a' and char_x <= 'z') or (char_x >= '0' and char_x <= '9'):
           continue                 # No need to translate

        char_y = "0x%02x" % x    # The string showing x in hex

    translate_dict_[x] = char_y

import copy

active_state_ = {         # A structure containing info per traversak and selected report data
    
}


# -----------------------------------------------------------------------------------
# Test if the user is assigned to the active_state struct
# -----------------------------------------------------------------------------------
def is_with_user(user_name):
    global active_state_
    return user_name in active_state_

# -----------------------------------------------------------------------------------
# Set new user
# -----------------------------------------------------------------------------------
def set_new_user(user_name):
    '''
    Set a new user in active_state_ struct + initiate initial user settings
    '''
    global active_state_

    active_state_[user_name] = {
        "lists" : {},           # Dictionaries of nodes maintained as f (user) and a unique name
        "reports" : {
                        "edge_nodes" : {}         # a dictionary of edge nodes selected in the tree navigation
                    },
        "selected"  :   "My_Report",
        "path" :    [],         # navigation as f(user)
        "level" : 0,            # The current location in the path
        "connected" : False,     # User is not connected
    }
    set_new_state(user_name, "My_Report", True)

# -----------------------------------------------------------------------------------
# Test for existance of a policy in a list of nodes selected to be monitored
# -----------------------------------------------------------------------------------
def is_in_info_list(user_name, list_name, policy_id):
    '''
    Selected policies are maintained as f(user)
    test if the policy exists in the list of policies

    param: list_name - an ID of the list. i.e. "monitored"
    '''
    user_info = active_state_[user_name]["lists"]
    if not list_name in user_info:
        return False
    return policy_id in user_info[list_name]

# -----------------------------------------------------------------------------------
# Updates a list of nodes selected to be monitored
# -----------------------------------------------------------------------------------
def add_to_info_list(user_name, list_name, policy_id, info):
    '''
     Selected policies are maintained as f(user)
     Add a policy to the list

     param: list_name - an ID of the list. i.e. "monitored"
     '''
    user_info = active_state_[user_name]["lists"]
    if not list_name in user_info:
        user_info[list_name] = {}

    user_info[list_name][policy_id] = info
# -----------------------------------------------------------------------------------
# Get a list of nodes selected to be monitored
# -----------------------------------------------------------------------------------
def get_info_list(user_name, list_name):
    user_info = active_state_[user_name]["lists"]
    if not list_name in user_info:
        info_list = None
    else:
        info_list = user_info[list_name]
    return info_list
# -----------------------------------------------------------------------------------
# is user connected
# -----------------------------------------------------------------------------------
def is_user_connnected(user_name):
    '''
    Return True if usser "connected" flag is set to True
    '''
    return (user_name in active_state_ and  active_state_[user_name]["connected"])

# -----------------------------------------------------------------------------------
# set user connected
# -----------------------------------------------------------------------------------
def set_user_connnected(user_name):
    if user_name in active_state_:
        active_state_[user_name]["connected"] = True

# -----------------------------------------------------------------------------------
# Register an element for the user
# -----------------------------------------------------------------------------------
def register_element(user_name, element_key, element):
    '''
    keep info as f(user + key)
    '''
    user_info = active_state_[user_name]
    user_info[element_key] = element
# -----------------------------------------------------------------------------------
# Register an element for the user
# -----------------------------------------------------------------------------------
def get_element(user_name, element_key):
    '''
    keep info as f(user + key)
    '''

    if user_name in active_state_:
        user_info = active_state_[user_name]
        if element_key in user_info:
            element = user_info[element_key]
        else:
            element = None
    else:
        element = None
    return element
# -----------------------------------------------------------------------------------
# Get the name of the visualization platform
# -----------------------------------------------------------------------------------
def get_platform_name(user_name, report_name):
    global active_state_
    user_info = active_state_[user_name]

    platform = None
    if report_name in user_info['reports']:
        if 'platform' in user_info['reports'][report_name]:
            platform =  user_info['reports'][report_name]['platform']
    return platform

# -----------------------------------------------------------------------------------
# Get the 'selected' report name
# -----------------------------------------------------------------------------------
def get_report_name(user_name):
    '''
    Return the default report for this user
    '''
    global active_state_
    user_info = active_state_[user_name]

    if 'selected' in user_info:
        report_name = user_info['selected']
    else:
        report_name = None
    return report_name

# -----------------------------------------------------------------------------------
# Save the last selection for the reports dates
# -----------------------------------------------------------------------------------
def set_dates_selection(user_name, report_name, from_date, to_date):
    global active_state_
    user_info = active_state_[user_name]

    if report_name in user_info['reports']:
        user_info['reports'][report_name]['dates'] = (from_date, to_date)

# -----------------------------------------------------------------------------------
# Get the last selection for the reports dates
# -----------------------------------------------------------------------------------
def get_dates_selection(user_name, report_name ):
    global active_state_
    from_date = None
    to_date = None
    user_info = active_state_[user_name]

    if report_name in user_info['reports']:
        if 'dates' in user_info['reports'][report_name]:
            from_date, to_date = user_info['reports'][report_name]['dates']
    return [from_date, to_date]
# -----------------------------------------------------------------------------------
# Set the name of the visualization platform for the report
# -----------------------------------------------------------------------------------
def set_platform_name(user_name, report_name, platform):
    
    global active_state_
    user_info = active_state_[user_name]

    if report_name in user_info['reports']:
        user_info['reports'][report_name]['platform'] = platform

# -----------------------------------------------------------------------------------
# Get user Path overview
# Example reply:
'''
    Name              Names of Info Fields       Names of policies keys            Values from Queries (based on policies keys)   
 (from Config)            (from Config)             (From Config)
 
[('Manufacturer', ['ID', 'Name', 'URL'],       ['id', 'name', 'url'],       [['9990b1b7d5ed51508cdca8f53d6a6621', 'Orics', 'http://orics.com/']]),
 ('Company',      ['ID', 'Customer'],          ['id', 'customer'],          [['0d255db48d048f80e32953a836b27495', 'TuscanBrands']
                                                                             ['0d597850005688024900ab432245563e', 'Costco']])
 ]
 
 Note - last layer provides all children 
'''
# -----------------------------------------------------------------------------------
def get_path_overview(user_name, level, parent_menu):
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

# -----------------------------------------------------------------------------------
# Return the list of nodes that are candidate to a report
# -----------------------------------------------------------------------------------
def get_selected_nodes(user_name:str):
    '''
    Return the nodes that were selected by the user as an option to a report
    '''
    return active_state_[user_name]['reports']['edge_nodes']

# -----------------------------------------------------------------------------------
# Test if the policy is in the selected nodes
# -----------------------------------------------------------------------------------
def is_node_selected(user_name:str, policy_id:str):
    return policy_id in active_state_[user_name]['reports']['edge_nodes']

# -----------------------------------------------------------------------------------
#
# Return a structure representing each node
# Node info includes:
#                     node_info["dbms_name"] = db_name
#                     node_info["table_name"] = tb_name
#                     node_info["policy"] = policy
#
# -----------------------------------------------------------------------------------
def get_table_with_selected_nodes(user_name, policy_keys, add_dbms_name, add_table_name):
    selected_nodes = get_selected_nodes(user_name)
    table_info = []
    for node_info in selected_nodes.values():
        row_info = []
        policy = node_info['policy']
        policy_type = get_policy_type(policy)
        for key in policy_keys:
            if key in policy[policy_type]:
                value = policy[policy_type][key]
            else:
                value = None
            row_info.append(value)         # Add the value from the policy
        if add_dbms_name:
            row_info.append(node_info["dbms_name"])
        if add_table_name:
            row_info.append(node_info["table_name"])
        table_info.append(row_info)
    return table_info
# -----------------------------------------------------------------------------------
# Add a node to the selected nodes list.
# -----------------------------------------------------------------------------------
def add_selected_node(user_name: str, policy_id: str, node_info:dict):
    active_state_[user_name]['reports']['edge_nodes'][policy_id] = node_info

# -----------------------------------------------------------------------------------
# Reset or start a new state
# -----------------------------------------------------------------------------------
def set_new_state(user_name, report_name, is_default):
    '''
    Set a new state for a user in active_state_ struct
    '''
    global active_state_

    active_state_[user_name]['reports'][report_name] = { }
    active_state_[user_name]['reports'][report_name]["entries"] = {} # The selected entries

    if is_default:
        active_state_[user_name]['selected'] = report_name

# -----------------------------------------------------------------------------------
# Delete a report
# -----------------------------------------------------------------------------------  
def delete_report(user_name, report_name):
    user_reports = active_state_[user_name]['reports']
    if len(user_reports) == 1:
        # Only reset the report as one report needs to be available
        set_new_state(user_name, report_name, True)
    else:
        del user_reports[report_name]
        if active_state_[user_name]['selected'] == report_name:
            # The deleted report is the default - set a different report as the default
            next_report = list(user_reports.keys())[0]
            active_state_[user_name]['selected'] == next_report


# -----------------------------------------------------------------------------------
# Get the report selected by the user
# -----------------------------------------------------------------------------------  
def get_report_selected(user_name):
    global active_state_

    if user_name in active_state_:
        report_name = active_state_[user_name]["selected"]
    else:
        report_name = "Default"
    return report_name
# -----------------------------------------------------------------------------------
# Update the path with the entries visited by the user 
# The path is maintained as a f(report)
# -----------------------------------------------------------------------------------
def update_status(user_name, parent_menu, list_keys, table_title, id, data):

    '''
    Keep the user path state as f(user_name + report_used)
    The info maintained:
        data - the user data
        keys - the keys tp pull the info from the JSON
    '''

    global active_state_
    
    user_info = active_state_[user_name]
  
    path_info = user_info["path"]  # the report maintains the path info

    # Set the path to the data location
    for index, step in enumerate(parent_menu):
        step_name = step[0]
        if index >= len(path_info):
            path_info.append( { "name" : step_name, "data" : None, "keys": None, "title": None, "id": None})
        elif path_info[index]["name"] != step_name:
            path_info[index]["name"] = step_name
            path_info[index]["data"] = None
            path_info[index]["keys"] = None     # The keys to pull data from the JSON
            path_info[index]["title"] = None  # The title rrelating to the keys
            path_info[index]["id"] = None

    path_info[index]["name"] = step_name
    path_info[index]["data"] = data    # Keep the data of that layer
    path_info[index]["keys"] = list_keys  # Keep the data of that layer
    path_info[index]["title"] = table_title  # Keep the printout title
    path_info[index]["id"] = id
    user_info["level"] = index  # Keep current location

# -----------------------------------------------------------------------------------
# Return the list of reports associated with the user
# -----------------------------------------------------------------------------------
def get_user_reports(user_name):
    global active_state_
    '''
    Return the klist of user reports
    '''
    
    user_reports = active_state_[user_name]["reports"]
    return list(user_reports.keys())

# -----------------------------------------------------------------------------------
# Get the selection entries for the report
# -----------------------------------------------------------------------------------
def get_report_entries(user_name, report_name):
    if report_name and report_name in active_state_[user_name]["reports"]:
        report_entries = active_state_[user_name]["reports"][report_name]['entries']
    else:
        report_entries = None
    return report_entries

# -----------------------------------------------------------------------------------
# Remove an entry from the report
# -----------------------------------------------------------------------------------
def remove_selected_entry(user_name, report_name, entry):
    '''
    Delete the entry from the list of entries in the report.
    '''

    if report_name and report_name in active_state_[user_name]["reports"]:
        report_entries = active_state_[user_name]["reports"][report_name]
        if entry in report_entries['entries']:
            del report_entries['entries'][entry]

# -----------------------------------------------------------------------------------
# Configure a new report or change report setting
# -----------------------------------------------------------------------------------
def set_report(user_name, form_info):
    '''
    Configure a new report or change report setting
    ''' 

    selection_counter = 0
    ret_val = True
    err_msg = None
    if 'report_name' in form_info:
        report_name = form_info['report_name']  
    else:
        report_name = ""        # user did not select an existing report
    
    if 'new_report' in form_info and len(form_info['new_report']):
        report_name = ""        # Ignore report selection
        new_report = form_info['new_report'] 
        if len(new_report) == new_report.count(' '):
            new_report = ""       # All spaces
        else:
            new_report = new_report.replace(' ','_')
    else:
        new_report = ""       

    if 'rename' in form_info and len(form_info['rename']):
        new_name = form_info['rename']
        if ' ' in new_name:
            if len(new_name) == new_name.count(' '):
                new_name = ""       # All spaces
            else:
                new_name = new_name.replace(' ','_')
    else:
        new_name = "" 

    if 'make_default' in form_info:
        selection_counter += 1
        is_default = form_info['make_default']
    else:
        is_default = False

    if 'reset' in form_info:
        selection_counter += 1
        reset = form_info['reset']
    else:
        reset = False

    if 'delete' in form_info:
        selection_counter += 1
        is_delete = form_info['delete']
    else:
        is_delete = False


    if new_report and report_name:
        ret_val = False
        err_msg = "Duplicate selections: select existing report or new report"
    else:
        conflicting_selections = False

        # Test conflicting choices
        if selection_counter == 3 or (is_delete and (selection_counter != 1 or new_report)):
            conflicting_selections = True

        # Test conflicting rename + new report
        elif  new_name and new_report:
            conflicting_selections = True
        
        if conflicting_selections:
            ret_val = False
            err_msg = "Wrong selections: conflicting report selections"
        else:
            # Test report not selected
            if not report_name and (is_delete or reset or new_name) or \
                        (is_default and not report_name and not new_name and not new_report):
                ret_val = False
                err_msg = "Report name not selected"
            else:

                if is_delete:
                    delete_report(user_name, report_name)
                elif new_report:
                    if get_report_info(user_name, report_name):
                        ret_val = False
                        err_msg = "Duplicate report name: %s" % report_name
                    else:
                        set_new_state(user_name, new_report, is_default)
                elif reset:
                    set_new_state(user_name, report_name, is_default)
                elif new_name:
                    # replace the report info to a different name
                    if get_report_info(user_name, new_name):
                        ret_val = False
                        err_msg = "Duplicate report name: %s" % new_name
                    else:
                        ret_val, err_msg = rename_report(user_name, report_name, new_name, is_default)                  
                elif is_default:
                    active_state_[user_name]['selected'] = report_name

    return [ret_val, err_msg]

# -----------------------------------------------------------------------------------
# Update AL command to retrieve info with info from the parent
# -----------------------------------------------------------------------------------
def rename_report(user_name, report_name, new_name, is_default):

    ret_val = True
    err_msg = None
    user_reports = active_state_[user_name]['reports']
    if report_name in user_reports:
        if new_name in user_reports:
            ret_val = False
            err_msg = "Duplicate report name: %s" % report_name
        else:
            report_struct = user_reports[report_name]
            active_state_[user_name]['reports'][new_name] = report_struct
            del active_state_[user_name]['reports'][report_name]

            if active_state_[user_name]['selected'] == report_name:
                # keep default if old name was the default
                active_state_[user_name]['selected'] = new_name
    else:
        ret_val = False
        err_msg = "Wrong report name: %s" % report_name

    if ret_val and is_default:
        active_state_[user_name]['selected'] = new_name
    return [ret_val, err_msg]
# -----------------------------------------------------------------------------------
# Update AL command to retrieve info with info from the parent
# -----------------------------------------------------------------------------------
def update_command(user_name, selection, command):
    
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
                    break       # End of WHERE part
                value = None
                if word[0] == '[' and word[-1] == ']':
                    keys_list = word[1:].split('[')         # The list of keys to use to retrieve from the JSON
                    if len(keys_list) > 1:             # at least 2 keys (the first is the policy type)
                        parent_type = keys_list[0][:-1]
                        parent_policy = get_policy(user_name, selection)   # Get the policy of the parent from the path
                        if parent_policy:
                            if parent_type in parent_policy:
                                # pull the attribute value
                                value = parent_policy
                                for entry in keys_list:
                                    if isinstance(value,dict):
                                        key = entry[:-1]    # Remove closing brakets
                                        if key in value:
                                            value = value[key]
                                        else:
                                            value = None
                                            break
                                    else:
                                        value = None
                                        break
                if value:
                    cmd_words[6 + index] = value    # Replace with value from parent
                else:
                    break
    if value:
        # command text was replaced with values from parents
        updated_cmd = ' '.join(cmd_words)
    else:
        updated_cmd = command
    
    return updated_cmd
# -----------------------------------------------------------------------------------
# Get the info selected for the report
# -----------------------------------------------------------------------------------
def get_report_info(user_name, report_name):
    '''
    Return a link to the info cpllected on the report.
    Includig: DBMS and Tables for output
    '''
    global active_state_
    
    user_info = active_state_[user_name]

    if report_name in user_info["reports"]:
        report_info = user_info["reports"][report_name]
    else:
        report_info = None
    return report_info

# -----------------------------------------------------------------------------------
# Get a policy from the path
# -----------------------------------------------------------------------------------
def get_policy(user_name, selection):

    global active_state_
    
    user_info = active_state_[user_name]
    
    path_info = user_info["path"]  # the user path info

    selection_list = selection.split('@')

    policy = None

    parent_level = (len(selection_list) - 2)    # Note: parent level starts at 0

    if user_info["level"] >= parent_level:
        # No parent policy with the path provided

        for index in range (parent_level + 1):
            entry = selection_list[index]
            if path_info[index]["name"] != entry:
                break
        
        if index == parent_level:
            policy = path_info[index]["data"]
    
    return policy
# -------------------------------------------------------------------------
# Add selected Entry to the list of entries in the report
# -------------------------------------------------------------------------
def add_entry_to_report(user_name, dbms_name, table_name, json_entry):
 
    '''
    Add an entry to the report - 
    Every report structure includes the list of Edge elements (and their parents) that participate in the report
    '''

    global active_state_
    
    user_info = active_state_[user_name]

    report_selected = user_info["selected"]

    # Get a dictionary with all the selected edge nodes for the report
    edge_selected = active_state_[user_name]['reports'][report_selected]["entries"] # The selected entries

    policy_type = get_policy_type(json_entry)
    if policy_type:
        if "id" in json_entry[policy_type]:
            policy_id = json_entry[policy_type]["id"]
        else:
            policy_id = None    # Missing ID for the policy
    else:
        # The JSON is not a policy
        if "id" in json_entry:
            policy_id = json_entry["id"]
        else:
            policy_id = None    # Missing ID for the json struct

    if policy_id:
        # Copy the path anf pathe elements to the list of selected items to print
        if not policy_id in edge_selected:
            # Not a duplicated node
            edge_selected[policy_id] = {}
            # The Path that determined the selected edge that is added to the report
            edge_selected[policy_id]["path"] = copy.deepcopy(active_state_[user_name]['path'])

            db_name = get_sql_name(json_entry, dbms_name)    # Pull the dbms name from the policy
            tb_name = get_sql_name(json_entry, table_name)  # Pull the dbms name from the policy

            edge_selected[policy_id]["dbms_name"] = db_name
            edge_selected[policy_id]["table_name"] = tb_name
            edge_selected[policy_id]["policy"] = json_entry

# -------------------------------------------------------------------------
# Get a dbms or a table name from the JSON structure
# -------------------------------------------------------------------------
def get_sql_name(json_entry, extract_key):
    '''
    Given a policy in JSON format and a key to extract the value from the policy,
    return the value.
    Replace spaces with underscore, return small letters and replace SQL allowable characters
    :param json_entry: The Policy
    :param extract_key: The key to use. For example [tag][name]
    :return: The derived value
    '''

    sql_name = extract_policy_value(json_entry, extract_key)  # Pull the dbms name from the policy
    if sql_name:
        sql_name = reset_str_chars(sql_name)  # Make a dbms name (without spaces etc.)
    else:
        # The extract key is the value to return
        sql_name = reset_str_chars(extract_key)  # Make a dbms name (without spaces etc.)
    return sql_name

# -------------------------------------------------------------------------
# Remove special chars that conflict with naming convention
# Database names and table names are set with alphanumeric characters
# -------------------------------------------------------------------------
def reset_str_chars( source_str ):
    global translate_dict_
    source_lower = source_str.lower()
    return source_lower.translate ( translate_dict_ )

# ======================================================================================================================
# Get the type of policy
# ======================================================================================================================
def get_policy_type(policy):

    if len(policy) == 1:
        # Policy has one entry at the root
        try:
            policy_type = next(iter(policy))
        except:
            policy_type = None
        else:
            if not isinstance(policy[policy_type], dict):
                policy_type = None  # second layer is not a dictionary
    else:
        policy_type = None

    return policy_type
# ======================================================================================================================
# Get The policy value - determine the policy type and return the value for the key
# ======================================================================================================================
def get_policy_value(policy, key):
    '''
    For the provided policy, pull the value using the second level key
    '''

    policy_type = get_policy_type(policy)
    if policy_type:
        if key in policy[policy_type]:
            return policy[policy_type][key]
    return None
# ======================================================================================================================
# Get a value from a policy using a key line [tag][name] [tag][id]
# ======================================================================================================================
def extract_policy_value(policy, key):
    '''
    Given a JSON policy and a key, retrieve the value
    The key structure is similar to the bring command: [key 1][key 2]

    If policy type is provided - test the type
    '''

    value = None
    if key[0] == '[' and key[-1] == ']':
        keys_list = key[1:].split('[')         # The list of keys to use to retrieve from the JSON
        value = policy
        for entry in keys_list:                # at least 2 keys (the first is the policy type)
            if isinstance(value,dict):
                key = entry[:-1]    # Remove closing brakets
                if key in value:
                    value = value[key]
                else:
                    value = None
                    break
            else:
                value = None
                break
    
    return value