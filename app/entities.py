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
from flask_table import Table, Col, LinkCol


class Item(object):
    def __init__(self, name, description = None):
        self.company = name
        self.description = description
# -----------------------------------------------------------------------------------
# A class to maintain an entry in a table
# Dynamically set the class variables
# attr_name_val is a list whereas entries are tupples: attribute name + values
# -----------------------------------------------------------------------------------

class AnyLogItem(object):
    def __init__(self, attr_name_val:list):
        for entry in attr_name_val:
            exec("self.{} = '{}'".format(entry[0], entry[1]))