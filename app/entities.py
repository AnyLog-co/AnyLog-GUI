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

# -----------------------------------------------------------------------------------
# A class to maintain an AnyLog Table table
# -----------------------------------------------------------------------------------
class AnyLogTable(object):
    '''
    Maintains table data and HTML print info
    table_name - a name representing the table
    column_names - a list with the table names
    column_keys - per each column - the attribute name in the JSON
    table_data - a list representing the rows whereas each entry is the list of the column values.
    extr_col - additional table columns like checkbox or button
                A list of attr-val pairs: Col-Name + HTML Input type (https://www.w3schools.com/html/html_form_input_types.asp)
                fir example: [('select','checkbox'), ('View','button')]
    '''
    def __init__(self, table_name:str, column_names:list, column_keys:list, table_data:list, extr_col:list):
        self.table_name = table_name
        self.column_names = column_names
        self.column_keys = column_keys
        self.table_data = table_data
        self.extr_col = extr_col
