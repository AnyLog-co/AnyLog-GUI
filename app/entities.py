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

import copy

functions_with_order_ = ["avg", "min", "max", "range", "count"]

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
            if isinstance(entry[1], str):
                exec("self.{} = '{}'".format(entry[0], entry[1]))
            else:
                exec("self.{} = {}".format(entry[0], entry[1]))

# -----------------------------------------------------------------------------------
# A class to maintain an AnyLog Table definitions
# -----------------------------------------------------------------------------------
class AnyLogTable(object):
    '''
    Maintains table data and HTML print info. Note: first col is always a unique ID
    table_name - a name representing the table
    column_names - a list with the table names
    column_keys - per each column - the attribute name in the JSON
    table_data - a list representing the rows whereas each entry is the list of the column values.
    extr_col - additional table columns like checkbox or button
                A list of attr-val pairs: Col-Name + HTML Input type (https://www.w3schools.com/html/html_form_input_types.asp)
                fir example: [('select','checkbox'), ('View','button')]
    '''
    def __init__(self, table_name:str, column_names:list, column_keys:list, rows:list, extr_col:list):
        self.table_name = table_name
        self.column_names = column_names
        self.column_keys = column_keys
        self.rows = rows
        self.extr_col = extr_col


# -----------------------------------------------------------------------------------
# AnyLog date time definitions for a dashboard or a panel
# -----------------------------------------------------------------------------------
class AnyLogDateTime():
    def __init__(self):
        self.reset()

    def reset(self):
        self.start_date_time = None
        self.end_date_time = None
        self.range_date_time = None      # i.e. -2M

    def get_start(self):
        return self.start_date_time
    def get_end(self):
        return self.end_date_time
    def get_range(self):
        return self.range_date_time

    def set_date_time(self, key, value):
        if key == "start":
            self.start_date_time = value
        elif key == "end":
            self.end_date_time = value
        else:
            self.range_date_time = value


# -----------------------------------------------------------------------------------
'''
The Dashboard setup

Dashboard ---> Panels --->  Projection ---> Functions

- functions is a list withe the function to process on the table
- projection defines the table
- panel includes multiple tables that are graphed together
- dashboard contains a report
 
'''
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
# AnyLog Projection Definitions
# -----------------------------------------------------------------------------------
class AnyLogProjection():
    def __init__(self, policy_name, dbms_name, table_name, functions, query, where_cond):
        self.policy_name = policy_name
        self.dbms_name = dbms_name
        self.table_name = table_name
        self.functions = functions          # The functions to process on the table
        self.query = query           # The query to execute default is increments
        self.where_cond = where_cond

        self.timestamp_column = 'timestamp'     # Default time column name
        self.value_column = 'value'             # Default value column name


# -----------------------------------------------------------------------------------
# AnyLog Panel Definitions
# -----------------------------------------------------------------------------------
class AnyLogPanel():
    def __init__(self):
        self.panel_name = None              # A unique name
        self.panel_type = "Graph"         # The type of display ("Graph" is the default)
        self.projection_list = []
        self.default_functions = [] # A list of default functions if not specified for each projection

    # -----------------------------------------------------------------------------------
    # Add a new projection to the panel
    # -----------------------------------------------------------------------------------
    def add_projection(self, policy_name, dbms_name, table_name, functions, query, where_cond):

        if not functions:
            functions = self.default_functions
        if not query:
            query = "increments"


        self.projection_list.append(AnyLogProjection(policy_name, dbms_name, table_name, functions, query, where_cond))

# -----------------------------------------------------------------------------------
# AnyLog Dashboard Definitions
# -----------------------------------------------------------------------------------
class AnyLogDashboard():
    def __init__(self):
        self.reset()
        self.date_time = AnyLogDateTime()
        self.default_functions = {}

    def reset(self):
        self.panels = []        # List of panels
        self.default_functions = {}

    def get_panels_count(self):
        return len(self.panels)
    # -----------------------------------------------------------------------------------
    # Add a projection list to the panel
    # -----------------------------------------------------------------------------------
    def add_projection_list(self, panel_name, panel_type, policy_name, dbms_name, table_name, functions, query, where_cond):

        if not functions:
            # Take the default for the type of panel
            if panel_type.lower() in self.default_functions:
                functions = copy.deepcopy(self.default_functions[panel_type.lower()])


        panel = self.get_set_panel(panel_name)
        panel.panel_type = panel_type
        panel.add_projection(policy_name, dbms_name, table_name, functions, query, where_cond)

    # -----------------------------------------------------------------------------------
    # Default setup = graph + Gauge
    # -----------------------------------------------------------------------------------
    def set_default(self):

        self.default_functions["graph" ] = ["min","max","avg"]
        self.default_functions["gauge"] = ["min","max","avg"]

        self.set_date_time("range", "-2M")      # Last 2 Months

    # -----------------------------------------------------------------------------------
    # Get the default setup for the type of graph
    # -----------------------------------------------------------------------------------
    def get_default_functions(self, panel_type):
        '''
        Return the default functions fir the type (graph/gauge) of panel
        '''

        global functions_with_order_
        if panel_type in self.default_functions:
            functions_selected =  self.default_functions[panel_type]
        else:
            functions_selected = []

        functions_not_selected = list(set(functions_with_order_) - set(functions_selected))
        functions_selected.sort(key = order_func)
        functions_not_selected.sort(key = order_func)
        return [functions_selected, functions_not_selected]

    # -----------------------------------------------------------------------------------
    # Add a new panel
    # -----------------------------------------------------------------------------------
    def add_panel(self,panel):
        self.panels.append(panel)

    # -----------------------------------------------------------------------------------
    # Set report date and time
    # -----------------------------------------------------------------------------------
    def set_date_time(self,key, value):
        '''
        key values are "start", "end" or range"
        '''
        self.date_time.reset()      # Delete older defs
        self.date_time.set_date_time(key, value)

    # -----------------------------------------------------------------------------------
    # Add a default function to a panel and create new panel if no panel with the needed ID
    # The default function is set for a projection without functions definitions
    # -----------------------------------------------------------------------------------
    def add_default_function(self, panel_type, function):
        '''
        add defualt function to the panel

        params panel_type: graph, gauge
        params function: "min", "max" etc.
        '''

        if not panel_type in self.default_functions:
            self.default_functions[panel_type] = []
        self.default_functions[panel_type].append(function)  # A list of default functions if not specified for each projection


    # -----------------------------------------------------------------------------------
    # Get or set a panel - if a panel exists return the panel, else add a new panel
    # -----------------------------------------------------------------------------------
    def get_set_panel(self, panel_name):

        returned_panel = None
        for panel in self.panels:
            if panel.panel_name == panel_name:
                returned_panel = panel
                break

        if not returned_panel:
            returned_panel = AnyLogPanel()    # Set a new panel
            returned_panel.panel_name = panel_name
            self.add_panel(returned_panel)

        return returned_panel

# -----------------------------------------------------------------------------------
# Maintain order - avg, min, max, diff, count
# -----------------------------------------------------------------------------------
def order_func(a):
    global functions_with_order_
    return functions_with_order_.index(a)

