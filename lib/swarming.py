import paramiko
import re
import docker

#custom libs
from lib.containering import parse_config
from lib.containering import update_config
from lib.logger import Logger


class SwarmManagment():
	"""
	Swarm manager class
	"""

	def __init__(self):
		"""
		Constructor of swarm manager
		Args:
			available_servers(list)
			swarm_servers(list)
			user(str)
			password(str)
			master_node(str)
			token(str)
		"""
		self.ssh_client = paramiko.SSHClient()
		self.ssh_client.load_system_host_keys()
		# self.available_servers = kwargs.get('available_servers', [])
		# self.swarm_servers = kwargs.get('swarm_servers', [])
		# self.user = kwargs.get('user')
		# self.password = kwargs.get('password')
		# self.master_nodes = kwargs.get('master_nodes', [])
		# self.__master = kwargs.get('master', None)
		# self.__token = kwargs.get('token')

		self.available_servers = parse_config("orchastrator.json")["available_servers"]
		self.swarm_servers = parse_config("orchastrator.json")["swarm_servers"]
		self.user = parse_config("orchastrator.json")["user"]
		self.password = parse_config("orchastrator.json")["password"]
		self.master_nodes = parse_config("orchastrator.json")["master_nodes"]
		self.__master = parse_config("orchastrator.json")["master"]
		self.__token = parse_config("orchastrator.json")["token"]


	@staticmethod
	def get_docker_api(host_ip):
		"""
		Get docker api client
		Args:
			host_ip(str)
		"""
		return docker.DockerClient(base_url='tcp://{}:2375'.format(host_ip))



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
		logger = Logger(filename = "orchastrator", logger_name = "SwarmManagment add_server")
		if isinstance(host_ips, str):
			if host_ips not in self.available_servers:
				self.available_servers.append(host_ips)
				update_config("orchastrator.json", "available_servers", host_ips, state='add')
			else:
				# print("The host ip is already in the list")
				logger.info("The host ip is already in the list")
				logger.clear_handler()
		elif isinstance(host_ips, list):
			self.available_servers = list(set(self.available_servers + host_ips))
			update_config("orchastrator.json", "available_servers", host_ips, state='add')

		else:
			logger.error("Server should be list or string")
			logger.clear_handler()
			raise TypeError("Server should be list or string")


	def add_swarm_server(self, host_ip):
		"""
		Add server to swarm_servers
		If the server consist in the list it won't be add
		Args:
			host_ips(str)
		Returns:
			Append to self.swarm_servers the host_ip
		"""
		logger = Logger(filename = "orchastrator", logger_name = "SwarmManagment add_swarm_server")
		if isinstance(host_ip, str):
			if host_ip not in self.swarm_servers:
				self.swarm_servers.append(host_ip)
				update_config("orchastrator.json", "swarm_servers", host_ip, state='add')
			else:
				# print("The host ip is already in the list")
				logger.info("The host ip is already in the list")
				logger.clear_handler()


	def list_available_servers(self):
		"""
		List the available servers remain
		Returns:
			self.available_servers(list)
		"""
		return parse_config("orchastrator.json")["available_servers"]


	def list_swarm_servers(self):
		"""
		List the servers in the swarm
		Returns:
			self.swarm_servers(list)
		"""
		return parse_config("orchastrator.json")["swarm_servers"]


	def remove_available_server(self, host_ip):
		"""
		Remove server ip from self.available_servers
		Args:
			host_ip(str)
		"""
		self.available_servers.remove(host_ip)
		update_config("orchastrator.json", "available_servers", host_ip, state='remove')


	def remove_swarm_server(self, host_ip):
		"""
		Remove server ip from self.swarm_servers
		Args:
			host_ip(str)
		"""
		if host_ip in self.swarm_servers:
			self.swarm_servers.remove(host_ip)
			update_config("orchastrator.json", "swarm_servers", host_ip, state='remove')
		else:
			logger = Logger(filename = "orchastrator", logger_name = "SwarmManagment remove_swarm_server")		
			logger.error("Node {} can't be removed from swarm_servers (It is not in swarm_servers)".format(host_ip))
			logger.clear_handler()			

	def join_server_swarm(self, host_ip):
		"""
		Join server to the swarm
		Args:
			host_ip(str)
		"""
		#####First way
		# self.ssh_client.connect(host_ip, username=self.user, password=self.password)
		# _, stdout, _ = self.ssh_client.exec_command('docker swarm join --token {} {}:2377'. \
		# 											format(self.__token, self.__master))
		# stdout = '\n'.join(map(lambda x: x.rstrip(), stdout.readlines()))
		# if re.search(r'This node joined a swarm as a worker', stdout, re.I|re.S):
		# 	self.remove_available_server(host_ip)
		# 	self.add_swarm_server(host_ip)
		# else:
		# 	return "Node {} can't be joined to the swarm".format(host_ip)


		#####Second way

		logger = Logger(filename = "orchastrator", logger_name = "SwarmManagment join_server_swarm")		
		docker_api = self.get_docker_api(host_ip)
		response = False
		try:
			response = docker_api.swarm.join(remote_addrs= \
							[parse_config("orchastrator.json")["master"]], \
							join_token = parse_config("orchastrator.json")["token"])
		except docker.errors.APIError as e:
			logger.info("Exception handling swarm joining but config will be updated and corrected")
			logger.clear_handler()
			self.remove_available_server(host_ip)
			self.add_swarm_server(host_ip)
			
		if response == True:
			logger.info("Node {} was successfully joined to the swarm".format(host_ip))
			logger.clear_handler()
			self.remove_available_server(host_ip)
			self.add_swarm_server(host_ip)
		else:

			logger.error("Node {} can't be joined to the swarm".format(host_ip))
			logger.clear_handler()
			return "Node {} can't be joined to the swarm".format(host_ip)

		#####Second way

	def leave_server_swarm(self, host_ip):
		"""
		Leave server from the swarm
		Args:
			host_ip(str)
		"""

		#####First way
		# if host_ip in parse_config("orchastrator.json")["master_nodes"]:
		# 	print("Demoting the node from manager")
		# 	self.demote_manager(host_ip)

		# self.ssh_client.connect(host_ip, username=self.user, password=self.password)
		# _, stdout, _ = self.ssh_client.exec_command('docker swarm leave')
		# stdout = '\n'.join(map(lambda x: x.rstrip(), stdout.readlines()))
		# print("STDOUT => {}".format(stdout))
		# stdout = "Node left the swarm"
		# hostname = self.get_hostname(host_ip)
		# if re.search(r'Node left the swarm', stdout, re.I|re.S):
		# 	print("YEEEEE")
		# 	self.ssh_client.connect(self.__master, username=self.user, password=self.password)
		# 	_, leave_stdout, _ = self.ssh_client.exec_command('docker node rm -f {}'.format(hostname))
		# 	leave_stdout = '\n'.join(map(lambda x: x.rstrip(), leave_stdout.readlines()))
		# 	self.add_server(host_ip)
		# 	self.remove_swarm_server(host_ip)						
		# else:
		# 	return "Node {} can't left the swarm for some reason".format(host_ip)

		#####Second way
		logger = Logger(filename = "orchastrator", logger_name = "SwarmManagment leave_server_swarm")
		docker_api = self.get_docker_api(host_ip)
		response = docker_api.swarm.leave(force=True)
		if response:
			self.add_server(host_ip)
			self.remove_swarm_server(host_ip)		
		else:
			logger.error("Node {} can't left the swarm for some reason".format(host_ip))
			logger.clear_handler()
			return "Node {} can't left the swarm for some reason".format(host_ip)

	def add_master_node(self, host_ip):
		"""
		Add server ip to self.master_nodes
		Args:
			host_ip(str)
		"""
		self.master_nodes.append(host_ip)
		update_config("orchastrator.json", "master_nodes", host_ip, state='add')





	def remove_master_node(self, host_ip):
		"""
		Remove server ip to self.master_nodes
		Args:
			host_ip(str)
		"""
		self.master_nodes.remove(host_ip)
		update_config("orchastrator.json", "master_nodes", host_ip, state='remove')


	def promote_to_manager(self, host_ip):
		"""
		Promote the server to manager in the swarm
		Args:
			host_ip(str)
		"""
		logger = Logger(filename = "orchastrator", logger_name = "SwarmManagment promote_to_manager")
		hostname = self.get_hostname(host_ip)
		self.ssh_client.connect(self.__master, username=self.user, password=self.password)
		_, promoted_stdout, _ = self.ssh_client.exec_command('docker node promote {}'.format(hostname))
		promoted_stdout = '\n'.join(map(lambda x: x.rstrip(), promoted_stdout.readlines()))
		if re.search(r'promoted to a manager in the swarm', promoted_stdout, re.I|re.S):
			self.add_master_node(host_ip)
		else:
			logger.error("Node {} can't be promoted to manager".format(host_ip))
			logger.clear_handler()
			return "Node {} can't be promoted to manager".format(host_ip)

	def demote_manager(self, host_ip):
		"""
		Demote the server from manager in the swarm
		Args:
			host_ip(str)
		"""
		logger = Logger(filename = "orchastrator", logger_name = "SwarmManagment demote_manager")
		hostname = self.get_hostname(host_ip)
		self.ssh_client.connect(self.__master, username=self.user, password=self.password)
		_, demoted_stdout, _ = self.ssh_client.exec_command('docker node demote {}'.format(hostname))
		demoted_stdout = '\n'.join(map(lambda x: x.rstrip(), demoted_stdout.readlines()))
		if re.search(r'demoted in the swarm', demoted_stdout, re.I|re.S):
			self.remove_master_node(host_ip)
		else:
			logger.error("Node {} can't be demoted from manager".format(host_ip))
			logger.clear_handler()
			return "Node {} can't be demoted from manager".format(host_ip)

	def get_hostname(self, host_ip):
		"""
		Take the hostname of the server ip
		Args:
			host_ip(str)
		Returns:
			hostname(str)
		"""
		self.ssh_client.connect(host_ip, username=self.user, password=self.password)
		_, hostname, _ = self.ssh_client.exec_command('hostname')
		hostname = '\n'.join(map(lambda x: x.rstrip(), hostname.readlines()))

		return hostname.strip()


	def change_master(self, host_ip):
		"""
		Change the self.__master
		Args:
			host_ip(str)
		"""
		self.__master = host_ip
		update_config("orchastrator.json", "master", host_ip, state="add")



	def change_token(self, token):
		"""
		Change the self.__token
		Args:
			token(str)
		"""
		self.__token = token
		update_config("orchastrator.json", "token", token, state="add")
