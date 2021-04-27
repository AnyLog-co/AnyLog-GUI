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

# -----------------------------------------------------------------------------------
# Objects to describe a tree hierarchy used in output_tree.html
# -----------------------------------------------------------------------------------
class TreeEntry():

    def __init__(self, start_list, end_list, is_key, data):
        self.start_list = start_list     # Start a new list before the print
        self.end_list = end_list          # end aa list after the print
        self.is_key = is_key            # Is a key for an attribute value

        if isinstance(data, str):
            self.data = "\"%s\"" % data
        else:
            self.data = str(data)

# -----------------------------------------------------------------------------------
# String to JSON
# -----------------------------------------------------------------------------------
def string_to_json( data_str ):

    try:
        #json_struct = data_str.json()
        json_struct = json.loads(data_str, encoding="utf8")
    except ValueError as err:
        error_msg = "Failed to map string to JSON: %s" % str(err)
        json_struct = None
    except JSONDecodeError as err:
        error_msg = "Failed to map string to JSON: %s" % str(err)
        json_struct = None
    except KeyError as err:
        error_msg = "Failed to map string to JSON: %s" % str(err)
        json_struct = None
    except:
        errno, err = sys.exc_info()[:2]
        error_msg = "Failed to map string to JSON: %s" % str(err)
        json_struct = None
    else:
        error_msg = None

    return [json_struct, error_msg]

# -----------------------------------------------------------------------------------
# JSON to string
# -----------------------------------------------------------------------------------
def json_to_string(json_struct):

    try:
        data_str = json.dumps(json_struct)
    except ValueError as err:
        error_msg = "Failed to map JSON to string: %s" % str(err)
        data_str = None
    except JSONDecodeError as e:
        error_msg = "Failed to map JSON to string: %s" % str(err)
        data_str = None
    except:
        error_msg = "Failed to map JSON to string"
        data_str = None
    else:
        error_msg = None

    return [data_str, error_msg]

# -----------------------------------------------------------------------------------
# Simple setup of a print of a list of JSON policies
# Send structure to output.html
# -----------------------------------------------------------------------------------
def simple_polisies_list(policies):
    data_list = []
    for json_entry in policies:
        json_string = json.dumps(json_entry,indent=4, separators=(',', ': '), sort_keys=True)
        data_list.append(json_string)  #  transformed to a JSON string.
    return data_list

# -----------------------------------------------------------------------------------
# Print setup of JSON for output_tree.html
# -----------------------------------------------------------------------------------
def setup_print_tree( source_struct, print_struct ):

    if isinstance(source_struct, dict):

        counter = len(source_struct) - 1  # The number of entries
        index = 0
        for key, value in source_struct.items():

            if isinstance(value,list) or isinstance(value, dict):
                start_list = not counter
                end_list = counter == index
                new_entry = TreeEntry(start_list, end_list, True, key)
                print_struct.append(new_entry)
                setup_print_tree( value, print_struct )
            else:
                set_edge(key, value, print_struct )

            index += 1

    elif isinstance(source_struct, list):
        counter = len(source_struct) - 1  # The number of entries

        for index, entry in enumerate(source_struct):

            if isinstance(entry, list) or isinstance(entry, dict):
                start_list = not counter
                end_list = counter == index
                setup_print_tree(entry, print_struct)
            else:
                set_edge(None, entry, print_struct)

    else:
        set_edge(None, source_struct, print_struct)

# -----------------------------------------------------------------------------------
# Add edge Node
# -----------------------------------------------------------------------------------
def set_edge(key, value, print_struct):

    if key:
        data = str(key) + " : " + str(value)
    else:
        data = str(value)

    new_entry = TreeEntry(False, False, False, data)
    print_struct.append(new_entry)






