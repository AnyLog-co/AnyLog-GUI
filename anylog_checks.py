from flask import Flask, render_template
import requests
import json
import pandas

def get_access_check(url):
      payload  = {}
      headers = {
      'type': 'info',
      'details': 'get status'
      }

# need to figure out how to plug into gRequests style async calls for speed but fine for small networks
      response = requests.request("GET", url, headers=headers, data = payload)
# response is JSON this allows using json libraries
      status_output = response.json()
      print(status_output)
      return status_output

def get_process(url):
    payload  = {}
    headers = {
      'type': 'info',
      'details': 'show processes'
    }
    process_response = requests.request("GET", url, headers=headers, data = payload)
#    test_output = response.decode('utf8')
    process_output = process_response.text.replace("\r\n","<br>")
    print(process_output)
    return process_output

def get_cpu(url):
    payload  = {}
    headers = {
      'type': 'info',
      'details': 'get cpu info'
    }
    cpu_response = requests.request("GET", url, headers=headers, data = payload)
#    test_output = response.decode('utf8')
    cpu_output = cpu_response.text.replace("\r\n","<br>")
    print(cpu_output)
    return cpu_output

def get_memory(url):
    payload  = {}
    headers = {
      'type': 'info',
      'details': 'get memory info'
    }
    memory_response = requests.request("GET", url, headers=headers, data = payload)
#    test_output = response.decode('utf8')
    memory_output = memory_response.text.replace("\r\n","<br>")
    memory_output = memory_output.replace("MB"," KB")
    print(memory_output)
    return memory_output

def get_disk(url):
    payload  = {}
    headers = {
      'type': 'info',
      'details': 'get disk usage /'
    }
    disk_response = requests.request("GET", url, headers=headers, data = payload)
#    test_output = response.decode('utf8')
    disk_output = disk_response.text.replace("','","<br>")
    disk_output = disk_output.replace("', '","<br>")
    disk_output = disk_output.replace("[{'","")
    disk_output = disk_output.replace("'}]","")
    disk_output = disk_output.replace("':'",":")
    disk_output = disk_output.replace("node","AnyLog Service IP")
    print(disk_output)
    return disk_output

def get_version(url):
    payload  = {}
    headers = {
      'type': 'info',
      'details': 'get version'
    }
    version_response = requests.request("GET", url, headers=headers, data = payload)
#    test_output = response.decode('utf8')
    version_output = version_response.text.replace("\r\n","<br>")
    print(version_output)
    return version_output
