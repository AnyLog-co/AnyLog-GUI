
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
class AnyLogTable(object):
    def __init__(self, attr_name_val:list):
        for entry in attr_name_val:
            exec("self.{} = '{}'".format(entry[0], entry[1]))

# -----------------------------------------------------------------------------------
# A class to maintain an entry in a table
# Dynamically set the class variables
# attr_name_val is a list whereas entries are tupples: attribute name + values
# -----------------------------------------------------------------------------------

class AnyLogItem(object):
    def __init__(self, attr_name_val:list):
        for entry in attr_name_val:
            exec("self.{} = '{}'".format(entry[0], entry[1]))