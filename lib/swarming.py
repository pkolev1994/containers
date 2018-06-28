import docker
import paramiko
import re

class SwarmManagment():
	"""
	Swarm manager class
	"""

	def __init__(self, **kwargs):
		"""
		Constructor of swarm manager
		Args:
			available_servers(list)
			swarm_servers(list)
		"""
		self.ssh_client = paramiko.SSHClient()
		self.ssh_client.load_system_host_keys()
		self.available_servers = kwargs.get('available_servers', [])
		self.swarm_servers = kwargs.get('swarm_servers', [])
		self.user = kwargs.get('user')
		self.password = kwargs.get('password')
		self.__master_node = kwargs.get('master_node')
		self.__token = kwargs.get('token')

	def add_server(self, host_ips):
		"""
		Add server to available_servers
		If the server consist in the list it won't be add
		Args:
			host_ips(list or str)
		Returns:
			Append to self.available_servers the host_ips
		"""
		if isinstance(host_ips, str):
			if host_ips not in self.available_servers:
				self.available_servers.append(host_ips)
			else:
				print("The host ip is already in the list")
		elif isinstance(host_ips, list):
			self.available_servers = list(set(self.available_servers + host_ips))
		else:
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
		if isinstance(host_ip, str):
			if host_ip not in self.swarm_servers:
				self.swarm_servers.append(host_ips)
			else:
				print("The host ip is already in the list")


	def list_available_servers(self):
		"""
		List the available servers remain
		Returns:
			self.available_servers(list)
		"""
		return self.available_servers


	def list_swarm_servers(self):
		"""
		List the servers in the swarm
		Returns:
			self.swarm_servers(list)
		"""
		return self.swarm_servers


	def remove_available_server(self, host_ip):
		"""
		Remove server ip from self.available_servers
		Args:
			host_ip(str)
		"""
		self.available_servers.remove(host_ip)


	def join_server_swarm(self, host_ip):
		"""
		Join server to the swarm
		Args:
			host_ip(str)
		"""
		self.ssh_client.connect(host_ip, username=self.user, password=self.password)
		_, stdout, _ = self.ssh_client.exec_command('docker swarm join --token {} {}:2377'. \
													format(self.__token, self.__master_node))
		stdout = '\n'.join(map(lambda x: x.rstrip(), stdout.readlines()))
		if re.search(r'This node joined a swarm as a worker', stdout, re.I|re.S):
			self.remove_available_server(host_ip)
			self.swarm_servers.append(host_ip)
		else:
			return "Node {} can't be joined to the swarm".format(host_ip)

	def leave_server_swarm(self, host_ip):
		"""
		Leave server from the swarm
		Args:
			host_ip(str)
		"""
		self.ssh_client.connect(host_ip, username=self.user, password=self.password)
		_, stdout, _ = self.ssh_client.exec_command('docker swarm leave')
		stdout = '\n'.join(map(lambda x: x.rstrip(), stdout.readlines()))
		_, hostname, _ = self.ssh_client.exec_command('hostname')
		hostname = '\n'.join(map(lambda x: x.rstrip(), hostname.readlines()))
		if re.search(r'Node left the swarm', stdout, re.I|re.S):
			self.ssh_client.connect(self.__master_node, username=self.user, password=self.password)
			_, leave_stdout, _ = self.ssh_client.exec_command('docker node rm -f {}'.format(hostname))
			leave_stdout = '\n'.join(map(lambda x: x.rstrip(), leave_stdout.readlines()))
			self.available_servers.append(host_ip)
			self.swarm_servers.remove(host_ip)						
		else:
			return "Node {} can't left the swarm for some reason".format(host_ip)