
from flask_table import Table, Col, LinkCol


class Companies(Table):
    company = Col('Company')
    select = LinkCol('Edit', 'machine', url_kwargs=dict(company='company'))

class Item(object):
    def __init__(self, name, description = None):
        self.company = name
        self.description = description
