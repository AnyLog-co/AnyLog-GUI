import ast
import requests 

def execute_query(conn:str, header:dict)->requests.models.Response: 
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
        r = requests.get('http://%s' % conn, headers=header)
    except: 
        r = None
        
    if r != None and r.status_code != 200: 
        r = None 

    return r 


def query_blockchain(conn:str, query:str)->list: 
    """"
    Execute given blockchain query and resturn results formated 
    :args: 
        conn:str - IP + Port connection
        query:str - quety to execute
    :param: 
       header:dict - header to execute 
       raw_results:str - raw query results 
       results:list - formated results 
    :return; 
       formated results 
    """
    header = {'type': 'info', 'details': query} 
    raw_results = execute_query(conn, header) 

    # convert results to list/dict 
    try: 
        results = ast.literal_eval(raw_results.text)
    except: 
        results = [] 

    return results 

def get_status(conn:str)->bool: 
    """
    Get status based on connection
    :args: 
        conn:str - connection IP + Port 
    :param: 
        status:bool - status of connecton 
        header:dict - query header
        raw_results:str - raw query results 
    :return: 
        status 
    """
    status = True 
    header = {'type': 'info', 'details': 'get status'} 
    raw_results = execute_query(conn, header)

    # convert results to list/dict 
    try: 
        results = ast.literal_eval(raw_results.text)
    except: 
        status = False 

    if status is not False: 
        if 'not running' in results['Status']: 
            status = False

    return status 

def get_tables(conn:str, database:str, name:str)->dict: 
    """
    Get tables based on database 
    :args:
        conn:str - connection IP + Port 
        database:str - database to query against 
    :param: 
       header:dict - header to execute 
       raw_results:str - raw query results 
       results:list - formated results 
    """
    header = {'type': 'info', 'details': 'blockchain get table where dbms = %s and name = %s' % (database, name)} 
    raw_results = execute_query(conn, header)

    # convert results to list/dict 
    try: 
        results = ast.literal_eval(raw_results.text)
    except Exception as e: 
        print(e) 
        results = {} 

    return results[0]

def query_data(conn:str, dbms:str, query:str)->dict: 
    """
    Query data (standard SELECTs) 
    :Args: 
       conn:str - IP & Port 
       dbms:str - database 
       query:str - query 
    :param: 
       header:Dict - header to execute 
       raw_results:str - raw query reults 
       results:dict - results 
    :return: 
        return results
    """
    header = {'type': 'sql', 'dbms': dbms,  'details': query}
    raw_results = execute_query(conn, header)

    # convert results to list/dict 
    try: 
        results = ast.literal_eval(raw_results.text)
    except Exception as e: 
        print(e) 
        results = {} 

    return results


def query_blockchain_complex(conn:str, policy:str, where_condition:str, keys:str)->dict: 
    """
    Based on key, get sub-result from results
    :args: 
        conn:str - IP & Port 
        policy:str - policy to get from blockchain (master, operator, cluster, etc.)
        where_condition:str - where condition in blockchain 
        keys:str - sub value from blockchain 
    :param;
        cluster_table:list - for cluster values in table 
        index:int - index within list 
        blockchain_query:str - query to execute 
    :return: 
        list of outputs in dict
    :sample-cmd: 
        query_blockchain_complex('127.0.0.1:2049', 'cluster', 'table_name=ping_sensor', 'company') 

    """
    output = [] 
    cluster_table = ['name', 'dbms', 'distribution', 'active'] 
    blockchain_query = 'blockchain get %s' % policy 

    # Convert WHERE conditions into list & format if policy of cluster type
    where_condition = where_condition.split('and') 
    for where in where_condition: 
        index = where_condition.index(where) 
        where = where.replace(' ', '') 
        base = where.split('=')[0] 
        if policy == 'cluster' and base.split('_')[0] == 'table': 
            new_base = 'table[%s]' % base.split('_')[1]
            where = where.replace(base, new_base) 
        where_condition[index] = where 
    
    if len(where_condition) > 0: 
        blockchain_query += ' where '
        for where in where_condition: 
            blockchain_query += where 
            if where is not where_condition[-1]: 
                blockchain_query += ' and '  

    # Convert key into list 
    keys=keys.replace(' ', '').split(',') 
    if len(keys) > 0 and (keys != [] and keys != ['']): 
        blockchain_query += ' bring '
        for key in keys:
            blockchain_query += '[%s][%s]' % (policy, key) 
            if key != keys[-1]: 
                blockchain_query += ' | '
            else: 
                blockchain_query += " separator = , "

    # Get results based on query 
    results = query_blockchain(conn, blockchain_query)

    # format results 
    try: 
        for result in results['Blockchain data'].split(','): 
            data = {} 
            result = result.split('|') 
            for rslt in result:
                index = result.index(rslt) 
                data[keys[index]] = rslt 
            output.append(data) 
    except: 
        pass 

    return output 
