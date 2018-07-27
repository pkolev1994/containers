import docker
import json
import re
from collections import Counter


class DecisionMaker():

	def __init__(self, available_servers):
		"""
		Constructor
		Args:
			available_servers(list)
		"""
		self.available_servers = available_servers
		self.apps_by_hosts = self.take_containers_by_hosts()

	@staticmethod
	def get_docker_api(host_ip):
		"""
		Get docker api client
		Args:
			host_ip(str)
		"""
		return docker.DockerClient(base_url='tcp://{}:2375'.format(host_ip))

	@staticmethod
	def list_containers_by_host(host_ip):

		docker_api = DecisionMaker.get_docker_api(host_ip)

		print("CC => {}".format(docker_api.containers.list()))
		cont_names = []
		for container in docker_api.containers.list():
			app_name_search = re.search('(.*?)\_\d+', container.name)
			if app_name_search:
				app_name = app_name_search.group(1)
				cont_names.append(app_name)
		return cont_names


	def take_containers_by_hosts(self):

		names_by_hosts = {}
		for host in self.available_servers:
			names_by_hosts[host] = dict(Counter(self.list_containers_by_host(host)))
		return names_by_hosts


	def counting_app_by_host(self, application):
		"""
		Counting application by hosts
		Args:
			application(str)
		Returns:
			container_count(str)
		"""		
		container_count = {}
		for host in self.apps_by_hosts.keys():
			if application not in self.apps_by_hosts[host]:
				# return host
				container_count[host] = {application: 0}
			else:
				container_count[host] = {application: self.apps_by_hosts[host][application]}

		return container_count


	def making_host_decision(self, application):
		"""
		Make decision on which host to run container
		Args:
			application(str)
		Returns:
			host(str)
		"""
		app_by_hosts = self.counting_app_by_host(application)
		for host in app_by_hosts.keys():
			if app_by_hosts[host][application] == 0:
				return host
			