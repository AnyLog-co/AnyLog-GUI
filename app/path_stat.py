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
        "reports" : {
                    },
        "selected"  :   "Default",
        "path" :    []
    }
    set_new_state(user_name, "Default", True)

# -----------------------------------------------------------------------------------
# Reset or start a new state
# -----------------------------------------------------------------------------------
def set_new_state(user_name, report_name, is_default):
    '''
    Set a new state for a user in active_state_ struct
    '''
    global active_state_

    active_state_[user_name]['reports'][report_name] = { }
    active_state_[user_name]['reports'][report_name]["path"] = [] # A list repreenting the path
    active_state_[user_name]['reports'][report_name]["level"] = 0 # The current location in the list
    active_state_[user_name]['reports'][report_name]["entries"] = {} # The selected entries

    if is_default:
        active_state_[user_name]['selected'] = report_name


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
def update_status(user_name, parent_menu, id, data):

    '''
    Keep the user path state as f(user_name + report_used)
    '''

    global active_state_
    
    user_info = active_state_[user_name]

    report_selected = user_info["selected"]
    
    path_info = user_info["reports"][report_selected]  # the report maintains the path info

    # Set the path to the data location
    for index, step in enumerate(parent_menu):
        step_name = step[0]
        if index >= len(path_info["path"]):
            path_info["path"].append( { "name" : step_name, "data" : None })
        elif not path_info["path"][index]["name"] != step_name:
            path_info["path"][index]["name"] = step_name
            path_info["path"][index]["data"] = None
    
    path_info["path"][index]["data"] = data    # Keep the data of that layer
    path_info["level"] = index  # Keep current location

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
# Configure a new report or change report setting
# -----------------------------------------------------------------------------------
def set_report(user_name, form_info):
    '''
    Configure a new report or change report setting
    ''' 

    ret_val = True
    err_msg = None
    if 'report_name' in form_info:
        report_name = form_info['report_name']  
    else:
        report_name = ""        # user did not select an existing report
    
    if 'new_report' in form_info:
        new_report = form_info['new_report']  
    else:
        new_report = ""       

    if 'rename' in form_info:
        new_name = form_info['rename']  
    else:
        new_name = "" 

    if 'make_default' in form_info:
        is_default = form_info['make_default']
    else:
        is_default = False

    if 'reset' in form_info:
        reset = form_info['reset']
    else:
        reset = False

    if new_report and report_name:
        ret_val = False
        err_msg = "Duplicate selections: select existing report or new report"
    else:

        if new_report:
            set_new_state(user_name, new_report, is_default)
        elif reset:
            set_new_state(user_name, report_name, is_default)
        elif new_name:
            # replace the report info to a different name
            
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

        elif is_default:
            active_state_[user_name]['selected'] = report_name

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
                        parent_policy = get_policy(user_name, selection, parent_type)   # Get the policy of the parent from the path
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
def get_policy(user_name, selection, policy_type):

    global active_state_
    
    user_info = active_state_[user_name]

    report_selected = user_info["selected"]
    
    path_info = user_info["reports"][report_selected]  # the report maintains the path info

    selection_list = selection.split('@')

    policy = None

    parent_level = (len(selection_list) - 2)    # Note: parent level starts at 0

    if path_info["level"] >= parent_level:
        # No parent policy with the path provided

        for index in range (parent_level + 1):
            entry = selection_list[index]
            if path_info["path"][index]["name"] != entry:
                break
        
        if index == parent_level:
            policy = path_info["path"][index]["data"]
    
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
            edge_selected[policy_id]["path"] = copy.deepcopy(active_state_[user_name]['reports'][report_selected]["path"])

            db_name = get_policy_value(json_entry, dbms_name)    # Pull the dbms name from the policy
            if db_name:
                db_name = reset_str_chars(db_name)  # Make a dbms name (without spaces etc.)
            else:
                db_name = reset_str_chars(dbms_name)  # Make a dbms name (without spaces etc.)

            tb_name = get_policy_value(json_entry, table_name)    # Pull the table name from the policy
            if tb_name:
                tb_name = reset_str_chars(tb_name)  # Make a dbms name (without spaces etc.)
            else:
                tb_name = reset_str_chars(table_name)  # Make a dbms name (without spaces etc.)

            edge_selected[policy_id]["dbms_name"] = db_name
            edge_selected[policy_id]["table_name"] = tb_name
            edge_selected[policy_id]["edge"] = json_entry

# -------------------------------------------------------------------------
# Remove special chars that conflict with naming convention
# Database names and table names are set with alphanumeric characters
# -------------------------------------------------------------------------
def reset_str_chars( source_str ):
    global translate_dict_
    return source_str.translate ( translate_dict_ )

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
# Get a value from a policy
# ======================================================================================================================
def get_policy_value(policy, key):
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