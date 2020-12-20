import argparse
import query_data 

def get_nodes(conn:str, company:str)->dict: 
   """
   :Step 1: 
      Based on company name get correelated nodes from network 
   :args: 
      company:str - name of the company to query against 
   :param: 
      nodes:dict - dict of node names + results 
      query:str - query to execute on AnyLog
   :return: 
      nodes
   """
   nodes = {'operator': [], 'publisher': [], 'query': [], 'cluster': []} 
   query = 'blockchain get %s where company = %s' 
   for node in nodes: 
       qry = query % (node, company) 
       nodes[node] = query_data.query_blockchain(conn, qry) 

   return nodes 
   
def get_status(nodes:dict)->dict: 
   """"
   :Step 2: 
      Get status for each node in the network
   :args: 
      nodes:dict - list of nodes 
   :param: 
      status_nodes:dict - dict onf nodes to get status of 
      conn:str - conn to node 
   :return: 
      nodes with status  
   """
   status_nodes = {'operator': {}, 'publisher': {}, 'query': {}} 
   for node in nodes: 
       if node in status_nodes and nodes[node] != {}: 
          for nd in nodes[node]: 
             conn = '%s:%s' % (nd[node]['ip'], nd[node]['rest port']) 
             status_nodes[node][conn] = {'name': nd[node]['name'], 'status': query_data.get_status(conn)}

   return status_nodes

def print_status(nodes:dict): 
   """
   :Step 3: 
      For each node in network print status 
   :args: 
      nodes:dict - list of nodes & status 
   :print: 
      node
        name --> ip:port --> status 
   """
   print_output = '\t%s ==> %s ==> %s' 
   for node in nodes: 
      if nodes[node] == {}: 
         print('%s ==> no nodes' % node)
      else: 
          print(node) 

      for ip in nodes[node]: 
         name = nodes[node][ip]['name'] 
         status = 'running'
         if nodes[node][ip]['status'] is False: 
            status = 'not running'  
         print(print_output %  (name, ip, status)) 

def get_metadata(conn:str)->dict: 
   """
   :Step 4: 
   Get cluster 
   :issue: 
      207 - https://www.google.com/url?q=https://github.com/AnyLog-co/AnyLog-Network/issues/207&sa=D&ust=1607459543967000&usg=AOvVaw30fwbNEMUiRA6QKMvULH2r
   :args: 
      conns:str - connection IP + Port
   :param; 
      metadata:list - list of metadat 
      results:str - raw metadata 
   """
   #results = query_data.get_metadata() 
   #metadata = results.split('\n') 

   """
   basic code executed in query_data.get_metadata 
   operator1 AL > blockchain load metadata
   operator1 AL > blockchain query metadata
   """
   metadata = ['anylog ==> sample_data ==> ping_sensor ==> 9c1c0aac23fe4b48a8e51acbc1d98ac2 ==> 10.0.0.8:2058'] 
   return metadata 

def print_metadata(metadata:dict, company:str): 
   """
   :Step 4: 
   Print metadata that's part of the company's network 
   :args: 
      metadata:dict - metadata 
      company:str - company name
   :print:
      company ==> dbms ==> table ==> cluster_id ==> operator IP/Port 
   """
   for mtadata in metadata: 
      if company in mtadata: 
         print(mtadata) 

def get_tables(conn:str, metadata:list, company:str)->dict: 
   """
   :Step 5: 
   Get tables based on database 
   :args: 
      conn:str - connection IP + Port 
      metadata:dict - metadata 
      company:str - comapny name 
   :params: 
      tables:dict - tables
   :return:
      tables 
   """
   tables = {} 
   for mtadata in metadata: 
       if company in mtadata: 
           lmetadata = mtadata.split(' ==> ')
           dbms = lmetadata[1]
           name = lmetadata[2] 
           table = query_data.get_tables(conn, dbms, name) 
           tables['%s.%s' % (dbms, name)] = table['table']['create'].replace('  ', '\n\t\t').replace(');', '\n\t);', 1).replace(';', ';\n\t').replace(' CREATE', 'CREATE') 

   return tables 
   
def print_tables(tables:dict):
   """
   :Step 5:
   Print tables 
   :args: 
      tables:dict - create statement
   :print: 
      dbms.name 
         CREATE 
   """
   stmt = '%s\n\t%s' 
   for table in tables: 
       print(stmt % (table, tables[table]))

def main(): 
   """
   Print information regarding network based on company 
      - Status of each node 
      - clusters of each node 
      - tables within cluster 
   :positional arguments:
      conn        REST connection IP:Port
      company     REST connection IP:Port
   :optional arguments:
      -h, --help       [HELP]         show this help message and exit
   :param: 
      nodes:dict - dict of nodes in network 
      status:dict - status of each node in network 
      metadata:str - (general) metadata from network 
      tables:dict - list of tables & definition 
   """
   parser = argparse.ArgumentParser() 
   parser.add_argument('conn',    type=str, default='127.0.0.1:2049', help='REST connection IP:Port') 
   parser.add_argument('company', type=str, default='anylog', help='REST connection IP:Port') 
   args = parser.parse_args () 

   # Status 
   print('Status of each node')
   print('--------------------')
   nodes = get_nodes(args.conn, args.company) 
   status = get_status(nodes) 
   print_status(status)

   print('\n') 

   # Cluster metadata 
   print('Info for each cluster') 
   print('---------------------')
   metadata = get_metadata(args.conn) 
   print_metadata(metadata, args.company)

   print('\n') 

   print('tables')
   print('------') 
   tables = get_tables(args.conn, metadata, args.company)
   print_tables(tables) 


if __name__ == '__main__': 
   main() 