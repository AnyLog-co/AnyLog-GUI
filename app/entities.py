
from flask_table import Table, Col, LinkCol


class Companies(Table):
    company = Col('Company')
    select = LinkCol('Edit', 'machine', url_kwargs=dict(company='company'))

class Item(object):
    def __init__(self, name, description = None):
        self.company = name
        self.description = description

# -----------------------------------------------------------------------------------
# A class to maintain a table
# Dynamically set the class variables
# attr_name_val is a list whereas entries are tupples: attribute name + values
# -----------------------------------------------------------------------------------
class AnyLogTable(Table):
    company = Col('Company')
    def set_col(self, gui_level, attr_name_val:list):
        '''
        Define the the class attributes
        Select to view the JSON or get the children
        '''
        for entry in attr_name_val:
            setattr(AnyLogTable, entry, Col(entry))
            #exec("AnyLogTable.{} = Col('{}')".format(entry, entry))

        AnyLogTable.view = LinkCol('view', 'tree', url_kwargs=dict(company='company')) # SHow more info of the JSON
        AnyLogTable.select = LinkCol('select', 'tree', url_kwargs=dict(level=gui_level + 1)) # Move to the next level

# -----------------------------------------------------------------------------------
# A class to maintain an entry in a table
# Dynamically set the class variables
# attr_name_val is a list whereas entries are tupples: attribute name + values
# -----------------------------------------------------------------------------------

class AnyLogItem(object):
    def __init__(self, attr_name_val:list):
        for entry in attr_name_val:
            exec("self.{} = '{}'".format(entry[0], entry[1]))