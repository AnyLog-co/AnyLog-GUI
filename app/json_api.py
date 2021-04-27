
import json
import sys
from json.decoder import JSONDecodeError

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
# Print setup of JSON for output_tree.html
# Every entry that is set in print_struct has 3 attributes
# - Is last in the subtree
# - is key (True) or value (False)
# - The data (key or value)
# -----------------------------------------------------------------------------------
def setup_print_tree( is_last, source_struct, print_struct ):
    '''
    Update print_struct with a setup for output_tree.html

    :param source_struct: A dictionary or a list
    :param print_struct: A structure to send to output_tree.html
    :return:
    '''



    if isinstance(source_struct, dict):
        counter = len(source_struct) - 1  # The number of entries
        index = 0
        for key, value in source_struct.items():
            if index == counter:
                print_struct.append((True, True, "\"%s\" : " %  key))          # last in the hierarchy
            else:
                print_struct.append((False, True, "\"%s\" : " %  key))          # last in the hierarchy

            setup_print_tree( True, value, print_struct )
            index += 1

    elif isinstance(source_struct, list):
        counter = len(source_struct) - 1  # The number of entries
        for index, entry in enumerate(source_struct):
            if index == counter:
                setup_print_tree(True, entry, print_struct)      # last in the hierarchy
            else:
                setup_print_tree(False, entry, print_struct)      # last in the hierarchy

    else:
        if isinstance(source_struct,str):
            value = "\"%s\"" % source_struct
        else:
            value = str(source_struct)

        print_struct.append((is_last, False, value))  # last in the hierarchy











