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
# Update the status of the user
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
            path_info["path"].append( {})
        path_info["path"][index]["name"] = step_name
    
    path_info["path"][index]["data"] = data    # Keep the data of that layer
    path_info["level"] = index  # Keep current location


# -----------------------------------------------------------------------------------
# Add entry to the report
# -----------------------------------------------------------------------------------
def add_report_entry(user_name, selection, id):

    global active_state_
    
    user_info = active_state_[user_name]

    report_selected = user_info["selected"]

    # Get a dictionary with all the selected edge nodes for the report
    edge_selected = active_state_[user_name]['reports'][report_selected]["entries"] # The selected entries

    edge_selected[id] = True

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
    is_default = form_info['make_default']
    if form_info['new_report'] or form_info['reset']:
        set_new_state(user_name, report_name, is_default)
    elif form_info['rename']:
        # replace the report info to a different name
        new_name = form_info['rename']
        user_reports = active_state_[user_name]['reports']
        if report_name in user_reports:
            if new_name in user_reports:
                ret_val = False
                err_msg = "Duplicate report name: %s" % report_name
            else:
                report_struct = user_reports[report_name]
                active_state_[user_name]['reports'][new_name] = report_struct
                active_state_[user_name]['reports'][report_name] = None
        else:
            ret_val = False
            err_msg = "Wrong report name: %s" % report_name

        if ret_val and is_default:
            active_state_[user_name]['selected'] = new_name

    elif is_default:
        active_state_[user_name]['selected'] = report_name

    return [ret_val, err_msg]