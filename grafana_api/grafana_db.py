import sqlite3

class GrafanaDB: 
   def __init__(self, db_file:str):
      """
      Connnect to database and execute query data 
      :args: 
         db_file:str - database file 
      :param: 
         conn:sqlite3.Connection - connection to database 
         cur:sqlite3.Cursor - cursor based on connection 
      """
      self.conn, self.cur = self.__connect_db(db_file)
      if self.conn is None or self.cur is None: 
         exit(1) 

   def __connect_db(self, db_file)->(sqlite3.Connection, sqlite3.Cursor):
       """
       connect to database 
       :args: 
          db_file:str - database file 
       :param: 
          conn:sqlite3.Connection - connection to database 
          cur:sqlite3.Cursor - cursor based on connection
       :return: 
          conn, cur
       """
       conn = None
       cur = None 

       try: 
          conn = sqlite3.connect(db_file) 
       except Exception as e: 
          print('Failed to connect to database (Error: %s)' % e)
       
       if conn is not None: 
          try: 
             cur = conn.cursor()
          except Exception as e: 
             print('Failed to declare cursor (Error: %s)' % e)

       return conn, cur 

   def close_conn(self)->bool: 
      """
      close connection to database
      :param: 
         status:bool 
      :return: 
         status 
      """
      status = True 
      try: 
         self.conn.close() 
      except Exception as e: 
         print('Failed to close connection to database (Error: %s)' % e) 
         status = False 
      return status 

   def extract_data(self, dashboard_name:str, graph_title:str)->list:
      """
      extract data from database based on dashboard & graph titles respectivly
      :args: 
         dashboard_name:str - dashboard title 
         graph_title:str - graph title 
      :param: 
         status:bool 
         data:list - data extracted from database 
         sql:str - sql statement to extract data with 
      :return: 
         data          
      """
      status = True 
      data = [] 
      sql = "SELECT data FROM dashboard WHERE title='%s';" % dashboard_name
      if graph_title != '': 
         graph_title = '%' + graph_title + '%'
         sql = sql.replace(';', " AND data LIKE '%s';" % graph_title) 

      try: 
         self.cur.execute(sql) 
      except Exception as e: 
         print('Failed to execute query (Error: %s)' % e)
         status = False 

      if status is True: 
         try: 
            data = self.cur.fetchall()
         except Exception as e: 
            print('Failed to fetch data (Error: %s)' % e) 

      return data 

   def update_dashboard_name(self, old_dashboard_name:str, new_dashboard_name:str)->bool: 
      """
      update dashboard title 
      :args: 
         old_dashboard_name:str - original dashboard title 
         new_dashboard_name:str - new dashboard title 
      :param: 
         status:bool 
         sql:str - query being execute 
      :return: 
         status
      """
      status = True 
      sql = "UPDATE dashboard SET title = '%s' WHERE title = '%s';" % (new_dashboard_name, old_dashboard_name)
       
      try:
         self.cur.execute(sql)
      except Exception as e: 
         print('Failed to execute UPDATE (Error: %s)' % e)
         status = False
      
      if status: 
         try: 
            self.conn.commit()
         except Exception as e: 
            print('Failed to commit changes (Error: %s)' % e)
            status = False 

      return status 
         
   def update_data(self, dashboard_name:str, new_data:str, old_data:str)->bool: 
      """
      update dashboard table (data column) 
      :args: 
         dashboard_name:str - dashboard title 
         new_data:str - updated data 
         old_data:str - original data being replaced 
      :param: 
         status:bool
         sql:str - query being executed 
      :return: 
         status
      """
      status = True 
      sql = "UPDATE dashboard SET data = '%s' WHERE title = '%s' AND data = '%s';" % (new_data, dashboard_name, old_data)
      try:
         self.cur.execute(sql)
      except Exception as e: 
         print('Failed to execute UPDATE (Error: %s)' % e)
         status = False
      
      if status: 
         try: 
            self.conn.commit()
         except Exception as e: 
            print('Failed to commit changes (Error: %s)' % e)
            status = False 

      return status 

