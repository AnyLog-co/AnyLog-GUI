



import json


# -----------------------------------------------------------------------------------
# String to JSON
# -----------------------------------------------------------------------------------
def string_to_json( data_str )

    try:
        json_struct = response.json()
    except ValueError as err:
        error_msg = "Failed to map string to JSON: %s" % str(err)
        json_struct = None
    except KeyError as err:
        error_msg = "Failed to map string to JSON: %s" % str(err)
        json_struct = None
    except:
        error_msg = "Failed to map string to JSON: %s" % str(err)
        json_struct = None

    return [json_struct, err_msg]


