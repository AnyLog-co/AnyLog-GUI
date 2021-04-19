
import json


# -----------------------------------------------------------------------------------
# String to JSON
# -----------------------------------------------------------------------------------
def string_to_json( data_str ):

    try:
        json_struct = data_str.json()
    except ValueError as err:
        error_msg = "Failed to map string to JSON: %s" % str(err)
        json_struct = None
    except KeyError as err:
        error_msg = "Failed to map string to JSON: %s" % str(err)
        json_struct = None
    except:
        error_msg = "Failed to map string to JSON: %s" % str(err)
        json_struct = None

    return [json_struct, error_msg]


