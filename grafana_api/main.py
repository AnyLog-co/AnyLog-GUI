import argparse
import os 
from grafana_db import GrafanaDB
import update_dashboard 


def __validate_db(db_path:str)->str:
   """
   Validate database exists
   :args:
      db_path:str - database path
   :param: 
      full_db_path:str - full database path
   :return: 
      full_db_path
   """
   full_db_path = None
   try: 
      full_db_path = os.path.expanduser(os.path.expandvars(db_path))
   except Exception as e: 
      print('Failed to extract db path (Error: %s)' % e)

   if full_db_path is None or not os.path.isfile(full_db_path):
      print('Failed to extract db path')
      exit(1) 

   return full_db_path 

def main(): 
    """
    :param: 
       full_db_path:str - from db_path, the full database path 
       gdb:grafana_db.GrafanaDB - class connection to GrafanaDB 
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('db_path',                 type=str, default='/var/snap/docker/common/var-lib-docker/volumes/grafana-data/_data/grafana.db', help='SQLite database file with path') 
    parser.add_argument('-d', '--dashboard-title', type=str, default='test',                                                                         help='Dashboard Title') 
    parser.add_argument('-g', '--graph-title',     type=str, default='Panel Title',                                                                  help='Graph pannel title') 
    args = parser.parse_args()

    full_db_path = os.path.expanduser(os.path.expandvars(args.db_path))
    gdb = GrafanaDB(full_db_path)
    rows = gdb.extract_data(args.dashboard_title, args.graph_title) 
    for row in rows: 
       update_row = update_dashboard.update_graph_name(row[0])
       gdb.update_table(row[0], update_row) 
    gdb.close_conn()

if __name__ == '__main__': 
   main() 
