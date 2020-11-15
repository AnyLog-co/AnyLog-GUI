import os 
import sqlite3 

class DBMS:
    def __init__(self, dbms_dir:str): 
        """
        Database correlated to user management of AnyLog-GUI
        :args: 
            dbms_dir:str - Database where data is stored 
        :params: 
           self.db_name:str -  database dir + Logical database name
        """
        dbms_dir = os.path.expandvars(os.path.expanduser(dbms_dir))
        if not os.path.isdir(dbms_dir): 
            os.makedirs(dbms_dir) 
        self.db_name = dbms_dir + '/anylog-gui.dbms' 

    def __execute_query(self, query_stmt): 
        """
        Execute query
        :args:
            query_stmt:str - Query to execute 
        :param: 
            conn:sqlite3.Connect - connection to SQLite3
        :return; 
            return query result, if fail return False 
        """
        results = None
        try: 
            with sqlite3.connect(self.db_name) as conn: 
                try: 
                    results = conn.execute(query_stmt) 
                except Exception as e: 
                    print('Failed to execute query (Error: %s)' % e)
                    results = False 
        except Exception as e: 
            print('Failed to connect to %s database (Error: %s)' % (self.db_name, e))
            results = False 
            
        return results 

    def create_users_table(self)->bool: 
        """
        Create Users database table
        :param:
            create_stmt:str - CREATE TABLE string
        :table:
            CREATE TABLE IF NOT EXISTS users(
                create_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, # Date when user gets created 
                update_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, # Update each time password gets changed 
                username VARCHAR NOT NULL DEFAULT 'new_user', 
                password VARCHAR NOT NULL DEFAULT 'user_password', 
                PRIMARY KEY(username), 
                KEY(username, password)
            ); 
        :return: 
           If query fails, it'll return False    
        """
        create_stmt = (
            "CREATE TABLE IF NOT EXISTS users("
            +"\n\tcreate_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            +"\n\tupdate_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP," 
            +"\n\tusername VARCHAR NOT NULL DEFAULT 'new_user',"
            +"\n\tpassword VARCHAR NOT NULL DEFAULT 'user_password',"
            +"\n\tPRIMARY KEY(username)"
            +"\n);"
        )
        return self.__execute_query(create_stmt) 

    def create_login_table(self)->bool:
        """
        Create Login table 
        :param:
            login_stmt:str - CREATE TABLE stmt
        :table:
            CREATE TABLE IF NOT EXISTS login(
                login_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, # Date when user logs-in 
                username VARCHAR NOT NULL DEFAULT 'new_user', 
                FOREIGN KEY(username) REFERENCE users(username) 
            ); 
        :return: 
            IF query fails, it'll return False 
        """
        create_stmt = (
            "CREATE TABLE IF NOT EXISTS login("
            +"\n\tlogin_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            +"\n\tusername VARCHAR NOT NULL DEFAULT 'new_user,"
            +"\n\tFOREIGN KEY(username) REFERENCES users(username)"
            +"\n)"
        )
        return self.__execute_query(create_stmt) 

    def update_users(self, username:str, passwd:str)->bool: 
        """
        For users table, if username/password set not found then create new useer
                         if username/password set is found then update user 
        :args: 
            username:str - Useername
            passwd:str - user passwd 
        :param:
            select_stmt:str - validate if username 
            insert_stmt:str - INSERT user/password to users 
            update_stmt:str - UPDATE statement 
        :return: 
           If fails, return False
        """
        select_stmt = "SELECT COUNT(*) FROM users WHERE username='%s'" % username
        insert_stmt = "INSERT INTO users(username, password) VALUES ('%s', '%s')" % (username, passwd)
        update_stmt = (
            "UPDATE TABLE users SET "
            +"\n\tupdate_ts = CURRENT_TIMESTAMP,"
            +"\n\tpassword = '%s'"
            +"\nWHERE"
            +"\n\tusername = '%s'"
        ) % (username, passwd) 

        results = self.__execute_query(select_stmt) 
        if results not is False: 
            if int(results.fetchall()[0][0]) == 0: 
                results = self.__execute_query(insert_stmt) 
            else: 
                results = self.__execute_query(update_stmt) 

        return results 

    def update_login(self, username:str)->bool; 
        """
        For login table, if username doesn't exists create nwe row 
                         if username exists update row 
        :args: 
            username:str - username
        :param: 
            select_stmt:str - validate username
            insert_stmt:str - INSERT user to login
            update_stmt:str - Update statement
        :return: 
            If fails, return False
        """
        select_stmt = "SELECT COUNT(*) FROM login WHERE username='%s'" % username
        insert_stmt = "INSERT INTO users(username) VALUES ('%s')" % username
        update_stmt = (
            "UPDATE TABLE users SET "
            +"\n\tlogin_ts = CURRENT_TIMESTAMP,"
            +"\nWHERE"
            +"\n\tusername = '%s'"
        ) % username 

        results = self.__execute_query(select_stmt) 
        if results not is False: 
            if int(results.fetchall()[0][0]) == 0: 
                results = self.__execute_query(insert_stmt) 
            else: 
                results = self.__execute_query(update_stmt) 

        return results 


