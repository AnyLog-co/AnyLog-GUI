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
import base64
# ---------------------------------------------------------------------------------
# Encrypt random string using base64
#
#
'''
Example: Setting basic authentication on the AnyLog Node:

set local password = 123456
set user authentication on
id add user where name = ori and password = 123 

id remove user where name = ori
'''
# ---------------------------------------------------------------------------------
def encrypt_string(data_string):
    '''
    Given a string, return encrypted string using base64 encoding.
    This conversion supports basic auth
    '''

    try:
        data_bytes = data_string.encode('ascii')
        base64_bytes = base64.b64encode(data_bytes)
    except:
        base64_bytes = None
    #base64_message = base64_bytes.decode('ascii')

    return base64_bytes
