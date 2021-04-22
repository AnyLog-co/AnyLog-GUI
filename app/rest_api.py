


import requests
from requests.exceptions import HTTPError



# -----------------------------------------------------------------------------------
# GET request
# -----------------------------------------------------------------------------------
def do_get(url, headers_data):

    try:
        response = requests.get(url=url, params=None, verify=False, headers=headers_data)
    except HTTPError as http_err:
        error_msg = "REST GET HTTPError Error: %s" % str(http_err)
        response = None
    except Exception as err:
        error_msg = "REST GET Error: %s" % str(err)
        response = None
    else:
        error_msg = None

    return [response, error_msg]


    
# -----------------------------------------------------------------------------------
# Post request
# -----------------------------------------------------------------------------------
def do_post(url, headers_data, data_str = None, data_json = None):

    try:
        response= requests.post(url=url, headers=headers_data, data=data_str, json=data_json, verify=False)
    except HTTPError as http_err:
        error_msg = "REST POST HTTPError Error: %s" % str(http_err)
        response = None
    except Exception as err:
        error_msg = "REST POST Error: %s" % str(err)
        response = None
    else:
        error_msg = None

    return [response, error_msg]