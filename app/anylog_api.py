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

# -----------------------------------------------------------------------
# AnyLog Connectors
# -----------------------------------------------------------------------

# -----------------------------------------------------------------------
# Go over the structure and the form and build the AnyLog Policy.
# Send the policy to the network
# -----------------------------------------------------------------------
def deliver_policy(policy_struct, policy_info):
    '''
    Build the AnyLog Policy from the form info
    Deliver the form to the network
    '''

    policy = {}
    policy_body = {}

    # Go over the policy structure and create the policy
    policy_type = policy_struct['key']
    policy[policy_type] = policy_body

    struct = policy_struct['struct']

    # go over the struct and pull the info from the form
    for entry in struct:
        attr_name = entry['key']
        attr_val = policy_info[attr_name]
        policy_body[attr_name] = attr_val


