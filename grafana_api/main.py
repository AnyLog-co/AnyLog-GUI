import argparse
import os 
from support import print_data 
from grafana_db import GrafanaDB
from update_dashboard import main as update_dashboard 


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
    Based on user input update Grafana
    :positional arguments:
       db_path                  SQLite database file with path
    :optional arguments:
       -h,  --help                                   show this help message and exit
       -d,  --dashboard-name     DASHBOARD_NAME      Dashboard Title                     (default: New dashboard Copy)
       -g,  --graph-title        GRAPH_TITLE         Graph pannel title                  (default "" | Grafana preset: Panel Title) 
       -p,  --print-data         PRINT_DATA          Print JSON from dashboard           (default; False) 
       -ud, --update-dashboard   UPDATE_DASHBOARD    Update component(s) of dashboard    (default: none | options: none,all,dashboard_name,graph_title,graph_query)
    :param: 
       statues:list - list of boolians 
       full_db_path:str - from db_path, the full database path 
       gdb:grafana_db.GrafanaDB - class connection to GrafanaDB 
       rows:list - based on query extracted rows 
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('db_path',                   type=str,  default='/var/snap/docker/common/var-lib-docker/volumes/grafana-data/_data/grafana.db',  help='SQLite database file with path') 
    parser.add_argument('-d',  '--dashboard-name',   type=str,  default='New dashboard Copy',                                                            help='Dashboard Title') 
    parser.add_argument('-g',  '--graph-title',      type=str,  default='',                                                                              help='Graph pannel title - the default graph name is "Panel Title"')
    parser.add_argument('-p', '--print-data',        type=bool, nargs='?',      const=True, default=False,                                               help='Print JSON from database')                                                     
    parser.add_argument('-ud', '--update-dashboard', type=str,  default="none", choices=['none', 'all', 'dashboard_name', 'graph_title', 'graph_query'], help='Update component(s) of dashboard') 
    args = parser.parse_args()
    
    statuses = []
    full_db_path = os.path.expanduser(os.path.expandvars(args.db_path))
    if not args.dashboard_name:
       print('Dashboard title is required') 
       exit(1) 
    gdb = GrafanaDB(full_db_path) # if fails, python exists with error  

    rows = gdb.extract_data(args.dashboard_name, args.graph_title) 
    
    if rows == []: 
       print('No data extracted based on the information provided') 
       exit(1) 
    
    if args.print_data is True:
       print_data(rows) 
    if args.update_dashboard != 'none': 
       # If enabled (ie not none) update information. Note, if graph_title is set then update information only correlated to graph title    
       status = update_dashboard(args.update_dashboard, gdb, rows, args.dashboard_name, args.graph_title) 
       statuses.append(status) 

    gdb.close_conn()

if __name__ == '__main__': 
   main() 
