from flask import Flask, render_template
import requests
import json
import pickle
import pandas
import anylog_checks

#hard code what is expected from the blockchain call
hostCheck = {"hostname":["host1","host2"], "ip":["35.155.162.56","34.212.12.184"], "port":["2049","2049"],"nodetype":["operator","operator"],"name":["debian","ubuntu"]}

# local version of the network Pickle location
networkPickle = "network.pkl"

# turn the results from Blockchain into a Dataframe to pull needed meta data
HostCheck_df = pandas.DataFrame(data=hostCheck)

# save the dataframe to Pickle
HostCheck_df.to_pickle(networkPickle)

#get the list of IP addresses to check
ips = HostCheck_df['ip']
print (ips)

app = Flask(__name__)

# this route designates the URL entrance path
@app.route('/status')
def get_status():
  result = pandas.DataFrame(columns=['Access Check','AnyLog Processes','CPU Info','Memory Info','Disk Usage','AnyLog Version'])
  
  for ip in ips:
# hard code url and REST IP address. This will need to be dynamic based on Blockchain
    url = "http://"+ ip + ":2049"

# executing get status
    status_output = anylog_checks.get_access_check(url)
# add Processes running on nodes
    process_output = anylog_checks.get_process(url)

# add CPU running on nodes
    cpu_output = anylog_checks.get_cpu(url)

# add CPU running on nodes
    memory_output = anylog_checks.get_memory(url)

# add CPU running on nodes
    disk_output = anylog_checks.get_disk(url)

# add Version running on nodes
    version_output = anylog_checks.get_version(url)

# add to the dataframe    
    result.loc[ip] = [status_output["Status"],"Process Check: <br>" + process_output, cpu_output, memory_output, disk_output, version_output]

#  pass dataframe to template for rendering
  return render_template('view.html',tables=[result.to_html(classes='overview',escape= False)],
    titles = ['AnyLog Network','AnyLog Node Status'])
if __name__ == '__main__':
    app.run(debug=True)

