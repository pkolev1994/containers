import docker
import paramiko
import re
import json
import scp
import socket

#custom libs
from lib.nodeconnection import Node


class StatsCollector():
	"""
	class StatsCollector
	"""

	def __init__(self, **kwargs):
		"""
		Constructor
		Args:
			username(str)
			password(str)
		"""
		self.__docker_client_api = docker.from_env()


	def list_nodes_ips(self):
		"""
		Lists all node ips in the swarm
		Args:
			None
		Returns:
			ip_nodes(list)
		"""
		ip_nodes = []
		for node in self.__docker_client_api.nodes.list():
			ip_nodes.append(node.attrs['Status']['Addr'])
		return ip_nodes


	def list_nodes_hostnames(self):
		"""
		Lists all node hostnames in the swarm
		Args:
			None
		Returns:
			hostname_nodes(list)
		"""
		hostname_nodes = []
		for node in self.__docker_client_api.nodes.list():
			hostname_nodes.append(node.attrs['Description']['Hostname'])
		return hostname_nodes


	@staticmethod
	def get_docker_api(host_ip):
		"""
		Get docker api client
		Args:
			host_ip(str)
		"""
		return docker.DockerClient(base_url='tcp://{}:2375'.format(host_ip))



	def collect_stats(self):
		"""
		Collects all containers stattistics of all nodes in the swarm
		Args:
			None
		Returns:
			all_hosts_containers(dict)
		"""
		oc_containers = {}
		for host in self.list_nodes_ips():
			oc_containers[host] = {}
			docker_client_api = self.get_docker_api(host)
			for container in docker_client_api.containers.list():
				stats = container.stats(decode = False, stream=False)
				container_id_search = re.search('<Container:\s*([^>]+)>', str(container))
				container_id = container_id_search.group(1)
				taken_stats = {}
				taken_stats[container.name]= {
												"container_id": container_id, 
												"stats": stats
											 }
				oc_containers[host].update(taken_stats)
		return oc_containers