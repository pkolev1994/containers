import docker
import json



def parse_config(json_file):
	"""
	Parse json_file and load it to a dictionary
	Returns:
		js_data(dict)
	"""
	try:
		with open(json_file) as json_data:
			js_data = json.load(json_data)
	except IOError:
		raise("File => {} couldn't be opened for read!".format(json_file))

	return js_data



def update_config(json_file, key, value):
	"""
	Update json_file
	"""

	jsonFile = open(json_file, "r") # Open the JSON file for reading
	data = json.load(jsonFile) # Read the JSON into the buffer
	jsonFile.close() # Close the JSON file


	if key is 'available_servers' or key is 'swarm_servers':
		data[key].append(value)
	else:
		data[key] = value
	## Save our changes to JSON file
	jsonFile = open(json_file, "w+")
	jsonFile.write(json.dumps(data,  indent=4))
	jsonFile.close()



class ContainerManagement():
	"""
	Class for running and 
	stopping contrainers 
	"""

	def __init__(self, available_servers):
		"""
		Constructor
		Args:
			available_servers(list)
		"""
		self.available_servers = parse_config('available_servers.json')['available_servers']
		self.roles_config = parse_config('types_instances.json')
		

	def add_server(self, host_ips):
		"""
		Add server to available_servers
		If the server consist in the self.available_servers
		it won't be add
		Args:
			host_ips(list or str)
		Returns:
			Append to self.available_servers the host_ips
		"""
		if isinstance(host_ips, str):
			if host_ips not in self.available_servers:
				self.available_servers.append(host_ips)
				update_config("orchastrator.json", "available_servers", host_ips)
			else:
				print("The host ip is already in the list")
		elif isinstance(host_ips, list):
			self.available_servers = list(set(self.available_servers + host_ips))
			update_config("orchastrator.json", "available_servers", host_ips)
		else:
			raise TypeError("Server should be list or string")


	def remove_available_server(self, host_ip):
		"""
		Remove server ip from self.available_servers
		Args:
			host_ip(str)
		"""
		self.available_servers.remove(host_ip)


	def run_container(self, host_ip, application):
		"""
		Run container
		Args:
			host_ip(str)
		"""
		docker_api = self.get_docker_api(host_ip)
		oc_containers = self.get_container_names()
		print("Aplication {} will be runned on server => {}".format(application, host_ip))
		for role_config in self.roles_config[application].keys():
			if not role_config in oc_containers:
				print("This name is not runned as container => {} with this ip => {}".format \
					(role_config, self.roles_config[application][role_config]))

				### Two ways:: 1st => run the contaienr and then connect it
				### to the network 
				### 2nd => create the container, then connect it to the 
				### network and then start it

				# runned_container = docker_api.containers. \
				# 			run(image = "g2.pslab.opencode.com:5000/{}1:v2". \
				# 			format(application), \
				# 			hostname = role_config, name = role_config, \
				# 			privileged = True, detach=True)

				runned_container = docker_api.containers. \
							create(image = "g2.pslab.opencode.com:5000/{}1:v2". \
							format(application), \
							hostname = role_config, name = role_config, \
							privileged = True, detach=True)
				docker_api.networks.get("external").connect(runned_container, \
					ipv4_address=self.roles_config[application][role_config])
				runned_container.start()
				break


	def stop_container(self, name, host_ip):
		"""
		Stopping container
		"""
		client = self.get_docker_api(host_ip)
		container_names = self.get_container_names()
		container_names[name].stop(timeout = 30)
		print("Exiting from orchestration func because we stop a container")
		print("=== Pruned  stopped containers ===")
		client.containers.prune(filters=None)



	@staticmethod
	def get_docker_api(host_ip):
		"""
		Get docker api client
		Args:
			host_ip(str)
		"""
		return docker.DockerClient(base_url='tcp://{}:2375'.format(host_ip))

	def get_container_names(self):
		"""
		Get container names
		Args:
		"""
		container_names = {}
		for server in self.available_servers:
			docker_api = self.get_docker_api(server)
			for container in docker_api.containers.list():
				container_names[container.name] = container

		return container_names