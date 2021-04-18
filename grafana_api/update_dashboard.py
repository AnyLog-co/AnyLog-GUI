import json 

def __convert_to_dict(data:str)->dict: 
   """
   Convert data from JSON to dict
   :args: 
      data:str - data object to convert
   :param: 
      dict_data:dict - data as dictionary 
   :return: 
      dict_data 
   """
   dict_data = {} 
   try:
      dict_data = json.loads(data) 
   except Exception as e: 
      print('Failed to convert data to dict from JSON (Error: %s' % e)

   return dict_data 

def __convert_to_json(data:dict)->str: 
   """
   Convert data from dict to JSON 
   :args: 
      data:dict - data object to convert 
   :param: 
      str_data:str - data as string 
   :return: 
      str_data 
   """
   str_data = None 
   try: 
      str_data = json.dumps(data) 
   except Exception as e: 
      print('Failed to convert to string from dict (Error: %s)' % e) 

   return str_data 

def update_graph_name(data:str)->str: 
   """
   Update graph name
   :args: 
      data:str - data object to convert
   :param: 
      dict_data:dict - data as dictionary  
      default:str - default value from data 
      graph_name:str - new graph name
   :return: 
      update data
   """
   dict_data = __convert_to_dict(data) 
   if dict_data: 
      default = dict_data['panels'][0]['title'] 
      graph_name = input('New Graph Name (Default: %s): ' % default) 
      if not graph_name: 
         graph_name = default 
      else: 
         dict_data['panels'][0]['title'] = graph_name
      data = __convert_to_json(dict_data) 

   return data 

def update_graph_query(data:str)->str: 
   """
   Update graph name
   :args: 
      data:str - data object to convert
   :param: 
      dict_data:dict - data as dictionary  
      graph_name:str - new graph name
   :return: 
      data
   """
   dict_data = __convert_to_dict(data) 
   if dict_data: 
      print(dict_data['panels'][0]['targets'])
     # graph_name = input('New Graph Name: ') 

