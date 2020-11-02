import argparse
from rest_requests import Query 

def format_blockchain(query_cls:Query): 
   """
   Format blockchain
   :args: 
      query_cls:Queery - call Query class 
   :param: 
      blockchain:dict - results from blockchain
   :print: 
      node
         ip | tcp | rest 
   """
   blockchain = query_cls.get_blockchain() 
   for node in blockchain: 
      print(node) 
      for ip in blockchain[node]:
         print('\t%s | TCP: %s | REST: %s' % (ip, blockchain[node][ip]['tcp'], blockchain[node][ip]['rest']) )

def format_operator(query_cls:Query):
   """
   Format operators 
   :args: 
      query_cls:Query - call to Query class 
   :param: 
      operators:dict - results for operator data
   :print:
      operator conn
         database name 
            table name 
   """
   operators = query_cls.get_operators()
   print('Operators Info') 
   for operator in operators: 
      print('\t%s' % operator) 
      for db in operators[operator]: 
         print('\t\t%s' % db) 
         for table in operators[operator][db]: 
            print('\t\t\t%s' % table) 
      if operator != list(operators)[-1]: 
         print('\n')

def format_process(query_cls:Query): 
   """
   Format processes 
   :args: 
      query_cls:Query - call to query class 
   :param: 
      processes:dict - results for processes 
   :print: 
      process: status
   """
   processes = query_cls.get_processes()
   print('Processes Status')
   for process in processes: 
      print('\t%s: %s' % (process, processes[process]))

def format_tables(query_cls:Query): 
   """
   Format tables
   :args: 
      query_cls:Query - call query class 
   :param: 
      tables:dict - result from tables query 
   :print: 
      db_name.table_name 
      ------------------
      create_stmt 
   """
   tables = query_cls.get_tables() 
   for table in tables: 
      brk = ''
      for i in range(len(table)): 
         brk += '-'
      print('%s\n%s\n%s\n' % (table, brk, tables[table]))

def format_status(query_cls:Query): 
   """
   Format status
   :args:
      quett_cls:Query - ccall to query class 
   :param: 
      status:str - node status 
   :print: 
      status
   """
   status = query_cls.get_status() 
   print('Status: %s' % status) 

def main(): 
   """
   Based on arguments, print relevent info
   :positional arguments:
      conn                  REST connection IP:Port
   :optional arguments:
      -h, --help       [HELP]         show this help message and exit
      -a, --all        [ALL]          Get all possible info from node
      -b, --blockchain [BLOCKCHAIN]   Get general info about all nodes
      -o, --operator   [OPERATOR]     Get info about operators
      -p, --process    [PROCESS]      Get process info
      -s, --status     [STATUS]       Get status of specific node
      -t, --table      [TABLE]        Get info about tables
   """
   parser = argparse.ArgumentParser() 
   parser.add_argument('conn',               type=str,  default='127.0.0.1:2049',     help='REST connection IP:Port') 
   parser.add_argument('-a', '--all',        type=bool, nargs='?', const=True, default=False, help='Get all possible info from node') 
   parser.add_argument('-b', '--blockchain', type=bool, nargs='?', const=True, default=False, help='Get general info about all nodes') 
   parser.add_argument('-o', '--operator',   type=bool, nargs='?', const=True, default=False, help='Get info about operators') 
   parser.add_argument('-p', '--process',    type=bool, nargs='?', const=True, default=False, help='Get process info')  
   parser.add_argument('-s', '--status',     type=bool, nargs='?', const=True, default=False, help='Get status of specific node') 
   parser.add_argument('-t', '--table',      type=bool, nargs='?', const=True, default=False, help='Get info about tables') 
   args = parser.parse_args () 

   if args.all: 
      args.blockchain = True 
      args.operator = True 
      args.process = True
      args.status = True
      args.table = True

   query_cls = Query(args.conn) 
   if args.blockchain: 
      format_blockchain(query_cls)
      print('\n')
   if args.operator: 
      format_operator(query_cls)
      print('\n')
   if args.process: 
      format_process(query_cls) 
      print('\n')
   if args.status:
      format_status(query_cls) 
      print('\n')
   if args.table: 
      format_tables(query_cls) 

if __name__ == '__main__': 
   main()

