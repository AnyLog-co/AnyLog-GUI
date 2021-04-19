from grafana_db import GrafanaDB
from support import convert_to_dict, convert_to_json, convert_to_str

def update_dashboard_name(gdb:GrafanaDB, dashboard_name:str)->(bool, str): 
   """
   Update dashboard name
   :args: 
      gdb:GrafanDB - connection to database 
      dashboard_name:str - dashboard name 
   :param:
      status:bool 
      new_dashboard_name:str - new dashboard name
   :return: 
      status, new_dashboard_name
   """
   new_dashboard_name = input('New dashboard name [default: %s]: ' % dashboard_name) 
   if not new_dashboard_name: 
      new_dashboard_name = dashboard_name
   
   if new_dashboard_name != dashboard_name: 
      status = gdb.update_dashboard_name(dashboard_name, new_dashboard_name) 

   if not status: 
      new_dashboard_name = dashboard_name 

   return status, new_dashboard_name 
   
def update_graph_title(gdb:GrafanaDB, dashboard_name:str, data:str)->bool: 
   """
   Update graph name
   :args: 
      gdb:grafana_db.GrafanaDB - connection to database 
      dashboard_name:str - dashboard title 
      data:str - data object to convert
   :param: 
      status = bool 
      dict_data:dict - data as dictionary  
      default:str - default value from data 
      graph_title:str - new graph name
   :return: 
      update data
   """
   status = True 
   new_data = None
   dict_data = convert_to_dict(data) 
   if dict_data: 
      default = dict_data['panels'][0]['title'] 
      graph_title = input('New Graph Name (Default: %s): ' % default) 
      if not graph_title: 
         graph_title = default 
      else: 
         dict_data['panels'][0]['title'] = graph_title
      new_data = convert_to_json(dict_data) 
   else: 
      status = False 
   
   if new_data != {}:
      status = gdb.update_data(dashboard_name, new_data, data)  
   else: 
      status = False 

   return status  

def update_graph_query(gdb:GrafanaDB, dashboard_name:str, data:str)->str: 
   """
   Update graph name
   :args: 
      data:str - data object to convert
   :param: 
      dict_data:dict - data as dictionary  
      graph_title:str - new graph name
   :return: 
      data
   """
   status = True 
   dict_data = convert_to_dict(data) 
   if dict_data: 
      # Update table to query against 
      default = dict_data['panels'][0]['targets'][0]['target'] 
      table = input('Table to query [default: %s]: ' % default) 
      if not table: 
         table = default 
      dict_data['panels'][0]['targets'][0]['target'] = table 

      # Update query information 
      default = dict_data['panels'][0]['targets'][0]['data'].replace("\n", "")
      query = input('Query [default: %s]: ' % default) 
      if not query: 
          query = default 
      if isinstance(query, dict): 
         query = convert_to_json(query) 
      if query: 
         dict_data['panels'][0]['targets'][0]['data'] = query       
      new_data = convert_to_json(dict_data) 
   if new_data != {}:
      status = gdb.update_data(dashboard_name, new_data, data)  
   else: 
      status = False 

   return status  
     

def main(cmd:str, gdb:GrafanaDB, data:str, dashboard_name:str, graph_title:str)->bool: 
   """
   Process to update information in grafana based on dashboard and graph name respectivly
   :args: 
      cmd:str - process(es) to execute 
      gdb:grafana_db.GrafanaDB - connection to database 
      data:str - data from query 
      dashboard_name:str - dashboard name
      graph_title:str - graph name
   :param: 
      status:bool - list of statues from each process  
   :return: 
      status
   """
   statuses = [] 
   if cmd == 'dashboard_name' or cmd == 'all': 
      status, dashboard_name = update_dashboard_name(gdb, dashboard_name)
      statuses.append(status) 
   if cmd == 'graph_title' or cmd == 'all': 
      for graph in data: 
         graph = graph[0]
         if isinstance(graph[0], bytes):
            graph = convert_to_str(graph) 
         status = update_graph_title(gdb, dashboard_name, graph)
         statuses.append(status) 
   if cmd == 'graph_query' or cmd == 'all': 
      for graph in data: 
         graph = graph[0]
         if isinstance(graph[0], bytes):
            graph = convert_to_str(graph) 
         status = update_graph_query(gdb, dashboard_name, graph)
         statuses.append(status)

   return all(status == True for status in statuses) 

