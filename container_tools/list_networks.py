import docker
import os
import re
import subprocess
import json
import time


docker_api = docker.from_env()
container_keys = {}
for network in docker_api.networks.list():
	command = "docker network inspect {}".format(network.name)
	output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, 
                        universal_newlines=True)
	response_json = output.stdout
	parsed_json = re.search('\[.*?({.*}).*?\]', response_json, re.I|re.S)
	cutted_info = parsed_json.group(1)
	cutted_info = json.loads(cutted_info)
	# print(cutted_info)
	if 'Containers' in cutted_info:
		if cutted_info['Containers'] is not None:
			keys = list(cutted_info['Containers'].keys())
			container_keys[network.name] = {}
			for key in keys:
				container_keys[network.name][key] = {}
				removed_port = re.search(r'(.*?)\/', \
					cutted_info['Containers'][key]['IPv4Address'], re.I|re.S)
				removed_port = removed_port.group(1)
				container_keys[network.name][key] = {'name': cutted_info['Containers'][key]['Name'], \
													'ip': removed_port}


print("###CONTAINER NETWORKS###")
names ={}
network_names = list(container_keys.keys())
for network_name in container_keys.keys():
	for network_name_2 in container_keys.keys():
		names_keys = list(names.keys())
		if "{}{}".format(network_name, network_name_2) in names or \
			"{}{}".format(network_name_2, network_name) in names:
			continue
		if network_name is network_name_2:
			continue
		else:
			for network_key in container_keys[network_name].keys():
				for network_key_2 in container_keys[network_name_2].keys():
					if network_key == network_key_2:
						internal_name = container_keys[network_name][network_key]['name']
						internal_name = "{}_ext".format(internal_name)
						container_keys[network_name_2][network_key_2]['name'] = internal_name 
			names["{}{}".format(network_name, network_name_2)] = 1

for network_name in container_keys.keys():
	print("#{}".format(network_name))
	for network_key in container_keys[network_name].keys():
		print("{}\t{}".format(container_keys[network_name][network_key]['ip'], \
							container_keys[network_name][network_key]['name']))
