
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

    counter = len(source_struct) - 1          # The number of entries

    if isinstance(source_struct, dict):
        for index, key, value in enumerate(source_struct.items()):
            if index == counter:
                print_struct.append((True, True, key))          # last in the hierarchy
            else:
                print_struct.append((False, True, key))    # last in the hierarchy

            print_struct.append((is_last, True, key + ' : '))

            setup_print_tree( value, print_struct )

    elif isinstance(source_struct, list):

        for index, entry in enumerate(source_struct):
            if index == counter:
                print_struct.append((True, False, entry))      # last in the hierarchy
            else:
                print_struct.append((False, False, entry))    # last in the hierarchy

    else:
        if isinstance(source_struct,str):
            value = "\"%s\"" % source_struct
        else:
            value = str(source_struct)

        print_struct.append((is_last, False, value))  # last in the hierarchy











