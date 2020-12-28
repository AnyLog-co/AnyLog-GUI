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

def get_sub_data(conn:str, policy:str, where_condition:str, key:str)->dict:
    """
    Based on key, get sub-result from results
    :args: 
        conn:str - IP & Port 
        policy:str - policy to get from blockchain (master, operator, cluster, etc.)
        where_condition:str - where condition in blockchain 
        key:str - sub value from blockchain 
    :param: 
        output:dict- results based on key + blockchain_query 
        blockchain_query:str - blockchain query based on policy & where_condition 
        blockchain_data:list - results based on blockchain_query 
    :return: 
        results from blockchain 
    """
    output = {}

    blockchain_query="blockchain get %s" % policy
    if where_condition != '': 
        blockchain_query = blockchain_query + ' where %s' % where_condition 
    blockchain_data = query_blockchain(conn, blockchain_query)
    
    if blockchain_data != []: 
        for row in blockchain_data:
            if '.' in key: 
                prt1 = key.split('.')[0] 
                prt2 = key.split('.')[1] 
                if isinstance(row[policy][prt1], list): 
                    output[row[policy]['name']] = [] 
                    for rw in row[policy][prt1]: 
                        if rw[prt2] not in output[row[policy]['name']]:
                            output[row[policy]['name']].append(rw[prt2])  
                else:
                    output[row[policy]['name']] = row[policy][key.split('.')[0]][key.split('.')[1]]
            else: 
                output[row[policy]['name']] = row[policy][key]

    return output
