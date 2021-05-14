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


import requests
from requests.exceptions import HTTPError

# -----------------------------------------------------------------------------------
# GET request
# -----------------------------------------------------------------------------------
def do_get(url, headers_data):

    try:
        response = requests.get(url=url, params=None, verify=False, headers=headers_data)
    except HTTPError as http_err:
        error_msg = "REST GET HTTP Error from %s Error: %s" % (str(url), str(http_err))
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