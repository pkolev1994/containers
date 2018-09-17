import etcd
import re


class EtcdManagement():

	def __init__(self):
		"""
		EtcdManagement constructor
		"""
		self.client = client = etcd.Client(port=2379)


	def write(self, new_key, value):
		"""
		writes key value in etcd
		"""
		self.client.write(new_key, value)

	def get_etcd_config(self):
		"""
		reads recursively all key 
		values in the key stored
		Args:
			None
		Returns:
			readed_config(dict)
		"""
		readed_config = {}
		readed_config['available_servers'] = self.get_available_servers()
		readed_config['swarm_servers'] = self.get_swarm_servers()
		readed_config['network_name'] = self.get_network_name()
		readed_config['token'] = self.get_token()
		readed_config['master'] = self.get_master()
		readed_config['logging_level'] = self.get_logging_level()
		readed_config['types_instances'] = self.get_types_instances()
		readed_config['platform_status'] = self.get_platform_status()
		readed_config.update(self.get_initial_state())

		return readed_config


	def get_platform_status(self):
		"""
		reads platfor_status from etcd 
		Args:
			None
		Returns:
			platfor_status(str)
		"""
		readed_platform_status = self.client.read("/orchastrator/platform_status/", \
													recursive=True, \
													sorted=True)
		for child in readed_platform_status.children:
			platform_status = child.value
		return platform_status


	def get_available_servers(self):
		"""
		reads available_servers from etcd 
		Args:
			None
		Returns:
			available_servers(list)
		"""
		available_servers = []
		readed_available_servers = self.client.read("/orchastrator/available_servers/", \
													recursive=True, \
													sorted=True)
		for child in readed_available_servers.children:
			match = re.match(r'\/orchastrator\/available_servers\/(.*?$)', \
								child.key, \
								re.I|re.S)
			if match:
				available_servers.append(match.group(1))

		return available_servers

	def get_types_instances(self):
		"""
		reads types_instances from etcd 
		Args:
			None
		Returns:
			types_instances(dict)
		"""
		types_instances = {}
		readed_instances = self.client.read("/orchastrator/types_instances/", recursive=True, sorted=True)
		for child in readed_instances.children:
			match = re.match(r'\/orchastrator\/types_instances\/(.*?)\/(.*?$)', \
								child.key, \
								re.I|re.S)
			if match:
				app_name = match.group(1)
			container_name = match.group(2)
			if app_name not in types_instances:
				types_instances[app_name] = {}
			types_instances[app_name].update({container_name: child.value})

		return types_instances


	def get_swarm_servers(self):
		"""
		reads swarm_servers from etcd 
		Args:
			None
		Returns:
			swarm_servers(list)
		"""
		swarm_servers = []
		readed_swarm_servers = self.client.read("/orchastrator/swarm_servers/", \
													recursive=True, \
													sorted=True)
		for child in readed_swarm_servers.children:
			match = re.match(r'\/orchastrator\/swarm_servers\/(.*?$)', \
								child.key, \
								re.I|re.S)
			if match:
				swarm_servers.append(match.group(1))

		return swarm_servers			


	def get_logging_level(self):
		"""
		reads logging_level from etcd 
		Args:
			None
		Returns:
			logging_level(str)
		"""
		readed_logging_level = self.client.read("/orchastrator/logging_level/", \
													recursive=True, \
													sorted=True)
		for child in readed_logging_level.children:
			logging_level = child.value
		return logging_level


	def get_network_name(self):
		"""
		reads network_name from etcd 
		Args:
			None
		Returns:
			network_name(str)
		"""
		readed_network_name = self.client.read("/orchastrator/network_name/", \
													recursive=True, \
													sorted=True)
		for child in readed_network_name.children:
			network_name = child.value
		return network_name


	def get_token(self):
		"""
		reads token from etcd 
		Args:
			None
		Returns:
			token(str)
		"""
		readed_token = self.client.read("/orchastrator/token/", \
													recursive=True, \
													sorted=True)
		for child in readed_token.children:
			token = child.value
		return token


	def get_master(self):
		"""
		reads master from etcd 
		Args:
			None
		Returns:
			master(str)
		"""
		readed_master = self.client.read("/orchastrator/master/", \
													recursive=True, \
													sorted=True)
		for child in readed_master.children:
			master = child.value
		return master


	def get_initial_state(self):
		"""
		reads app_per_node and app_min
		Args:
			None
		Returns:
			initial_state(dict)
		"""
		initial_state = {}
		readed_keys = self.client.read("/orchastrator/", recursive=True, sorted=True)
		for child in readed_keys.children:
			match = re.match(r'\/orchastrator\/(.*?$)', \
								child.key, \
								re.I|re.S)
			if re.search('(?:per\_node|\_min)', match.group(1), re.I|re.S):
				initial_state[match.group(1)] = float(child.value)

		return initial_state

	def remove_key(self, key):
		"""
		removes key from etcd
		Args:
			None
		Returns:
			None
		"""
		self.client.delete(key)
