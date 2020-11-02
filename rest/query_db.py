import argparse
from rest_requests import Query 


def main(): 
   """
   Main to execute queery
   :positional arguments:
      conn                  REST connection IP:Port
      logical_db            logical database to query from
      query                 query to execute
   :optional arguments:
      -h, --help    HELP      show this help message and exit
      -s, --servers SERVERS   specific servers to query against
   :sample calls:
      python3 AnyLog-Network/tests/gui/query_db.py 127.0.0.1:2049 sample_db "SELECT COUNT(*) FROM test WHERE timestamp >= '2020-10-31 10:35:00'" 
      
      python3 AnyLog-Network/tests/gui/query_db.py 127.0.0.1:2049 sample_db "SELECT col FROM test WHERE timestamp >= '2020-10-31 10:35:00'" -s 10.0.0.23:2048,10.0.0.25:2048
   """

   parser = argparse.ArgumentParser() 
   parser.add_argument('conn',           type=str, default='127.0.0.1:2049',     help='REST connection IP:Port') 
   parser.add_argument('logical_db',      type=str, default='sample_data',        help='logical database to query from') 
   parser.add_argument('query',           type=str, default='SELECT * FROM test', help='query to execute') 
   parser.add_argument('-s', '--servers', type=str, default=None,                 help='specific servers to query against') 
   args = parser.parse_args () 

   query_cls = Query(args.conn) 
   results = query_cls.execute_query(args.logical_db, args.query, args.servers) 
   for result in results: 
      print('\t', result)

if __name__ == '__main__': 
   main()

