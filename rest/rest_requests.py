import ast
import json
import requests 

class Query: 
   def __init__(self, conn:str):
      """
      Class that supports different types of queries 
      :param: 
            self.conn:str - IP and port
      """
      self.conn = conn 

   def __get_obj(self, header:dict)->requests.models.Response: 
      """
      Execute actual query
      :args: 
         conn:str - IP and port 
         header:dict - query to execute
      :param: 
         r:requests.models.Response - Data from request
      :return: 
         if fails return None, else return data as requests.models.Response object 
      """
      try:
         r = requests.get('http://%s' % self.conn, headers=header)
      except: 
         r = None

      if r != None and r.status_code != 200: 
         r = None 
      return r 
    
   def __format_blockchain(self, data:str)->dict: 
      """"
      Given info from blockchain, format data to be useable
      :args: 
         data:str - data from blockchain
         dict_data:list - formated data  
      :return: 
         dict_data 
      """
      dict_data = [] 
      for dta in data.split('}, {'):
         # fix formating 
         if dta[0] == '[':
            dta = dta.split('[', 1)[-1]
         if dta[-1] == ']':
            dta = dta.rsplit(']', 1)[0]
         if dta[0] != '{':
            dta = '{' + dta
         if dta[-2] != '}':
            dta = dta + '}'
         # convert to dict 
         dict_data.append(ast.literal_eval(dta.replace("'", '"')))

      return dict_data

   def get_blockchain(self)->dict: 
      """
      Get IP, TCP port and REST port for each node in the network
      :param: 
         header:dict - query 
         blockchain:dict - list of nodes 
            {ip: {tcp, rest}}
      :return: 
         blockchain    
      """
      blockchain = {}
      for node in ['master', 'query', 'operator', 'publisher']: 
         header = {'type': 'info', 'details': 'blockchain get %s' % node} 
         r = self.__get_obj(header)
         try:
            data = r.text
         except:
            data = None

         if data is not None: 
            for nod in self.__format_blockchain(data):
               for typ in nod: 
                  if typ not in blockchain: 
                     blockchain[typ] = {} 
                  if nod[typ]['ip'] not in blockchain: 
                     blockchain[typ][nod[typ]['ip']] = {'tcp': '', 'rest': ''}
                     if 'port' in nod[typ]: 
                        blockchain[typ][nod[typ]['ip']]['tcp'] = int(nod[typ]['port'])
                     if 'rest port' in nod[typ]:
                        blockchain[typ][nod[typ]['ip']]['rest'] = int(nod[typ]['rest port'])

      return blockchain
   
   def execute_query(self, logical_db:str, query:str, servers:str=None)->list:
      """
      Execute query
      :args:
         logical_db:str - database
         query:str - query to execute
         servers:str - servers to execute query against (optional)
      :param:
         header:str - query
         results:list - results from query
      :return:
         results
      """
      header = {
         'type': 'sql',
         'dbms': logical_db,
         'details': query,
         'servers': servers
      }

      r = self.__get_obj(header)
      try:
         results = r.json()['Query']
      except:
         results = []
      return results

   def get_machine_data(self)->dict: 
      """
      Get information correlated specifically to node 
      :queries: 
        get cpu info 
        get disk usage / <-- convert from Bytes to MB
        get memory info 
      :param: 
         header:dict - query 
         info:dict - data from queries
      :return; 
         info 
      """
      info = {} 
      header = {'type': 'info', 'details': 'get cpu info'}
      r = self.__get_obj(header)
      try:
         data = r.text
      except: 
         data = None 

      if data is not None: 
         for dta in data.split('\n'): 
            info['CPU %s' % dta.split(':')[0].lstrip().rstrip().capitalize()] = dta.split(':')[1].lstrip().rstrip()

      header = {'type': 'info', 'details': 'get disk usage /'}
      r = self.__get_obj(header)
      try:
         data = r.text
      except: 
         data = None 

      try: 
         data = ast.literal_eval(data.replace('[', '').replace(']', ''))
      except: 
         data = None 

      if data is not None:
         for dta in data: 
            if dta.lower() != 'node': 
               info['Disk %s' % dta.lstrip().rstrip().capitalize()] = '%sMB' % "{:,.2f}".format(round(int(data[dta].replace(',','')) / 1000000, 3))

      header = {'type': 'info', 'details': 'get memory info'}
      r = self.__get_obj(header)
      try:
         data = r.text
      except: 
         data = None 

      if data is not None: 
         for dta in data.split('\n'): 
             if dta != '': 
                info['Memory %s' % dta.split(':')[0].lstrip().rstrip().capitalize()] = dta.split(':')[1].lstrip().rstrip()
      
      return info 

   def get_operators(self)->dict:
      """
      Get list of operators and databases from blockchain
      :args: 
        header:dict - query 
        blockchain:dict - data from blockchain 
           {operator_conn: {db_name: [table_list]}} 
      :return:
        blockchain
      """
      header = {'type': 'info', 'details': 'blockchain get operator'}
      blockchain = {}
      r = self.__get_obj(header)
      try:
         data = r.text
      except:
         data = None

      if data is None:
         return blockchain

      nodes = self.__format_blockchain(data) 
      for node in nodes: 
        # get relevent info 
         conn = '%s:%s' % (node['operator']['ip'], node['operator']['port'])
         if conn not in blockchain:
            blockchain[conn] = {}

         dbms = node['operator']['dbms']
         if dbms not in blockchain[conn]:
            blockchain[conn][dbms] = []

         tables = node['operator']['table']
         if not isinstance(tables, list):
            tables = tables.split(',')
         for table in tables:
            blockchain[conn][dbms].append(table)

      return blockchain

   def get_processes(self)->dict: 
      """
      Get list of processes running on node
      :param: 
         header:dict - query 
         procces:dict - results
      """
      header = {'type': 'info', 'details': 'show processes'}
      process = {} 
      r = self.__get_obj(header)
      try: 
         data = r.text
      except Exception as e: 
         data = None 

      if data is None:
         return process 
      
      for p in data.split('\n'): 
         if p != '': 
            key = p.split(' : ')[0].rsplit(' ')[0]
            value = p.split(' : ')[1].split('\r')[0]
            process[key] = value
            #process[p.split(' : ')[0].lstrip()] = p.split(' : ')[1]
      return process 

   def get_status(self)->str: 
      """
      Get status code
      :param: 
         header:dict - query to execute
      :return: 
         Status 
      """
      header = {'type': 'info', 'details': 'get status'}
      r = self.__get_obj(header)
      try:
          status = r.json()['Status']
      except:
         status = '%s not running' % self.conn
      return status

   def get_tables(self)->dict: 
      """
      Get create tables for each database 
      :args:
         headers:dict - query 
         blockchain:dict - data from blockchain
            {db_name.table_name: create_stmt} 
      :return: 
         blockchain: 
      """
      header = {'type': 'info', 'details': 'blockchain get table'} 
      blockchain = {} 
      r = self.__get_obj(header) 
      try: 
         data = r.text
      except: 
         data = None 

      if data is None: 
         return blockchain 

      tables = self.__format_blockchain(data) 
      for table in tables: 
         name = '%s.%s' % (table['table']['dbms'], table['table']['name']) 
         if name not in blockchain: 
            blockchain[name] = table['table']['create'].replace('  ','\n\t').replace('; ',';\n') 

      return blockchain 

