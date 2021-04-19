


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