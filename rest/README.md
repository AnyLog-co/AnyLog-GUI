The following scripts support connecting and formating data recieved via REST requests. 

```
/home/anylog/AnyLog-GUI
├── README.md
└── rest
    ├── general_info.py
    ├── query_db.py
    ├── README.md
    └── rest_requests.py
```

# File Descriptions
   * rest_requests.py -- Actual REST (GET) calls to an AnyLog node. 

   * query_db.py -- The main and formating script for querying for data on the operator(s). 
```
# Help
anylog@anylog-develop:~/AnyLog-GUI/rest$ python3 ~/AnyLog-GUI/rest/query_db.py --help
usage: query_db.py [-h] [-s SERVERS] conn logical_db query
positional arguments:
  conn                   REST connection IP:Port
  logical_db            logical database to query from
  query                  query to execute
optional arguments:
  -h, --help             show this help message and exit
  -s, --servers SERVERS  specific servers to query against

# Examples
anylog@anylog-develop:~/AnyLog-GUI/rest$ python3 ~/AnyLog-GUI/rest/query_db.py 23.239.12.151:2049 lsl_demo "SELECT device_name, COUNT(*) FROM ping_sensor group by device_name;" 
         {'device_name': 'VM Xompass VPN 2', 'count(*)': '18766'}
         {'device_name': 'Ubiquiti 10G-Switch', 'count(*)': '36797'}
         {'device_name': 'ADVA ALM OTDR', 'count(*)': '45074'}
         {'device_name': 'VM Lit SL NMS', 'count(*)': '19012'}
         {'device_name': 'Basic Network Element', 'count(*)': '36'}
         {'device_name': 'Catalyst 3500XL', 'count(*)': '345142'}
         {'device_name': 'REMOTE-SERVER-ANDRES', 'count(*)': '95409'}
         {'device_name': 'Ubiquiti 10G Switch', 'count(*)': '55261'}
         {'device_name': 'APC PDU', 'count(*)': '34'}
         {'device_name': 'F.O Monitoring Server', 'count(*)': '11258'}
         {'device_name': 'ADVA FSP3000R7', 'count(*)': '10902'}
         {'device_name': 'Ubiquiti OLT', 'count(*)': '14849'}
         {'device_name': 'GOOGLE_PING', 'count(*)': '14971'}

anylog@anylog-develop:~/AnyLog-GUI/rest$ python3 ~/AnyLog-GUI/rest/query_db.py 23.239.12.151:2049 lsl_demo "SELECT device_name, COUNT(*) FROM ping_sensor group by device_name;" -s 172.105.13.202:2048
         {'device_name': 'VM Xompass VPN 2', 'count(*)': '7253'}
         {'device_name': 'Ubiquiti 10G-Switch', 'count(*)': '14991'}
         {'device_name': 'ADVA ALM OTDR', 'count(*)': '22235'}
         {'device_name': 'VM Lit SL NMS', 'count(*)': '8303'}
         {'device_name': 'Catalyst 3500XL', 'count(*)': '161907'}
         {'device_name': 'REMOTE-SERVER-ANDRES', 'count(*)': '42644'}
         {'device_name': 'Ubiquiti 10G Switch', 'count(*)': '22023'}
         {'device_name': 'APC PDU', 'count(*)': '17'}
         {'device_name': 'F.O Monitoring Server', 'count(*)': '4707'}
         {'device_name': 'ADVA FSP3000R7', 'count(*)': '4010'}
         {'device_name': 'Ubiquiti OLT', 'count(*)': '7157'}
         {'device_name': 'GOOGLE_PING', 'count(*)': '7212'}
```

   * genera_info.py -- The main and formating script for querying the database, or receving node information 
```
# Help 
anylog@anylog-develop:~/AnyLog-GUI/rest$ python3 ~/AnyLog-GUI/rest/general_info.py --help 
usage: general_info.py [-h] [-a [ALL]] [-b [BLOCKCHAIN]] [-o [OPERATOR]]
                       [-p [PROCESS]] [-s [STATUS]] [-t [TABLE]]
                       conn
positional arguments:
  conn                  REST connection IP:Port
optional arguments:
  -h, --help                       show this help message and exit
  -a, --all [ALL]                  Get all possible info from node
  -b, --blockchain [BLOCKCHAIN]    Get general info about all nodes
  -o, --operator [OPERATOR]        Get info about operators
  -p, --process [PROCESS]          Get process info
  -s, --status [STATUS]            Get status of specific node
  -t, --table [TABLE]              Get info about tables
  -u, --utils      [UTILS]        Get utilty information (cpu, memory, disk) 

# Example 
anylog@anylog-develop:~/AnyLog-GUI/rest$ python3 ~/AnyLog-GUI/rest/general_info.py 23.239.12.151:2049 -a
master
        45.33.41.185 | TCP: 2048 | REST: 2049
query
        23.239.12.151 | TCP: 2048 | REST: 2049
        172.104.61.193 | TCP: 2048 | REST: 2049
operator
        172.105.13.202 | TCP: 2048 | REST: 2049
        139.162.164.95 | TCP: 2048 | REST: 2049
        139.162.126.241 | TCP: 2048 | REST: 2049
        185.162.127.230 | TCP: 2048 | REST: 2049
publisher
        172.104.180.110 | TCP: 2048 | REST: 2049


Operators Info
        172.105.13.202:2048
                lsl_demo
                        ping_sensor
                        percentagecpu_sensor
                        systemuptime_sensor


        139.162.164.95:2048
                lsl_demo
                        ping_sensor
                        percentagecpu_sensor
                        systemuptime_sensor


        139.162.126.241:2048
                lsl_demo
                        ping_sensor
                        percentagecpu_sensor


        185.162.127.230:2048
                sample_data
                        machine_data
                        sin_data
                        cos_data


Processes Status
        TCP: Running
        REST: Running
        Operator: Not declared
        Publisher: Not declared
        Syncronizer: Running
        Schedular: Not declared
        HA: Not declared


Status: query@23.239.12.151:2048 running


sample_data.cos_data
--------------------
CREATE TABLE IF NOT EXISTS cos_data(
        row_id SERIAL PRIMARY KEY,
        insert_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
        timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
        value FLOAT );
CREATE INDEX cos_data_timestamp_index ON cos_data(timestamp);
CREATE INDEX cos_data_insert_timestamp_index ON cos_data(insert_timestamp);

sample_data.machine_data
------------------------
CREATE TABLE IF NOT EXISTS machine_data(
        row_id SERIAL PRIMARY KEY,
        insert_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
        boot_time FLOAT,
        cpu_percentge DECIMAL,
        disk_useage DECIMAL,
        hostname VARCHAR,
        local_ip CIDR,
        remote_ip CIDR,
        swap_memory DECIMAL,
        timestamp TIMESTAMP NOT NULL DEFAULT NOW() );
CREATE INDEX machine_data_timestamp_index ON machine_data(timestamp);
CREATE INDEX machine_data_insert_timestamp_index ON machine_data(insert_timestamp);

lsl_demo.percentagecpu_sensor
-----------------------------
CREATE TABLE IF NOT EXISTS percentagecpu_sensor(
        row_id SERIAL PRIMARY KEY,
        insert_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
        device_name VARCHAR,
        parentelement UUID,
        timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
        value FLOAT,
        webid VARCHAR );
CREATE INDEX percentagecpu_sensor_parentelement_index ON percentagecpu_sensor(parentelement);
CREATE INDEX percentagecpu_sensor_timestamp_index ON percentagecpu_sensor(timestamp);
CREATE INDEX percentagecpu_sensor_insert_timestamp_index ON percentagecpu_sensor(insert_timestamp);

lsl_demo.ping_sensor
--------------------
CREATE TABLE IF NOT EXISTS ping_sensor(
        row_id SERIAL PRIMARY KEY,
        insert_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
        device_name VARCHAR,
        parentelement UUID,
        timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
        value FLOAT,
        webid VARCHAR );
CREATE INDEX ping_sensor_parentelement_index ON ping_sensor(parentelement);
CREATE INDEX ping_sensor_timestamp_index ON ping_sensor(timestamp);
CREATE INDEX ping_sensor_insert_timestamp_index ON ping_sensor(insert_timestamp);

sample_data.sin_data
--------------------
CREATE TABLE IF NOT EXISTS sin_data(
        row_id SERIAL PRIMARY KEY,
        insert_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
        timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
        value FLOAT );
CREATE INDEX sin_data_timestamp_index ON sin_data(timestamp);
CREATE INDEX sin_data_insert_timestamp_index ON sin_data(insert_timestamp);

lsl_demo.systemuptime_sensor
----------------------------
CREATE TABLE IF NOT EXISTS systemuptime_sensor(
        row_id SERIAL PRIMARY KEY,
        insert_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
        device_name VARCHAR,
        parentelement UUID,
        timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
        value VARCHAR,
        webid VARCHAR );
CREATE INDEX systemuptime_sensor_parentelement_index ON systemuptime_sensor(parentelement);
CREATE INDEX systemuptime_sensor_timestamp_index ON systemuptime_sensor(timestamp);
CREATE INDEX systemuptime_sensor_insert_timestamp_index ON systemuptime_sensor(insert_timestamp);

CPU:
        CPU Physical cores: 1 | CPU Logical cores: 1
Disk:
        Disk Total: 15,783.11MB | Disk Used: 6,101.17MB | Disk Free: 8,860.02MB
Memory:
        Memory Total: 2,040,972MB | Memory Available: 1,573,060MB | Memory Used: 296,720MB | Memory Free: 264,964MB
```

