import docker
import json
import re
from collections import Counter

#custom lib
from lib.containering import parse_config
from lib.swarming import SwarmManagment

class DecisionMaker():

	def __init__(self):
		"""
		Constructor
		Args:
			available_servers(list)
		"""

		self.swarm_manager = SwarmManagment()
		self.swarm_servers = parse_config('orchastrator.json')['swarm_servers']
		self.available_servers = parse_config('orchastrator.json')['available_servers']
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
		cont_names = []
		for container in docker_api.containers.list():
			app_name_search = re.search('(.*?)\_\d+', container.name)
			if app_name_search:
				app_name = app_name_search.group(1)
				cont_names.append(app_name)
		return cont_names


	def take_containers_by_hosts(self):

		names_by_hosts = {}
		for host in self.swarm_servers:
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


	def making_host_decision(self, application, decision):
		"""
		Make decision on which host to run container
		Args:
			application(str)
			decision(str)
		Returns:
			host(str)
		"""
		app_per_node = "{}_per_node".format(application)
		app_by_hosts = self.counting_app_by_host(application)
		host_number = len(app_by_hosts.keys())
		if decision is 'up':
			application_number = 0
			for host in app_by_hosts.keys():
				if app_by_hosts[host][application] == 0:
					return host
				else:
					application_number += app_by_hosts[host][application]
			average_app_number = round(application_number/host_number)
			print("Average => {}".format(average_app_number))
			print("Appp => {}".format(parse_config('orchastrator.json')[app_per_node]))
			# print("Servers => ")
			###logic for adding node to the swarm
			if average_app_number == parse_config('orchastrator.json')[app_per_node]:
				if self.available_servers:
					self.swarm_manager.join_server_swarm(host_ip = self.available_servers[0])
					return self.available_servers[0]
				else:
					print("There are not any available servers should  \
							look at host stat to run on the lowest  \
							loaded host  a container")
			###logic for adding node to the swarm			
			for host in app_by_hosts.keys():
				if app_by_hosts[host][application] < average_app_number and \
					app_by_hosts[host][application] < parse_config('orchastrator.json')[app_per_node]:
					return host
			for host in app_by_hosts.keys():
				return host
		elif decision is 'down':
			application_number = 0
			for host in app_by_hosts.keys():
					application_number += app_by_hosts[host][application]
			average_app_number = round(application_number/host_number)			
			for host in app_by_hosts.keys():
				if app_by_hosts[host][application] > average_app_number and \
					app_by_hosts[host][application] < parse_config('orchastrator.json')[app_per_node]:
					return host
			for host in app_by_hosts.keys():
				return host